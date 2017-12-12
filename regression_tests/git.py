"""
    Interface to git.
"""

# The implementation is based on
# https://github.com/s3rvac/git-branch-viewer/blob/master/viewer/git.py

import contextlib
import datetime
import os
import re


class GitError(Exception):
    """An exception that is raised when there is an error during interaction
    with a git repository.
    """
    pass


class Commit:
    """A representation of a git commit."""

    #: The length of a valid hash. Hashes of a different length are not
    #: permitted.
    VALID_HASH_LENGTH = 40

    #: The set of valid hash characters '0123456789abcdef'. Other characters
    #: are not permitted in a hash.
    VALID_HASH_CHARACTERS = set('0123456789abcdef')

    def __init__(self, hash, author, email, date, subject):
        """
        :param str hash: Identifier of the commit.
        :param str author: Author of the commit.
        :param str email: Email of the author.
        :param date date: Date the commit was authored.
        :param str subject: Commit subject (the first line of the commit
                            message).

        The hash is normalized so that it contains only lowercase characters.
        The data cannot be changed after the commit is created.

        :raises ValueError: If the hash's length differs from
                            :attr:`VALID_HASH_LENGTH` or if the hash contains
                            characters out of :attr:`VALID_HASH_CHARACTERS`.
        """
        self._hash = self._normalize_hash(hash)
        self._verify_hash(self._hash)

        self._author = author
        self._email = email
        self._date = date
        self._subject = subject

    @property
    def hash(self):
        """Identifier of the commit."""
        return self._hash

    @property
    def author(self):
        """Author of the commit."""
        return self._author

    @property
    def email(self):
        """Email of the author."""
        return self._email

    @property
    def date(self):
        """Date the commit was authored."""
        return self._date

    @property
    def subject(self):
        """Subject (the first line of commit message)."""
        return self._subject

    def short_subject(self, length=50):
        """Shorter version of the subject.

        When the subject is of a shorter or equal length as `length`, it is
        returned unmodified. However, when it is longer than `length`, the
        first `length` characters are returned with appended ellipsis
        (`...`).
        """
        if len(self.subject) <= length:
            return self.subject
        return '{}...'.format(self.subject[:length])

    def short_hash(self, length=8):
        """Shorter version of the hash."""
        return self.hash[:length]

    @property
    def age(self):
        """Age of the commit."""
        return datetime.datetime.today() - self.date

    def __eq__(self, other):
        return (self.hash == other.hash and
                self.author == other.author and
                self.email == other.email and
                self.date == other.date and
                self.subject == other.subject)

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        return hash(repr(self))

    def __repr__(self):
        return '{}({!r}, {!r}, {!r}, {!r}, {!r})'.format(
            self.__class__.__name__,
            self.hash,
            self.author,
            self.email,
            self.date,
            self.subject)

    def _normalize_hash(self, hash):
        """Returns a normalized version of the given hash."""
        return hash.lower()

    def _verify_hash(self, hash):
        """Checks that the hash is of a correct format."""
        self._verify_hash_length(hash)
        self._verify_hash_characters(hash)

    def _verify_hash_length(self, hash):
        """Checks that the hash is of a correct length."""
        if len(hash) != self.VALID_HASH_LENGTH:
            raise ValueError(
                "hash '{}' has invalid length {} (expected {})".format(
                    hash, len(hash), self.VALID_HASH_LENGTH))

    def _verify_hash_characters(self, hash):
        """Checks that the hash contains valid characters."""
        hash_characters = set(hash)
        invalid_characters = hash_characters - self.VALID_HASH_CHARACTERS
        if invalid_characters:
            raise ValueError(
                "hash '{}' contains invalid character(s): '{}'".format(
                    hash, ''.join(invalid_characters)))


class Repository:
    """An interface to a git repository."""

    def __init__(self, path, cmd_runner):
        """
        :param str path: A path to the repository.
        :param CmdRunner cmd_runner: Runner of external commands to be used.

        If the path is relative, it is converted into an absolute path.

        :raises GitError: If the repository does not exist.
        """
        self._path = os.path.abspath(path)
        self._cmd_runner = cmd_runner
        self._verify_repository_existence()

    @property
    def path(self):
        """Absolute path to the repository."""
        return self._path

    def get_current_branch_name(self):
        """Returns the name of the currently checked-out branch."""
        return self._run_git_cmd(['rev-parse', '--abbrev-ref', 'HEAD']).strip()

    def get_commit_from_hash(self, hash):
        """Returns the commit corresponding to the given hash."""
        return self._get_commit_from_git_show_with_object(hash)

    def get_current_commit(self):
        """Returns the currently checked-out commit."""
        return self._get_commit_from_git_show_with_object('HEAD')

    def get_commits_since(self, commit):
        """Returns a list of commits since the given commit (:class:`.Commit`).

        More precisely, it returns a list of commits from the range
        ``commit..HEAD``. Moreover, only commits from the first parent are
        included so that when there is a merge commit, only the merge commit is
        returned, not the merged commits.

        The commit itself is not included into the resulting list.
        """
        return self._get_commits_in_range('{}..HEAD'.format(commit.hash))

    def get_last_commits(self, count):
        """Returns a list of the last `count` commits."""
        # To explain the code below, for example, if count is 5, we return all
        # the commits in range
        #
        #   HEAD~~~~~..HEAD
        #
        # There are many other ways of obtaining the last commits, and this way
        # enables us to use _get_commits_in_range(), so this is why this way
        # was chosen.
        return self._get_commits_in_range('HEAD' + ('~' * count) + '..HEAD')

    @contextlib.contextmanager
    def checkout(self, commit):
        """A context manager that checkouts the given commit
        (:class:`.Commit`).

        When `commit` is the currently checked out commit, this function does
        nothing.
        """
        original_commit = self.get_current_commit()
        try:
            if commit != original_commit:
                original_branch = self.get_current_branch_name()
                self._run_git_cmd(['checkout', commit.hash])
            yield
        finally:
            if commit != original_commit:
                self._run_git_cmd(['checkout', original_branch])

    def update(self):
        """Updates the repository."""
        # When we are in a detached-HEAD state (a specific commit has been
        # checked out), we have to first checkout master; otherwise, the pull
        # will fail. This may happen e.g. when the runner was abruptly stopped
        # (killed) during testing.
        if self._is_in_detached_head_state():
            self._run_git_cmd(['checkout', 'master'])
        self._run_git_cmd(['pull'])

    @classmethod
    def clone(cls, url, path, cmd_runner):
        """Clones a repository on `url` into `path`.

        :param str url: URL of the repository.
        :param str path: A path to which the repository will be cloned.
        :param CmdRunner cmd_runner: Runner of external commands to be used.

        :returns: The cloned repository (:class:`Repository`).
        """
        output, return_code, _ = cmd_runner.run_cmd(['git', 'clone', url, path])
        if return_code != 0:
            raise GitError(
                "clone of '{}' into '{}' failed; reason: {}".format(url, path, output)
            )
        return cls(path, cmd_runner)

    def _is_in_detached_head_state(self):
        """Is the repository in a detached-HEAD state?"""
        return self.get_current_branch_name() == 'HEAD'

    def _get_commit_from_git_show_with_object(self, obj):
        """Returns a commit from the output of ``git show`` with the given
        object (like commit).
        """
        # We use `git show` with a custom format to get just the needed
        # information about the commit. The used format produces output of the
        # following form:
        #
        #   hash
        #   author
        #   email
        #   date (timestamp)
        #   subject
        #
        # The '--quiet' parameter prevents a diff from being displayed (we do
        # not need it).
        output = self._run_git_cmd([
            'show', '--quiet', '--format=format:%H%n%an%n%ae%n%at%n%s%n', obj
        ])
        m = re.match(r"""
                (?P<hash>[a-fA-F0-9]+)\n
                (?P<author>.+)\n
                (?P<email>.+)\n
                (?P<date_ts>[0-9]+)\n
                (?P<subject>.+)\n
            """, output, re.VERBOSE | re.MULTILINE)
        hash = m.group('hash')
        author = m.group('author')
        email = m.group('email')
        date = datetime.datetime.fromtimestamp(int(m.group('date_ts')))
        subject = m.group('subject')
        return Commit(hash, author, email, date, subject)

    def _get_commits_in_range(self, range):
        """Returns a list of commits in the given range (`str`, like
        ``'hash~..HEAD'``).

        Only commits from the first parent are included so that when there is a
        merge commit, only the merge commit is returned, not the merged
        commits. This, however, works only for "true" merges, not for
        fast-forward merges. Fast-forward merges are generally undetectable.
        """
        cmd = ['log', '--first-parent', '--format=%H', range]
        output = self._run_git_cmd(cmd)
        # The output should be of the form
        #
        #   hash1
        #   hash2
        #   ...
        #
        hashes = output.split('\n')
        # Check that hash is non-empty before creating a commit from it because
        # there may be an empty line in the output.
        commits = [self.get_commit_from_hash(hash) for hash in hashes if hash]
        # We have to reverse the list so that the newest commits appear last.
        commits.reverse()
        return commits

    def _run_git_cmd(self, args):
        """Runs the git command with the given arguments in the repository and
        returns the output.
        """
        git_cmd = ['git', '-C', self.path] + args
        output, return_code, _ = self._cmd_runner.run_cmd(git_cmd)
        if return_code != 0:
            raise GitError("error during the execution of '{}'".format(git_cmd))
        return output

    def _verify_repository_existence(self):
        """Checks that the repository exists."""
        self._run_git_cmd(['status'])


def contains_username(repo_url):
    """Does the given repository URL (`str`) contain a username?"""
    return '@' in repo_url


def add_username(username, repo_url):
    """Adds `username` (`str`) into the given repository URL (`str`).

    This function does nothing when there already is a username or `username`
    is empty.
    """
    if username and not contains_username(repo_url):
        repo_url = re.sub(
            r'^ssh://',
            'ssh://' + re.escape(username) + '@',
            repo_url
        )
    return repo_url
