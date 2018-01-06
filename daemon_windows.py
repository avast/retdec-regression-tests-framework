#!/usr/bin/env python3
"""
    A simplified version of ``daemon.py`` for Windows.
"""

import argparse
import contextlib
import logging
import os
import sys
import time

from regression_tests.cmd_runner import CmdRunner
from regression_tests.config import parse_config
from regression_tests.db import DB
from regression_tests.git import Repository
from regression_tests.io import print_error
from regression_tests.logging import setup_logging
from regression_tests.qos import WithQoS
from regression_tests.utils.list import merge_duplicates


# Absolute path to the root directory of regression tests.
ROOT_DIR = os.path.abspath(os.path.dirname(__file__))

# Path to the runner.py script.
RUNNER_PATH = os.path.join(ROOT_DIR, 'runner.py')

# We need to use a PID file because the approach with sockets is only for
# Linux.
PID_FILE_PATH = os.path.join(ROOT_DIR, __file__ + '.pid')


def process_exists(pid):
    """Checks if a process with the given PID exists."""
    # Based on http://stackoverflow.com/a/20186516/2580955.
    try:
        os.kill(pid, 0)
    except PermissionError:
        return True  # Operation not permitted (i.e. the process exists).
    except ProcessLookupError:
        return False
    except OSError as ex:
        # On our Windows server, kill() raises the following exception when
        # there is no such process with the given PID (it does not raise
        # ProcessLookupError as expected).
        if str(ex) == '[WinError 87] The parameter is incorrect':
            return False
        # Re-raise the exception because it is an unexpected one.
        raise
    return True


def exit_if_already_running():
    """Exits the script if it is already running."""
    # The following approach is susceptible to race conditions, but since I was
    # not able to find a better way of doing this on Windows, I use it anyway.
    if os.path.isfile(PID_FILE_PATH):
        # Check if the process is already running.
        with open(PID_FILE_PATH, 'r') as f:
            pid = int(f.read())
        if process_exists(pid):
            print_error(
                'script is already running ({}) -> exiting'.format(PID_FILE_PATH)
            )
            sys.exit(1)

    # We may run.
    with open(PID_FILE_PATH, 'w') as f:
        f.write(str(os.getpid()))


def parse_args():
    """Parses command-line arguments and returns them."""
    parser = argparse.ArgumentParser(
        description='Daemon that automatically runs regression tests for new commits.'
    )
    args = parser.parse_args()
    return args


# Do not put the following call to the try block because we want the PID file
# to be removed only if the process that created it ends.
exit_if_already_running()


try:
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
    wait_time = int(config['daemon']['wait_time'])
    while True:
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

        # We need at least one commit to continue.
        if not commits:
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
        logging.info('running tests for commit {}'.format(commit.hash))
        cmd_runner.run_cmd([
            'python3',
            'runner.py',
            '--commit', commit.hash,
            '--build'
        ])
except Exception:
    logging.exception('unhandled exception')
    raise
finally:
    # We have to properly remove the PID file.
    with contextlib.suppress(FileNotFoundError):
        os.remove(PID_FILE_PATH)
