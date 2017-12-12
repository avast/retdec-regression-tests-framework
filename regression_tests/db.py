"""
    Database support.
"""

# MySQL database creation:
#
#   CREATE DATABASE regression_tests;
#   CREATE USER 'regression_tests' IDENTIFIED BY 'XXX';
#   GRANT ALL PRIVILEGES ON regression_tests.* TO 'regression_tests';
#   FLUSH PRIVILEGES;
#   USE regression_tests;
#

from datetime import datetime

from regression_tests.commit_results import CommitResults
from regression_tests.commit_results import CommitsResults
from regression_tests.git import Commit
from regression_tests.io import print_warning
from regression_tests.retdec_builder import BuildInfo
from regression_tests.retdec_builder import NoBuildInfo
from regression_tests.test_results import TestResults
from regression_tests.test_results import TestsResults

try:
    import sqlalchemy
except ImportError:
    # The sqlalchemy module is not available, so fall back to no database
    # support. This is done by using a mock instead of the real module.
    from unittest import mock
    sqlalchemy = mock.MagicMock()

    print_warning("module 'sqlalchemy' (https://pypi.python.org/pypi/sqlalchemy) "
                  "not found, running without database support")


class DBError(Exception):
    """A base class of all exceptions :class:`.DB` raises."""


class InvalidCommitError(DBError):
    """An exception raised when an invalid commit is encountered."""


class InvalidBuildError(DBError):
    """An exception raised when an invalid commit is encountered."""


class DB:
    """An access to a database for storing regression tests and their
    results.

    Instances of this class are not thread-safe, so if you want to access a
    database from multiple threads/processes, please use different instances or
    manual locking (like using ``multiprocessing.Lock``).
    """

    def __init__(self, conn_url):
        """
        :param str conn_url: Connection URL.
        """
        # pool_recycle represents the number of seconds after which a
        # connection is automatically recycled. This is required for MySQL,
        # which removes connections after 8 hours idle by default. The value
        # 3600 represents 1 hour.
        self._engine = sqlalchemy.create_engine(conn_url, pool_recycle=3600)
        self._create_tables()

    def clear(self):
        """Clears the database."""
        # Based on http://stackoverflow.com/a/5003705/2580955.
        for table in reversed(self._metadata.sorted_tables):
            self._execute(table.delete())

    def get_date_of_last_update(self):
        """Returns a date of the last update.

        When the database is empt, it returns the minimal possible date.
        """
        # We consider the last end_date in results as the date of the last
        # update.
        select = self._test_results_table.select().with_only_columns(
            [self._test_results_table.c.end_date]
        ).order_by(
            self._test_results_table.c.end_date.desc()
        ).limit(
            1
        )
        results = self._execute(select)
        row = results.fetchone()
        return row.end_date if row is not None else datetime.min

    def get_unprocessed_commits(self):
        """Returns a list of commits that are in the database but has to yet
        been processed.
        """
        # We return a list of commits for which there are no build information.
        select = self._commits_table.select().where(
            ~self._commits_table.c.id.in_(
                self._builds_table.select().with_only_columns(
                    [self._builds_table.c.commit_id]
                )
            )
        ).order_by(
            self._commits_table.c.id.asc()
        )
        results = self._execute(select)
        return [self._commit_from_row(row) for row in results]

    def get_topmost_commit(self):
        """Returns the topmost commit that is stored in the database."""
        select = self._commits_table.select().order_by(
            self._commits_table.c.id.desc()
        ).limit(
            1
        )
        results = self._execute(select)
        row = results.fetchone()
        return self._commit_from_row(row) if row is not None else None

    def topmost_commit_has_succeeded(self):
        """Checks if the topmost commit has succeeded (build, tests).

        If there is no topmost commit, it returns ``False``.
        """
        commit = self.get_topmost_commit()
        if commit is None:
            return False

        commit_results = self.get_results_for_commit(commit)
        return (commit_results.build_has_succeeded() and
                not commit_results.has_failed_tests())

    def get_commit_for_non_critical_tests(self, max_depth=8):
        """Returns a commit for which non-critical tests should run.

        Only the first `max_depth` commits are checked.
        """
        commits_results = self.get_results_for_recent_commits(max_depth)
        for commit_results in reversed(commits_results):
            # We stop searching after we find either a commit which passed all
            # the non-critical tests, or a commit for which non-critical tests
            # should be run.
            if commit_results.build_has_failed():
                # There is no point in running non-critical tests for a commit
                # whose build has failed.
                continue
            elif commit_results.has_results_for_non_critical_tests():
                if not commit_results.has_failed_tests():
                    return None
            else:
                return commit_results.commit
        return None

    def initialize_commit_records(self, commit, remove_build_infos=True,
                                  remove_test_results=True, remove_emails=True):
        """Initializes records for the given commit.

        It inserts the commit (unless it is already present in the database)
        and clears all the builds and results associated to it (unless
        requested not to do so).
        """
        self.insert_commit(commit)
        if remove_build_infos:
            self._remove_build_infos_for_commit(commit)
        if remove_test_results:
            self._remove_test_results_for_commit(commit)
        if remove_emails:
            self._remove_emails_for_commit(commit)

    def insert_commit(self, commit):
        """Inserts the given commit into the database.

        :param Commit commit: Commit to be inserted.

        If the commit is already present in the database, this function does
        nothing.
        """
        if self._commit_exists(commit):
            return

        insert = self._commits_table.insert(dict(
            hash=str(commit.hash),
            date=commit.date,
            author=str(commit.author),
            email=str(commit.email),
            subject=str(commit.subject)
        ))
        self._execute(insert)

    def insert_commits(self, commits):
        """Inserts the given sequence of commits into the database.

        See the description of :func:`insert_commit()` for more information.
        """
        for commit in commits:
            self.insert_commit(commit)

    def get_commits_count(self):
        """Returns the number of commits in the database."""
        select = sqlalchemy.select(
            [sqlalchemy.func.count()]
        ).select_from(self._commits_table)
        return self._execute(select).fetchone()[0]

    def insert_build_started_info(self, commit, start_date):
        """Inserts a record that a build of RetDec in the given commit has
        started.

        :param Commit commit: Commit in which RetDec is being built.
        :param datetime start_date: Start date of the build.

        :returns: ID of the inserted record (`int`).

        :raises InvalidCommitError: If there is no such commit in the database.
        """
        self._verify_commit_exists(commit)

        insert = self._builds_table.insert(dict(
            commit_id=self._id_of(commit),
            start_date=start_date
        ))
        result = self._execute(insert)
        return result.lastrowid

    def insert_build_ended_info(self, build_id, build_info):
        """Inserts a record that a build of RetDec in the given commit has
        ended.

        :param int build_id: ID returned by
                             :func:`insert_build_started_info()`.
        :param BuildInfo build_info: Information about the build.

        :raises InvalidBuildError: If there is no such build in the database.
        """
        self._verify_build_exists(build_id)

        update = self._builds_table.update().values(
            start_date=build_info.start_date,
            end_date=build_info.end_date,
            succeeded=build_info.succeeded,
            log=build_info.log
        ).where(
            self._builds_table.c.id == build_id
        )
        self._execute(update)

    def insert_test_results(self, test_results, commit):
        """Inserts the given test results into the database.

        :param TestResults test_results: Test results to be inserted.
        :param Commit commit: Commit to which the results correspond.

        :raises InvalidCommitError: If there is no such commit in the database.
        """
        self._verify_commit_exists(commit)

        insert = self._test_results_table.insert(dict(
            commit_id=self._id_of(commit),
            module_name=str(test_results.module_name),
            case_name=str(test_results.case_name),
            start_date=test_results.start_date,
            end_date=test_results.end_date,
            run_tests=test_results.run_tests,
            failed_tests=test_results.failed_tests,
            output=str(test_results.output),
            critical=test_results.critical
        ))
        self._execute(insert)

    def insert_email_for_commit(self, email, commit):
        """Inserts the given email for the given commit into the database.

        :param Email email: Email for the commit.
        :param Commit commit: Commit to which the email corresponds.

        :raises InvalidCommitError: If there is no such commit in the database.

        If there is already an email attached to the given commit, this
        function does nothing.
        """
        self._verify_commit_exists(commit)

        if self.email_sent_for_commit(commit):
            return

        insert = self._emails_table.insert(dict(
            commit_id=self._id_of(commit),
            subject=str(email.subject),
            from_addr=str(email.from_addr),
            to_addr=str(email.to_addr),
            reply_to_addr=str(email.reply_to_addr),
            cc_addr=str(email.cc_addr),
            body=str(email.body),
            sent_date=datetime.now()
        ))
        self._execute(insert)

    def email_sent_for_commit(self, commit):
        """Checks if an email for the given commit has already been sent.

        :param Commit commit: Commit to which the email should correspond.
        """
        select = self._emails_table.select().with_only_columns(
            [self._emails_table.c.id]
        ).where(
            self._emails_table.c.commit_id == self._id_of(commit)
        )
        return self._execute(select).fetchone() is not None

    def has_test_run_for_commit(self, module_name, case_name, commit):
        """Checks if the given test case has run for the given commit.

        :param str module_name: Name of the test module.
        :param str/TestCaseName case_name: Name of the test case.
        :param Commit commit: Commit.

        :returns: ``True`` if the given test case has run for the given commit,
                  ``False`` otherwise.

        :raises InvalidCommitError: If there is no such commit in the database.
        """
        self._verify_commit_exists(commit)

        select = sqlalchemy.select(
            [sqlalchemy.func.count()]
        ).where(
            sqlalchemy.and_(
                self._test_results_table.c.commit_id == self._id_of(commit),
                self._test_results_table.c.module_name == str(module_name),
                self._test_results_table.c.case_name == str(case_name)
            )
        ).select_from(self._test_results_table)
        return self._execute(select).fetchone()[0] > 0

    def get_results_for_commit(self, commit):
        """Returns results (:class:`.CommitResults`) for the given commit
        (:class:`.Commit`).

        :raises InvalidCommitError: If there is no such commit in the database.
        """
        self._verify_commit_exists(commit)

        tests_results = self._get_tests_results_for_commit(commit)
        build_info = self._get_build_info_for_commit(commit)
        return CommitResults(commit, tests_results, build_info)

    def get_results_for_recent_commits(self, count=8):
        """Returns a list of results (:class:`.CommitResults`) for the last
        `count` commits.
        """
        return CommitsResults(
            self.get_results_for_commit(commit) for commit in self._get_recent_commits(count)
        )

    def _execute(self, query):
        """Executes the given query."""
        return self._engine.execute(query)

    def _create_tables(self):
        """Creates all the tables in the database."""
        # Aliases to make the code more succinct. Do not use imports because
        # the sqlalchemy module may not be available (see the handling at top
        # of this file).
        ForeignKey = sqlalchemy.ForeignKey
        schema = sqlalchemy.schema
        types = sqlalchemy.types

        self._metadata = schema.MetaData()

        # We have to explicitly specify the length of text columns. Otherwise,
        # in MySQL databases, it uses TEXT, which can contain only 65,535
        # bytes. The following length corresponds to MEDIUMTEXT, which can
        # contain 16,777,215 bytes.
        TEXT_LENGTH = 2 ** 24 - 1

        # Commits.
        self._commits_table = schema.Table(
            'commits',
            self._metadata,
            schema.Column('id', types.Integer(), primary_key=True),
            schema.Column('hash', types.String(255), unique=True, nullable=False),
            schema.Column('date', types.DateTime(), nullable=False),
            schema.Column('author', types.String(255), nullable=False),
            schema.Column('email', types.String(255), nullable=False),
            schema.Column('subject', types.String(255), nullable=False)
        )

        # Builds.
        self._builds_table = schema.Table(
            'builds',
            self._metadata,
            schema.Column('id', types.Integer(), primary_key=True),
            schema.Column('commit_id', types.Integer(), ForeignKey('commits.id'),
                          nullable=False),
            schema.Column('start_date', types.DateTime(), nullable=False),
            schema.Column('end_date', types.DateTime()),
            schema.Column('succeeded', types.Boolean()),
            schema.Column('log', types.Text(length=TEXT_LENGTH))
        )

        # Test results.
        self._test_results_table = schema.Table(
            'results',
            self._metadata,
            schema.Column('id', types.Integer(), primary_key=True),
            schema.Column('build_id', types.Integer(), ForeignKey('builds.id')),
            schema.Column('commit_id', types.Integer(), ForeignKey('commits.id'),
                          nullable=False),
            schema.Column('module_name', types.String(255), nullable=False),
            schema.Column('case_name', types.String(255), nullable=False),
            schema.Column('start_date', types.DateTime(), nullable=False),
            schema.Column('end_date', types.DateTime()),
            schema.Column('run_tests', types.Integer()),
            schema.Column('failed_tests', types.Integer()),
            schema.Column('output', types.Text(length=TEXT_LENGTH)),
            schema.Column('critical', types.Boolean()),
        )

        # Emails.
        self._emails_table = schema.Table(
            'emails',
            self._metadata,
            schema.Column('id', types.Integer(), primary_key=True),
            schema.Column('commit_id', types.Integer(), ForeignKey('commits.id'),
                          nullable=False, unique=True),
            schema.Column('subject', types.String(255), nullable=False),
            schema.Column('from_addr', types.String(255), nullable=False),
            schema.Column('to_addr', types.String(255), nullable=False),
            schema.Column('reply_to_addr', types.String(255), nullable=False),
            schema.Column('cc_addr', types.String(255), nullable=False),
            schema.Column('body', types.Text(length=TEXT_LENGTH), nullable=False),
            schema.Column('sent_date', types.DateTime(), nullable=False)
        )

        self._metadata.bind = self._engine
        self._metadata.create_all(checkfirst=True)

    def _verify_commit_exists(self, commit):
        """Verifies that the given commit is present in the database."""
        if self._id_of(commit) is None:
            raise InvalidCommitError(
                'commit {} was not found in the database'.format(commit.short_hash())
            )

    def _verify_build_exists(self, build_id):
        """Verifies that the given build is present in the database."""
        select = self._builds_table.select().with_only_columns(
            [self._builds_table.c.id]
        ).where(
            self._builds_table.c.id == build_id
        )
        if self._execute(select).fetchone() is None:
            raise InvalidBuildError(
                'build with ID {} was not found in the database'.format(build_id)
            )

    def _get_tests_results_for_commit(self, commit):
        """Returns tests results for the given commit."""
        select = self._test_results_table.select().where(
            self._test_results_table.c.commit_id == self._id_of(commit)
        )
        results = self._execute(select)
        return TestsResults([
            TestResults(
                r.module_name,
                r.case_name,
                r.start_date,
                r.end_date,
                r.run_tests,
                r.failed_tests,
                r.output,
                r.critical
            ) for r in results
        ])

    def _get_build_info_for_commit(self, commit):
        """Returns the last build info for the given commit."""
        select = self._builds_table.select().where(
            self._builds_table.c.commit_id == self._id_of(commit)
        ).order_by(
            self._builds_table.c.start_date.desc()
        ).limit(
            1
        )
        result = self._execute(select).fetchone()
        if result is not None:
            return BuildInfo(
                start_date=result.start_date,
                end_date=result.end_date,
                succeeded=result.succeeded,
                log=result.log
            )
        return NoBuildInfo()

    def _get_recent_commits(self, count):
        """Returns a list of commits (:class:`.Commit`) for the last `count`
        commits.
        """
        select = self._commits_table.select().order_by(
            self._commits_table.c.id.desc()
        ).limit(
            count
        )
        results = self._execute(select)
        recent_commits = [
            self._commit_from_row(row) for row in results
        ]
        # We need to reverse the commits so that the "oldest" is the first one.
        recent_commits.reverse()
        return recent_commits

    def _remove_build_infos_for_commit(self, commit):
        """Removes all build infos for the given commit."""
        self._remove_records_for_commit(self._builds_table, commit)

    def _remove_test_results_for_commit(self, commit):
        """Removes all test results for the given commit."""
        self._remove_records_for_commit(self._test_results_table, commit)

    def _remove_emails_for_commit(self, commit):
        """Removes all emails for the given commit."""
        self._remove_records_for_commit(self._emails_table, commit)

    def _remove_records_for_commit(self, table, commit):
        """Removes rows in `table` whose ``commit_id`` column corresponds to
        the ID of the given commit.
        """
        delete = table.delete().where(
            table.c.commit_id == self._id_of(commit)
        )
        self._execute(delete)

    def _commit_from_row(self, row):
        """Creates a commit from the data in the given row."""
        return Commit(
            row.hash,
            row.author,
            row.email,
            row.date,
            row.subject
        )

    def _commit_exists(self, commit):
        """Checks if the given commit exists in the database."""
        return self._id_of(commit) is not None

    def _id_of(self, entity):
        """Returns an ID of the given entity.

        Supported entities are:
          * commits

        If the entity cannot be found, it returns ``None``.
        """
        if isinstance(entity, Commit):
            # Commit's ID.
            select = self._commits_table.select().with_only_columns(
                [self._commits_table.c.id]
            ).where(
                self._commits_table.c.hash == entity.hash
            )
            results = self._execute(select)
            result = results.fetchone()
            return result.id if result is not None else None
