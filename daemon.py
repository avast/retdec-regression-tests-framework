#!/usr/bin/env python3
"""
    Daemon for Linux that automatically runs regression tests for new commits.

    This script is only for Linux. If you want to run the daemon on Windows,
    use ``daemon_windows.py`` instead.
"""

import argparse
import logging
import os
import signal
import socket
import sys
import time

from regression_tests.cmd_runner import CmdRunner
from regression_tests.config import parse as parse_config
from regression_tests.db import DB
from regression_tests.git import Repository
from regression_tests.io import print_error
from regression_tests.logging import setup_logging
from regression_tests.qos import WithQoS
from regression_tests.utils.os import on_windows
from regression_tests.utils.list import merge_duplicates


# Absolute path to the root directory of regression tests.
ROOT_DIR = os.path.abspath(os.path.dirname(__file__))

# Path to the runner.py script.
RUNNER_PATH = os.path.join(ROOT_DIR, 'runner.py')


def get_script_user():
    """Returns the name of the user who started the script."""
    import pwd  # Import it here because it does not exist on Windows.
    return pwd.getpwuid(os.getuid()).pw_name


def exit_if_on_windows():
    """Exits the script if it is run on MS Windows."""
    # This script needs support of signal.SIGCONT, socket.AF_UNIX, and
    # os.killpg(), which are not present on MS Windows.
    if on_windows():
        print_error('this script cannot be run on MS Windows')
        sys.exit(1)


def exit_if_already_running():
    """Exits the script if it is already running for the current user."""
    # Instead of storing the PID of the process in the filesystem and checking
    # whether it already exists, we utilize AF_UNIX sockets and the abstract
    # namespace. In this way, we don't have to manage any files.
    # Based on http://stackoverflow.com/a/7758075/2580955.
    # See also http://blog.eduardofleury.com/archives/2007/09/13 for more
    # information on AF_UNIX sockets.
    #
    # The socket has to be global. Otherwise, it would be closed once this
    # function finishes because of the garbage collector.
    global lock_socket
    lock_socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
    try:
        # To bind the socket to the abstract namespace, we have to start its
        # name with the null byte.
        lock_socket.bind('\0' + __file__ + get_script_user())
    except socket.error:
        print_error('script is already running -> exiting')
        sys.exit(1)


def parse_args():
    """Parses command-line arguments and returns them."""
    parser = argparse.ArgumentParser(
        description='Daemon that automatically runs regression tests for new commits.'
    )
    args = parser.parse_args()
    return args


def non_critical_tests_have_finished():
    """Checks if non-critical tests have finished."""
    if non_critical_tests is None:
        return False
    return non_critical_tests.poll() is not None


def update_commits_for_non_critical_tests_and_get_commit_to_be_tested():
    """Updates ``commits_for_non_critical_tests``.

    Returns commit to be tested, or ``None`` if there is no commit to be
    tested.
    """
    commit = db.get_commit_for_non_critical_tests(max_initial_commits)
    if commit:
        # There is a new commit to be tested.
        if commit in commits_for_non_critical_tests:
            commits_for_non_critical_tests.remove(commit)
        commits_for_non_critical_tests.append(commit)
        return commit

    if commits_for_non_critical_tests:
        # We have some older commits to be tested.
        return commits_for_non_critical_tests[-1]

    return None


def stop_non_critical_tests():
    """Stops non-critical tests in a safe manner."""
    global non_critical_tests
    # Do not use non_critical_tests.send_signal() because of possible race
    # conditions
    # (http://python.6.x6.nabble.com/Avoid-race-condition-with-Popen-send-signal-td2825095.html).
    os.killpg(non_critical_tests.pid, signal.SIGCONT)
    # Do not use non_critical_tests.wait() because of a possible deadlock
    # (https://docs.python.org/3/library/subprocess.html#subprocess.Popen.wait).
    # The reason is that non-critical tests are started by calling
    # CmdRunner.start(), which uses pipes.
    non_critical_tests.communicate()
    non_critical_tests = None


def kill_non_critical_tests():
    """Kills non-critical tests (if they are still running)."""
    # non_critical_tests may not be defined when this function is called.
    if 'non_critical_tests' in globals() and non_critical_tests is not None:
        os.killpg(non_critical_tests.pid, signal.SIGTERM)


try:
    exit_if_on_windows()
    exit_if_already_running()

    # Config.
    config = parse_config('config.ini', 'config_local.ini')

    # Logging.
    setup_logging(config, os.path.basename(__file__))
    logging.info('script started (`' + ' '.join(sys.argv) + '`)')

    # Quality of Service.
    qos_enabled = config.getboolean('qos', 'enabled')
    qos_max_tries = int(config['qos']['max_tries'])
    qos_wait_time = int(config['qos']['wait_time'])

    # Database.
    db = DB(config['db']['conn_url'])
    if qos_enabled:
        db = WithQoS(db, qos_max_tries, qos_wait_time)

    # Arguments.
    args = parse_args()

    # Command runner.
    cmd_runner = CmdRunner()

    # Repository.
    retdec_repo_dir = config['daemon']['retdec_repo_dir']
    if not retdec_repo_dir:
        raise ValueError("'retdec_repo_dir' in [daemon] is not set")
    elif retdec_repo_dir == config['runner']['retdec_repo_dir']:
        raise ValueError('runner and daemon cannot share the same repository')
    repo = Repository(retdec_repo_dir, cmd_runner)
    if qos_enabled:
        repo = WithQoS(repo, qos_max_tries, qos_wait_time)

    commits = []
    non_critical_tests = None
    skip_non_critical_tests_check = False
    commits_for_non_critical_tests = []
    wait_time = int(config['daemon']['wait_time'])
    while True:
        # Check the current run of non-critical tests (if any).
        if non_critical_tests_have_finished():
            commits_for_non_critical_tests.pop()
            non_critical_tests = None

        repo.update()

        # Get commits to be processed. We simply extend the list and merge any
        # duplicates afterwards.
        #
        # (1) Not-yet-processed commits that are already in the database.
        commits.extend(db.get_unprocessed_commits())
        # (2) New commits in the repository.
        max_initial_commits = int(config['daemon']['max_initial_commits'])
        last_commit = db.get_topmost_commit()
        if last_commit is not None:
            commits.extend(repo.get_commits_since(last_commit))
        else:
            commits.extend(repo.get_last_commits(max_initial_commits))

        # We have to merge duplicates (if any) because the previous actions may
        # have introduced duplicate commits.
        commits = merge_duplicates(commits)

        if commits:
            # There is at least one new commit, so allow a check for
            # non-critical tests.
            skip_non_critical_tests_check = False

            # Check whether we have to stop the non-critical tests because there is
            # a new commit to be processed.
            if non_critical_tests is not None:
                new_commit_hashes = [commit.hash for commit in commits]
                logging.info('stopping non-critical tests for commit {} (new commits: {})'.format(
                    commits_for_non_critical_tests[-1].hash,
                    ', '.join(new_commit_hashes)))
                stop_non_critical_tests()
        else:
            # No commits. Check whether we should wait for new commits or start
            # non-critical tests.
            if non_critical_tests is None and not skip_non_critical_tests_check:
                commit = update_commits_for_non_critical_tests_and_get_commit_to_be_tested()
                if commit:
                    # Run non-critical tests (asynchronously so that we can
                    # stop them when a new commit appears in the repository).
                    logging.info('running non-critical tests for commit {}'.format(
                        commit.hash))
                    non_critical_tests = cmd_runner.start(
                        [
                            'python3',
                            RUNNER_PATH,
                            '--commit', commit.hash,
                            '--build',
                            '--support-stop',
                            '--resume'
                        ],
                        # The output from runner.py is irrelevant as we do not do
                        # anything with it.
                        discard_output=True
                    )
                else:
                    # There are no non-critical tests, so we can skip further
                    # checks until there is a new commit. Queries for them,
                    # more specifically db.get_commit_for_non_critical_tests(),
                    # take some time, so this check saves us time.
                    skip_non_critical_tests_check = True

            # Wait.
            time.sleep(wait_time)
            continue

        # Insert the commits into the database so that we can then process them
        # in any order. If a commit is already in the database, it is
        # automatically skipped.
        db.insert_commits(commits)

        # Process just the newest commit and then check whether there are newer
        # commits. This is done so that the newest commits are processed first
        # to get the most meaningful feedback as soon as possible.
        commit = commits.pop()
        logging.info('running critical tests for commit {}'.format(commit.hash))
        cmd_runner.run_cmd([
            'python3',
            RUNNER_PATH,
            '--commit', commit.hash,
            '--build',
            '--critical'
        ])
except Exception:
    logging.exception('unhandled exception')
    raise
finally:
    kill_non_critical_tests()
