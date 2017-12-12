"""
    Tests for the :mod:`regression_tests.repository` module.
"""

# The tests are based on
# https://github.com/s3rvac/git-branch-viewer/blob/master/tests/git_tests.py

# Cannot use `from datetime import datetime` because of eval() in `repr` tests.
import datetime
import os
import random
import unittest
from unittest import mock

from regression_tests.git import Commit
from regression_tests.git import GitError
from regression_tests.git import Repository
from regression_tests.git import add_username
from regression_tests.git import contains_username
from tests.filesystem.directory_tests import ROOT_DIR


def get_curr_date():
    """Returns the current date."""
    # Do not include milliseconds into the date because git uses just seconds.
    curr_date_ts = int(datetime.datetime.now().timestamp())
    return datetime.datetime.fromtimestamp(curr_date_ts)


def get_rand_hash(characters=Commit.VALID_HASH_CHARACTERS):
    """Returns a new, random hash from the given characters"""
    return ''.join(random.choice(
        list(characters)) for _ in range(Commit.VALID_HASH_LENGTH))


def create_commit(hash=None, author=None, email=None, date=None, subject=None):
    """Returns a new commit, possibly based on the given data (if not None)."""
    hash = hash if hash is not None else get_rand_hash()
    author = author if author is not None else 'Petr Zemek'
    email = email if email is not None else 'petr.zemek@avast.com'
    date = date if date is not None else get_curr_date()
    subject = subject if subject is not None else 'Commit message'
    return Commit(hash, author, email, date, subject)


class CommitClassTests(unittest.TestCase):
    """Tests for the `Commit` class itself."""

    def test_valid_hash_length_has_proper_value(self):
        self.assertEqual(Commit.VALID_HASH_LENGTH, 40)

    def test_valid_hash_characters_has_proper_value(self):
        self.assertEqual(Commit.VALID_HASH_CHARACTERS, set('abcdef0123456789'))


class CommitCreateAndAccessTests(unittest.TestCase):
    """Tests for `Commit.__init__()` and accessors."""

    def test_data_passed_into_constructor_are_accessible_after_creation(self):
        hash = get_rand_hash()
        author = 'Petr Zemek'
        email = 'petr.zemek@avast.com'
        date = get_curr_date()
        subject = 'Commit message'
        commit = Commit(hash, author, email, date, subject)
        self.assertEqual(commit.hash, hash)
        self.assertEqual(commit.author, author)
        self.assertEqual(commit.email, email)
        self.assertEqual(commit.date, date)
        self.assertEqual(commit.subject, subject)

    def test_data_cannot_be_changed_after_creation(self):
        commit = create_commit()
        with self.assertRaises(AttributeError):
            commit.hash = get_rand_hash()
        with self.assertRaises(AttributeError):
            commit.author = 'Other Author'
        with self.assertRaises(AttributeError):
            commit.email = 'Other email'
        with self.assertRaises(AttributeError):
            commit.date = get_curr_date()
        with self.assertRaises(AttributeError):
            commit.subject = 'Other commit message'

    def test_hash_is_properly_normalized(self):
        commit = create_commit(
            hash='207891DB5BDDBFB0C7210ACA8C76AC6A9C5F9859'
        )
        self.assertEqual(
            commit.hash,
            '207891db5bddbfb0c7210aca8c76ac6a9c5f9859'
        )

    def test_value_error_is_raised_when_hash_is_empty(self):
        with self.assertRaises(ValueError):
            create_commit(hash='')

    def test_value_error_is_raised_when_hash_too_short(self):
        with self.assertRaises(ValueError):
            create_commit(hash='abcdef')

    def test_value_error_is_raised_when_hash_too_long(self):
        with self.assertRaises(ValueError):
            create_commit(hash='a' * (Commit.VALID_HASH_LENGTH + 1))

    def test_value_error_is_raised_when_hash_has_invalid_characters(self):
        with self.assertRaises(ValueError):
            create_commit(hash=(Commit.VALID_HASH_LENGTH - 1) * 'a' + 'g')


class CommitShortHashTests(unittest.TestCase):
    """Tests for `Commit.short_hash()`."""

    def test_short_hash_returns_correct_result(self):
        commit = create_commit(hash='207891db5bddbfb0c7210aca8c76ac6a9c5f9859')
        self.assertEqual(commit.short_hash(10), '207891db5b')


class CommitShortSubjectTests(unittest.TestCase):
    """Tests for `Commit.short_subject()`."""

    def test_short_subject_returns_subject_when_subject_is_shorter(self):
        commit = create_commit(subject='test')
        self.assertEqual(commit.short_subject(5), commit.subject)

    def test_short_subject_returns_subject_when_subject_has_same_length(self):
        commit = create_commit(subject='test')
        self.assertEqual(commit.short_subject(4), commit.subject)

    def test_short_subject_returns_shorter_subject_when_subject_is_longer(self):
        commit = create_commit(subject='test')
        self.assertEqual(commit.short_subject(3), 'tes...')


class CommitAgeTests(unittest.TestCase):
    """Tests for `Commit.age()`."""

    @mock.patch('datetime.datetime')
    def test_age_returns_correct_result(self, datetime_mock):
        commit = create_commit()
        today = get_curr_date()
        datetime_mock.today.return_value = today
        expected_age = today - commit.date
        self.assertEqual(commit.age, expected_age)


class CommitComparisonTests(unittest.TestCase):
    """Tests for commit comparison."""

    def test_two_identical_commits_are_equal(self):
        commit = Commit(
            get_rand_hash(),
            'PZ',
            'zemek@petrzemek.net',
            get_curr_date(),
            'Commit message'
        )
        self.assertEqual(commit, commit)

    def test_two_commits_with_equal_data_are_equal(self):
        hash = get_rand_hash()
        author = 'PZ'
        email = 'zemek@petrzemek.net'
        date = get_curr_date()
        subject = 'Commit message'
        commit1 = Commit(hash, author, email, date, subject)
        commit2 = Commit(hash, author, email, date, subject)
        self.assertEqual(commit1, commit2)

    def test_two_commits_with_different_hash_are_not_equal(self):
        author = 'PZ'
        email = 'zemek@petrzemek.net'
        date = get_curr_date()
        subject = 'Commit message'
        commit1 = Commit(get_rand_hash(), author, email, date, subject)
        commit2 = Commit(get_rand_hash(), author, email, date, subject)
        self.assertNotEqual(commit1, commit2)

    def test_two_commits_with_different_author_are_not_equal(self):
        hash = get_rand_hash()
        email = 'zemek@petrzemek.net'
        date = get_curr_date()
        subject = 'Commit message'
        commit1 = Commit(hash, 'Petr Zemek', email, date, subject)
        commit2 = Commit(hash, 'PZ', email, date, subject)
        self.assertNotEqual(commit1, commit2)

    def test_two_commits_with_different_email_are_not_equal(self):
        hash = get_rand_hash()
        author = 'PZ'
        date = get_curr_date()
        subject = 'Commit message'
        commit1 = Commit(hash, author, 'zemek@petrzemek.net', date, subject)
        commit2 = Commit(hash, author, 'petr.zemek@avast.com', date, subject)
        self.assertNotEqual(commit1, commit2)

    def test_two_commits_with_different_date_are_not_equal(self):
        hash = get_rand_hash()
        author = 'PZ'
        email = 'zemek@petrzemek.net'
        subject = 'Commit message'
        commit1 = Commit(
            hash,
            author,
            email,
            datetime.datetime(2007, 12, 11, 5, 43, 14),
            subject
        )
        commit2 = Commit(
            hash,
            author,
            email,
            datetime.datetime(2014, 5, 18, 10, 27, 53),
            subject
        )
        self.assertNotEqual(commit1, commit2)

    def test_two_commits_with_different_msg_are_not_equal(self):
        hash = get_rand_hash()
        author = 'PZ'
        date = get_curr_date()
        commit1 = Commit(
            hash,
            author,
            'zemek@petrzemek.net',
            date,
            'Commit message'
        )
        commit2 = Commit(
            hash,
            author,
            'petr.zemek@avast.com',
            date,
            'Some other commit message'
        )
        self.assertNotEqual(commit1, commit2)


class CommitHashTests(unittest.TestCase):
    """Tests for `Commit.__hash__()`."""

    def test_two_equal_commits_hash_to_same_value(self):
        date = get_curr_date()
        commit1 = Commit(40 * 'a', 'PZ', 'petr.zemek@avast.com', date, 'message')
        commit2 = Commit(40 * 'a', 'PZ', 'petr.zemek@avast.com', date, 'message')
        self.assertEqual(hash(commit1), hash(commit2))

    def test_two_commits_with_different_hash_do_not_hash_to_same_value(self):
        date = get_curr_date()
        commit1 = Commit(40 * 'a', 'PZ', 'petr.zemek@avast.com', date, 'message')
        commit2 = Commit(40 * 'f', 'PZ', 'petr.zemek@avast.com', date, 'message')
        self.assertNotEqual(hash(commit1), hash(commit2))

    def test_two_commits_with_different_author_do_not_hash_to_same_value(self):
        date = get_curr_date()
        commit1 = Commit(40 * 'a', 'PZ', 'petr.zemek@avast.com', date, 'message')
        commit2 = Commit(40 * 'f', 'Petr', 'petr.zemek@avast.com', date, 'message')
        self.assertNotEqual(hash(commit1), hash(commit2))

    def test_two_commits_with_different_email_do_not_hash_to_same_value(self):
        date = get_curr_date()
        commit1 = Commit(40 * 'a', 'PZ', 'petr.zemek@avast.com', date, 'message')
        commit2 = Commit(40 * 'f', 'PZ', 'zemek@petrzemek.net', date, 'message')
        self.assertNotEqual(hash(commit1), hash(commit2))

    def test_two_commits_with_different_date_do_not_hash_to_same_value(self):
        commit1 = Commit(
            40 * 'a',
            'PZ',
            'petr.zemek@avast.com',
            get_curr_date(),
            'message'
        )
        commit2 = Commit(
            40 * 'f',
            'PZ',
            'petr.zemek@avast.com',
            get_curr_date(),
            'message'
        )
        self.assertNotEqual(hash(commit1), hash(commit2))

    def test_two_commits_with_different_subject_do_not_hash_to_same_value(self):
        date = get_curr_date()
        commit1 = Commit(40 * 'a', 'PZ', 'petr.zemek@avast.com', date, 'message')
        commit2 = Commit(40 * 'f', 'PZ', 'petr.zemek@avast.com', date, 'hello')
        self.assertNotEqual(hash(commit1), hash(commit2))


class CommitReprTests(unittest.TestCase):
    """Tests for `Commit.__repr__()`."""

    def test_repr_works_correctly(self):
        commit = create_commit()
        commit_repr = repr(commit)
        self.assertIsInstance(commit_repr, str)
        self.assertEqual(eval(commit_repr), commit)


class BaseRepositoryTests(unittest.TestCase):
    """A base class for all `Repository` tests."""

    def setUp(self):
        self.cmd_runner = mock.Mock()
        self.cmd_runner.run_cmd.return_value = ('', 0, False)

    def create_repo(self, path):
        return Repository(path, self.cmd_runner)


class RepositoryCreateTests(BaseRepositoryTests):
    """Tests for Repository.__init__()."""

    def test_create_repo_calls_git_status(self):
        REPO_PATH = os.path.join(ROOT_DIR, 'existing', 'repository')
        self.create_repo(REPO_PATH)
        self.cmd_runner.run_cmd.assert_called_once_with(
            ['git', '-C', REPO_PATH, 'status'])

    def test_path_is_accessible_after_creating_repo_from_existing_repository(self):
        REPO_PATH = os.path.join(ROOT_DIR, 'existing', 'repository')
        repo = self.create_repo(REPO_PATH)
        self.assertEqual(repo.path, REPO_PATH)

    @mock.patch('os.path.abspath')
    def test_rel_path_is_converted_into_abs_path_after_creating_repo(
            self, mock_abspath):
        ABS_REPO_PATH = os.path.join(ROOT_DIR, 'existing', 'repository')
        REL_REPO_PATH = os.path.join('..', 'repository')
        mock_abspath.return_value = ABS_REPO_PATH
        repo = self.create_repo(REL_REPO_PATH)
        self.assertEqual(repo.path, ABS_REPO_PATH)

    def test_path_cannot_be_changed_after_creation(self):
        repo = self.create_repo(os.path.join(ROOT_DIR, 'existing', 'repository'))
        with self.assertRaises(AttributeError):
            repo.path = os.path.join(ROOT_DIR, 'other', 'repository')

    def test_create_repo_from_nonexisting_location_raises_exception(self):
        self.cmd_runner.run_cmd.return_value = (
            "fatal: Cannot change to '...': No such file or directory",
            128,
            False
        )
        with self.assertRaises(GitError):
            self.create_repo(os.path.join(ROOT_DIR, 'nonexisting', 'dir'))

    def test_create_repo_from_location_with_no_repository_raises_exception(self):
        self.cmd_runner.run_cmd.return_value = (
            'fatal: Not a git repository (or any parent up to mount point ...)',
            128,
            False
        )
        with self.assertRaises(GitError):
            self.create_repo(os.path.join(ROOT_DIR, 'no', 'repository'))


class BaseWithCreatedRepositoryTests(BaseRepositoryTests):
    """Base class for tests of a created `Repository`."""

    def setUp(self):
        super().setUp()
        self.repo = self.create_repo(os.path.join(ROOT_DIR, 'existing', 'repository'))


class BaseGetCommitTests(BaseWithCreatedRepositoryTests):
    """A base class for all `Repository.get_commit_*()` tests."""

    def setUp(self):
        super().setUp()
        self.hash = '4b34858294e9f4eee1cdd9af58911154b99472e3'
        self.author = 'Petr Zemek'
        self.email = 'petr.zemek@avast.com'
        self.date = get_curr_date()
        self.subject = 'Commit message'
        self.cmd_runner.run_cmd.return_value = (
            '{}\n{}\n{}\n{}\n{}\n\ndiff'.format(
                self.hash, self.author, self.email,
                int(self.date.timestamp()), self.subject),
            0,
            False
        )


class RepositoryGetCurrentBranchNameTests(BaseGetCommitTests):
    """Tests for `Repository.get_current_branch_name()`."""

    def test_calls_proper_command(self):
        self.repo.get_current_branch_name()
        self.cmd_runner.run_cmd.assert_called_with(
            ['git', '-C', self.repo.path, 'rev-parse', '--abbrev-ref', 'HEAD'])

    def test_returns_correct_branch_name(self):
        BRANCH = 'master'
        self.cmd_runner.run_cmd.return_value = (BRANCH + '\n', 0, False)
        self.assertEqual(self.repo.get_current_branch_name(), BRANCH)


class RepositoryGetCommitFromHashTests(BaseGetCommitTests):
    """Tests for `Repository.get_commit_from_hash()`."""

    def test_calls_proper_command(self):
        self.repo.get_commit_from_hash(self.hash)
        self.cmd_runner.run_cmd.assert_called_with([
            'git',
            '-C', self.repo.path,
            'show',
            '--quiet',
            '--format=format:%H%n%an%n%ae%n%at%n%s%n',
            self.hash
        ])

    def test_returns_correct_commit(self):
        self.assertEqual(
            self.repo.get_commit_from_hash(self.hash),
            Commit(self.hash, self.author, self.email, self.date, self.subject)
        )


class RepositoryGetCurrentCommitTests(BaseGetCommitTests):
    """Tests for `Repository.get_current_commit()`."""

    def test_calls_proper_command(self):
        self.repo.get_current_commit()
        self.cmd_runner.run_cmd.assert_called_with([
            'git',
            '-C', self.repo.path,
            'show',
            '--quiet',
            '--format=format:%H%n%an%n%ae%n%at%n%s%n',
            'HEAD'
        ])

    def test_returns_correct_commit(self):
        self.assertEqual(
            self.repo.get_current_commit(),
            Commit(self.hash, self.author, self.email, self.date, self.subject)
        )


class RepositoryGetCommitsSinceTests(BaseGetCommitTests):
    """Tests for `Repository.get_commits_since()`."""

    def test_calls_proper_command(self):
        commit = create_commit()
        self.repo.get_commits_since(commit)
        self.cmd_runner.run_cmd.assert_any_call([
            'git',
            '-C', self.repo.path,
            'log',
            '--first-parent',
            '--format=%H',
            commit.hash + '..HEAD'
        ])

    def test_returns_correct_commits(self):
        commit1 = create_commit()
        commit2 = create_commit()

        def cmd_runner_side_effect(cmd):
            if 'log' in cmd:
                return (
                    '\n'.join([commit1.hash, commit2.hash]),
                    0,
                    False
                )
            for c in [commit1, commit2]:
                if c.hash in cmd:
                    return (
                        '{}\n{}\n{}\n{}\n{}\n\ndiff'.format(
                            c.hash, c.author, c.email,
                            int(c.date.timestamp()), c.subject
                        ),
                        0,
                        False
                    )
        self.cmd_runner.run_cmd.side_effect = cmd_runner_side_effect
        commit = create_commit()
        self.assertEqual(self.repo.get_commits_since(commit), [commit2, commit1])


class RepositoryGetLastCommitsSinceTests(BaseGetCommitTests):
    """Tests for `Repository.get_last_commits()`."""

    def test_calls_proper_command(self):
        self.repo.get_last_commits(5)
        self.cmd_runner.run_cmd.assert_any_call([
            'git',
            '-C', self.repo.path,
            'log',
            '--first-parent',
            '--format=%H',
            'HEAD~~~~~..HEAD'
        ])

    def test_returns_correct_commits(self):
        commit1 = create_commit()
        commit2 = create_commit()

        def cmd_runner_side_effect(cmd):
            if 'log' in cmd:
                return (
                    '\n'.join([commit1.hash, commit2.hash]),
                    0,
                    False
                )
            for c in [commit1, commit2]:
                if c.hash in cmd:
                    return (
                        '{}\n{}\n{}\n{}\n{}\n\ndiff'.format(
                            c.hash, c.author, c.email,
                            int(c.date.timestamp()), c.subject
                        ),
                        0,
                        False
                    )
        self.cmd_runner.run_cmd.side_effect = cmd_runner_side_effect
        self.assertEqual(self.repo.get_last_commits(10), [commit2, commit1])


class RepositoryCheckoutTests(BaseGetCommitTests):
    """Tests for `Repository.checkout()`."""

    def test_checkouts_commit_upon_enter_when_commit_is_not_current_commit(self):
        commit = create_commit()
        self.repo.get_current_commit = mock.Mock(return_value=create_commit())
        with self.repo.checkout(commit):
            self.cmd_runner.run_cmd.assert_called_with(
                ['git', '-C', self.repo.path, 'checkout', commit.hash]
            )

    def test_checkouts_back_original_commit_upon_exit_when_commit_is_not_current_commit(self):
        original_branch = 'master'
        self.cmd_runner.run_cmd.return_value = (original_branch + '\n', 0, False)
        self.repo.get_current_commit = mock.Mock(return_value=create_commit())
        new_commit = create_commit()
        with self.repo.checkout(new_commit):
            self.cmd_runner.run_cmd.reset_mock()
        self.cmd_runner.run_cmd.assert_called_with(
            ['git', '-C', self.repo.path, 'checkout', original_branch]
        )

    def test_does_nothing_when_commit_is_currently_checked_out_commit(self):
        commit = create_commit()
        self.repo.get_current_commit = mock.Mock(return_value=commit)
        self.cmd_runner.run_cmd.reset_mock()
        with self.repo.checkout(commit):
            pass
        self.assertFalse(self.cmd_runner.run_cmd.called)


class RepositoryUpdateTests(BaseGetCommitTests):
    """Tests for `Repository.update()`."""

    def test_calls_proper_git_command_when_on_branch(self):
        self.cmd_runner.run_cmd.return_value = ('master', 0, False)

        self.repo.update()

        self.cmd_runner.run_cmd.assert_has_calls([
            mock.call(['git', '-C', self.repo.path, 'pull'])
        ])

    def test_calls_proper_git_commands_when_in_detached_head_state(self):
        self.cmd_runner.run_cmd.return_value = ('HEAD', 0, False)

        self.repo.update()

        self.cmd_runner.run_cmd.assert_has_calls([
            mock.call(['git', '-C', self.repo.path, 'checkout', 'master']),
            mock.call(['git', '-C', self.repo.path, 'pull'])
        ])


class RepositoryCloneTests(BaseRepositoryTests):
    """Tests for `Repository.clone()`."""

    def test_calls_correct_git_command(self):
        Repository.clone('url', 'path', self.cmd_runner)

        self.cmd_runner.run_cmd.assert_any_call(
            ['git', 'clone', 'url', 'path']
        )

    def test_creates_repository_when_clone_succeeds(self):
        self.cmd_runner.run_cmd.return_value = ('', 0, False)

        repo = Repository.clone('url', 'path', self.cmd_runner)

        self.assertEqual(repo.path, os.path.join(os.getcwd(), 'path'))

    def test_raises_exception_when_clone_fails(self):
        self.cmd_runner.run_cmd.return_value = ('error', 1, False)

        with self.assertRaisesRegex(GitError, r'.*clone.*'):
            Repository.clone('url', 'path', self.cmd_runner)


class ContainsUsernameTests(unittest.TestCase):
    """Tests for `contains_username()`."""

    def test_returns_true_when_url_contains_username(self):
        self.assertTrue(contains_username('ssh://login@host.com/repo.git'))

    def test_returns_false_when_url_contains_username(self):
        self.assertFalse(contains_username('ssh://host.com/repo.git'))


class AddUsernameTests(unittest.TestCase):
    """Tests for `add_username()`."""

    def test_adds_username_when_there_is_no_username_in_url(self):
        url = add_username('login', 'ssh://host.com/repo.git')

        self.assertEqual(url, 'ssh://login@host.com/repo.git')

    def test_does_nothing_when_there_already_is_username_in_url(self):
        URL = 'ssh://login@host.com/repo.git'

        new_url = add_username('login', URL)

        self.assertEqual(new_url, URL)

    def test_does_nothing_when_username_is_empty(self):
        URL = 'ssh://login@host.com/repo.git'

        new_url = add_username('', URL)

        self.assertEqual(new_url, URL)
