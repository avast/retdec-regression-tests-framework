#!/usr/bin/env python3
"""
    Runner of regression tests.
"""

import argparse
import io
import logging
import multiprocessing as mp
import os
import shutil
import signal
import stat
import sys
import traceback
import unittest
from datetime import datetime

from regression_tests.clang import setup_clang_bindings
from regression_tests.cmd_runner import CmdRunner
from regression_tests.config import parse_standard_config_files
from regression_tests.db import DB
from regression_tests.email import prepare_email
from regression_tests.email import send_email
from regression_tests.filesystem.directory import Directory
from regression_tests.git import Repository
from regression_tests.git import add_username
from regression_tests.io import print_error
from regression_tests.io import print_prologue
from regression_tests.io import print_summary
from regression_tests.io import print_test_results
from regression_tests.logging import setup_logging
from regression_tests.qos import WithQoS
from regression_tests.retdec_builder import build_retdec
from regression_tests.test_finder import find_tests
from regression_tests.test_finder import get_tests_dir
from regression_tests.test_results import NoTestResults
from regression_tests.test_results import TestResults
from regression_tests.test_results import TestsResults
from regression_tests.test_settings import TestSettings


def parse_args():
    """Parses command-line arguments and returns them."""
    parser = argparse.ArgumentParser(description='Runner of regression tests.')
    parser.add_argument('tests_dir', type=str, metavar='PATH', nargs='?',
                        help='Explicit path to the tests.')
    parser.add_argument('-b', '--build', action='store_true', dest='build',
                        help=('Build RetDec before testing (enabled if -c/--commit is used).'))
    parser.add_argument('-c', '--commit', type=str, metavar='SHA', dest='commit',
                        help='Force commit to be tested.')
    parser.add_argument('-C', '--critical', action='store_true', dest='only_critical',
                        help='Run only critical tests.')
    parser.add_argument('-r', '--regexp', type=str, metavar='REGEXP', dest='regexp',
                        help='Run only tests matching the given regular expression.')
    parser.add_argument('-R', '--resume', action='store_true', dest='resume',
                        help='Do not run tests that have already run for the commit.')
    parser.add_argument('-s', '--support-stop', action='store_true', dest='support_stop',
                        help=('Support a graceful stopping of run tests '
                              '(Linux only, needed in the daemon).'))
    parser.add_argument('-t', '--tool', type=str, metavar='TOOL', dest='tool',
                        help='Run only tests for the given tool.')
    args = parser.parse_args()

    if args.commit is not None:
        args.build = True

    return args


def ensure_is_run_from_script_dir():
    """Ensures that the script is run from its directory."""
    script_dir = os.path.abspath(os.path.dirname(__file__))
    if os.getcwd() != script_dir:
        print_error(
            '{} has to be run from {}, not from {}'.format(
                os.path.basename(__file__),
                script_dir,
                os.getcwd()
            )
        )
        sys.exit(1)


def ensure_all_required_settings_are_set(config):
    """Ensures that all required settings in the given configuration are set."""
    # [runner] -> clang_dir
    clang_dir = config['runner']['clang_dir']
    if not clang_dir:
        print_error("no 'clang_dir' in the [runner] section of config_local.ini "
                    "(you have to add it)")
        sys.exit(1)
    elif not os.path.exists(clang_dir):
        print_error("'clang_dir' in the [runner] section of config_local.ini "
                    "points to a non-existing directory")
        sys.exit(1)
    elif not os.path.exists(os.path.join(clang_dir, 'bin')):
        print_error("'clang_dir' in the [runner] section of config_local.ini "
                    "does not seem to point to Clang")
        sys.exit(1)

    # [runner] -> retdec_build_dir
    retdec_build_dir = config['runner']['retdec_build_dir']
    if not retdec_build_dir:
        print_error("no 'retdec_build_dir' in the [runner] section of config_local.ini "
                    "(you have to add it)")
        sys.exit(1)
    elif not os.path.exists(retdec_build_dir):
        print_error("'retdec_build_dir' in the [runner] section of config_local.ini "
                    "points to a non-existing directory")
        sys.exit(1)
    elif not os.path.exists(os.path.join(retdec_build_dir, 'CMakeCache.txt')):
        print_error("'retdec_build_dir' in the [runner] section of config_local.ini "
                    "does not seem to point to a RetDec build directory")
        sys.exit(1)

    # [runner] -> retdec_install_dir
    retdec_install_dir = config['runner']['retdec_install_dir']
    if not retdec_install_dir:
        print_error("no 'retdec_install_dir' in the [runner] section of config_local.ini "
                    "(you have to add it)")
        sys.exit(1)
    elif not os.path.exists(retdec_install_dir):
        print_error("'retdec_install_dir' in the [runner] section of config_local.ini "
                    "points to a non-existing directory")
        sys.exit(1)
    elif not os.path.exists(os.path.join(retdec_install_dir, 'bin', 'decompile.sh')):
        print_error("'retdec_install_dir' in the [runner] section of config_local.ini "
                    "does not seem to point to RetDec")
        sys.exit(1)

    # [runner] -> retdec_repo_dir
    retdec_repo_dir = config['runner']['retdec_repo_dir']
    if not retdec_repo_dir:
        print_error("no 'retdec_repo_dir' in the [runner] section of config_local.ini "
                    "(you have to add it)")
        sys.exit(1)
    elif not os.path.exists(retdec_repo_dir):
        print_error("'retdec_repo_dir' in the [runner] section of config_local.ini "
                    "points to a non-existing directory")
        sys.exit(1)
    elif not os.path.exists(os.path.join(retdec_repo_dir, 'src', 'bin2llvmir')):
        print_error("'retdec_repo_dir' in the [runner] section of config_local.ini "
                    "does not seem to point to a RetDec repository")
        sys.exit(1)

    # [runner] -> tests_root_dir
    tests_root_dir = config['runner']['tests_root_dir']
    if not tests_root_dir:
        print_error("no 'tests_root_dir' in the [runner] section of config_local.ini "
                    "(you have to add it)")
        sys.exit(1)
    elif not os.path.exists(tests_root_dir):
        print_error("'tests_root_dir' in the [runner] section of config_local.ini "
                    "points to a non-existing directory")
        sys.exit(1)
    elif not os.path.exists(os.path.join(tests_root_dir, 'bugs')):
        print_error("'tests_root_dir' in the [runner] section of config_local.ini "
                    "does not seem to point to regression tests")
        sys.exit(1)

    if config['runner'].getboolean('idaplugin_tests_enabled'):
        # [runner] -> idaplugin_ida_dir
        idaplugin_ida_dir = config['runner']['idaplugin_ida_dir']
        if not idaplugin_ida_dir:
            print_error("no 'idaplugin_ida_dir' in the [runner] section of config_local.ini "
                        "(you have to add it to run tests for our IDA plugin)")
            sys.exit(1)
        elif not os.path.exists(idaplugin_ida_dir):
            print_error("'idaplugin_ida_dir' in the [runner] section of config_local.ini "
                        "points to a non-existing directory")
            sys.exit(1)
        elif not os.path.exists(os.path.join(idaplugin_ida_dir, 'plugins')):
            print_error("'idaplugin_ida_dir' in the [runner] section of config_local.ini "
                        "does not seem to point to IDA Pro")
            sys.exit(1)

        # [runner] -> idaplugin_script
        idaplugin_script = config['runner']['idaplugin_script']
        if not idaplugin_script:
            print_error("no 'idaplugin_script' in the [runner] section of config_local.ini "
                        "(you have to add it to run tests for our IDA plugin)")
            sys.exit(1)
        elif not os.path.exists(idaplugin_script):
            print_error("'idaplugin_script' in the [runner] section of config_local.ini "
                        "points to a non-existing file")
            sys.exit(1)


def adjust_environment(config):
    """Adjusts the environment so that the regression tests may run (e.g.
    update PATH).
    """
    if config['runner'].getboolean('idaplugin_tests_enabled'):
        tools_dir = os.path.join(config['runner']['retdec_install_dir'], 'bin')

        # run-ida-decompilation.sh requires decompile.sh to be reachable from PATH.
        os.environ['PATH'] = tools_dir + os.pathsep + os.environ['PATH']

        # run-ida-decompilation.sh requires path to IDA Pro.
        os.environ['IDA_PATH'] = config['runner']['idaplugin_ida_dir']

        # Copy run-ida-decompilation.sh into the directory where other tools
        # are located so it can be found. However, do this only when runner.py
        # is run (not for spawned processes to prevent multiple processes from
        # overwriting the same file).
        if __name__ == '__main__':
            target_script_path = os.path.join(tools_dir, 'run-ida-decompilation.sh')
            shutil.copyfile(config['runner']['idaplugin_script'], target_script_path)
            # We also need to ensure that the copied file is executable by the
            # current user.
            os.chmod(
                target_script_path,
                os.stat(target_script_path).st_mode | stat.S_IXUSR
            )

    # We have to provide path to our supportive scripts (e.g.
    # regression_tests.tools.decompilation_test.DecompilationTest._get_compiler_for_out_c()
    # relies on windows-gcc-32.sh being in PATH).
    root_path = os.path.dirname(__file__)
    scripts_dir = os.path.join(root_path, 'support', 'scripts')
    os.environ['PATH'] = scripts_dir + os.pathsep + os.environ['PATH']


def run_retdec_build(config, db, cmd_runner, tested_commit):
    """Runs a build of RetDec.

    If the build fails, it prints and error message and sends an email to the
    author of the tested commit (if needed).
    """
    build_start_date = datetime.now()
    build_id = db.insert_build_started_info(
        tested_commit,
        build_start_date
    )
    build_info = build_retdec(
        Directory(config['runner']['retdec_build_dir']),
        cmd_runner,
        int(config['runner']['build_procs'])
    )

    # Ensure that the same date appears after the build is finished
    # (otherwise, there may be a difference of a few seconds).
    build_info.start_date = build_start_date
    db.insert_build_ended_info(build_id, build_info)

    if not build_info.succeeded:
        LINES_COUNT = 30
        error_msg = 'failed to build RetDec; ' +\
            'showing the last {} lines of the log:\n...\n'.format(LINES_COUNT) +\
            '\n'.join(build_info.log.split('\n')[-LINES_COUNT:]).strip()
        logging.error(error_msg)
        print_error(error_msg)

        send_email_for_commit_if_needed(config, db, tested_commit)

        sys.exit(1)


def get_num_of_procs_for_tests(config):
    """Returns the number of processes to be used to run the tests."""
    tests_procs = int(config['runner']['tests_procs'])
    return tests_procs if tests_procs > 0 else mp.cpu_count()


def remove_results_from_previous_test_runs(tests_dir):
    """Removes results from previous test runs in the given directory.

    It performs the removal recursively, i.e. also in subdirectories.
    """
    for dir, _, _ in tests_dir.walk():
        if dir.name == TestSettings.outputs_dir_name:
            dir.remove()


def get_excluded_dirs(tests_root_dir, config):
    """Returns a list of directories to exclude when running tests."""
    dirs = config['runner']['excluded_dirs']
    dir_paths = dirs.split(',') if dirs else []

    # When tests for our IDA plugin are disabled, we have to exclude their
    # directory so they are not discovered by automatic test discovery.
    if not config['runner'].getboolean('idaplugin_tests_enabled'):
        dir_paths.append(os.path.join('tools', 'idaplugin'))

    excluded_dirs = [tests_root_dir.get_dir(path) for path in dir_paths]
    return excluded_dirs


def get_test_cases_to_run(tests_dir, tests_root_dir, excluded_dirs, config, args):
    """Returns test cases to be run."""
    return find_tests(
        tests_dir,
        tests_root_dir,
        config['runner']['test_file'],
        excluded_dirs,
        only_critical=args.only_critical,
        only_for_tool=args.tool,
        only_matching=args.regexp
    )


def initialize_worker(mp_lock):
    """Initializes a worker that runs test cases."""
    # The lock has to be made global through an initialization function when
    # creating mp.Pool(). Otherwise, interpreter instances on Windows would not
    # share a single lock but each interpreter would create its own lock. This
    # would cause race conditions when emitting output or accessing the
    # database.
    # Based on http://stackoverflow.com/a/28721419/2580955.
    global lock
    lock = mp_lock

    # Block SIGINT in the workers so that Ctrl+C kills only the main process.
    # It then terminates the workers. Otherwise, stack traces from all workers
    # would be printed to the standard error when Ctrl+C is used.
    # Based on http://stackoverflow.com/a/11312948/2580955.
    signal.signal(signal.SIGINT, signal.SIG_IGN)


def ordered_indexes(test_cases):
    """Returns a list of indexes of the given test cases to run.

    The list is ordered in a way to make the regression tests run as fast as
    possible (when running in parallel).
    """
    # We want long-running tests to start first and short-running tests to
    # start last. In this way, the regression tests will run as fast as
    # possible (provided that they run in parallel, not sequentially).
    #
    # We use a heuristic approach by running first tests that are known to be
    # long-running. Then, we run other tests.
    #
    # An alternative (and better) approach would be to consult the database to
    # find out the precise running time of tests from the previous commit.

    def format_num_prefix(n):
        return str(n).zfill(2)

    def test_case_key(i):
        # Run tests in this order:
        order_prefixes = [
            'tools.idaplugin.vawtrak.TestDecompileAll',
            'bugs',
            'features',
            'samples',
            'integration',
            'tools.idaplugin',
            # Other.
        ]
        test_name = test_cases[i].full_name
        for n, prefix in enumerate(order_prefixes):
            if test_name.startswith(prefix):
                return format_num_prefix(n) + test_name
        return format_num_prefix(len(order_prefixes)) + test_name

    return sorted(range(len(test_cases)), key=test_case_key)


def run_test_cases(test_cases, tested_commit, procs, resume, lock):
    """Runs the given test cases and returns a list of results."""
    # Properly handle Ctrl+C (KeyboardInterrupt).
    # Based on http://stackoverflow.com/a/11312948/2580955.
    pool = mp.Pool(
        processes=procs,
        initializer=initialize_worker,
        initargs=(lock,)
    )
    try:
        run_test_case_on_index_args = [
            (i, tested_commit, resume) for i in ordered_indexes(test_cases)
        ]
        test_results = TestsResults(
            pool.starmap(
                run_test_case_on_index,
                run_test_case_on_index_args,
                # Send tasks to processes one by one instead of sending them a
                # chunk of tasks at once. This speeds up the regression tests.
                # By default, the chunk size is `len(tasks) / processors`, so
                # it may happen that a single process gets many long-running
                # tasks. We don't want that. Instead, by sending them a single
                # task at once, all processors are utilized during the whole
                # duration of the regression tests.
                chunksize=1
            )
        )
        pool.close()
        pool.join()
        return test_results
    except KeyboardInterrupt:
        pool.terminate()
        pool.join()
        sys.exit(1)


def run_test_case_on_index(i, tested_commit, with_resume):
    """Runs a test case on the given index for the given tested commit."""
    global cmd_runner
    global db
    global lock
    global stop_testing
    global test_cases
    global tools_dir

    test_case = test_cases[i]

    # Should we stop testing? See install_stop_testing_handler() for more
    # details.
    if stop_testing:
        return NoTestResults(test_case.module_name, test_case.name)

    # Check whether the test case should run. We only need to consult the
    # database if resume is requested, i.e. when only running tests that have
    # not run yet.
    test_case_should_run = True
    if with_resume:
        with lock:
            test_case_should_run = not db.has_test_run_for_commit(
                test_case.module_name, test_case.name, tested_commit)

    if test_case_should_run:
        tool_runner = test_case.test_settings.get_tool_runner(
            cmd_runner,
            tools_dir
        )
        test_results = run_test_case(test_case, tool_runner)
        with lock:
            db.insert_test_results(test_results, tested_commit)
            print_test_results(test_results)
    else:
        test_results = NoTestResults(test_case.module_name, test_case.name)
    return test_results


def run_test_case(test_case, tool_runner):
    """Runs the tests in the given test case by using the given runner."""
    # Initialize timing.
    start_date = datetime.now()

    try:
        # Run the tool.
        tool = tool_runner.run_tool(
            test_case.tool,
            test_case.tool_arguments,
            test_case.tool_dir,
            test_case.tool_timeout
        )

        # Run the tests with redirected output.
        test_suite = test_case.create_test_suite(tool)
        test_output = io.StringIO()
        test_runner = unittest.TextTestRunner(stream=test_output)
        test_result = test_runner.run(test_suite)
    except Exception:
        # Create a faked test result to allow uniform construction of
        # TestResults at the end of this function.
        test_output = io.StringIO(traceback.format_exc())
        test_result = unittest.TestResult()
        # unittest.TestResult() does not allow us to set the following
        # attributes during construction, so we have to set them afterwards.
        test_result.testsRun = 1
        test_result.errors = [object()]  # Only the length is important.
        test_result.failures = []

    # Finish timing.
    end_date = datetime.now()

    # Create the results.
    return TestResults(
        test_case.module_name,
        test_case.name,
        start_date,
        end_date,
        test_result.testsRun,
        len(test_result.errors) + len(test_result.failures),
        test_output.getvalue(),
        test_case.is_critical()
    )


def send_email_for_commit_if_needed(config, db, commit):
    """Sends an email for the given commit, depending on several conditions.
    """
    if not config['email'].getboolean('enabled'):
        # Sending of emails is disabled.
        return

    if db.email_sent_for_commit(commit):
        # The email has already been sent.
        return

    commit_results = db.get_results_for_commit(commit)
    if (not commit_results.build_has_failed() and
            not commit_results.has_failed_tests()):
        # There is nothing to report.
        return

    if db.topmost_commit_has_succeeded():
        # There is no need to send the email if the topmost commit has
        # succeeded.
        return

    email = prepare_email(
        commit_results,
        config['email']['subject_prefix'],
        config['web']['main_page_url'],
        config['web']['wiki_page_url']
    )

    # Set proper addresses.
    def set_addr_if_defined(addr_type):
        addr_name = '{}_addr'.format(addr_type)
        addr = config['email'][addr_name]
        if addr:
            setattr(email, addr_name, addr)
    set_addr_if_defined('from')
    set_addr_if_defined('to')
    set_addr_if_defined('reply_to')
    set_addr_if_defined('cc')

    # Send the email.
    logging.info("sending email to '{}' concerning commit {}".format(
        email.to_addr, commit.short_hash()))
    send_email(
        email,
        config['email']['smtp_server'],
        config['email']['smtp_port'],
        config['email']['smtp_user'],
        config['email']['smtp_pass']
    )
    db.insert_email_for_commit(email, commit)


def install_stop_testing_handler():
    """Installs a handler for the "stop testing" signal.

    When this signal is received, the testing should stop and the script should
    exit. This is marked by setting the ``stop_testing`` global variable to
    ``True``.
    """
    # The used signal is SIGCONT. This particular signal was chosen because it
    # does not terminate applications without an explicit signal handler, such
    # as our scripts and tools.
    def sigcont_handler(signum, frame):
        global stop_testing
        if stop_testing is not True:
            stop_testing = True

    global stop_testing
    stop_testing = False
    signal.signal(signal.SIGCONT, sigcont_handler)


def request_username_for_repo(repo_url):
    """Requests a username for the given repository and returns a new URL,
    containing the username.
    """
    username = input('Enter username for {}: '.format(repo_url))
    return add_username(username.strip(), repo_url)


try:
    ensure_is_run_from_script_dir()

    # Config.
    config = parse_standard_config_files()
    ensure_all_required_settings_are_set(config)

    # Logging.
    setup_logging(config, os.path.basename(__file__))
    # Only log the start of the main process.
    if __name__ == '__main__':
        logging.info('script started (`' + ' '.join(sys.argv) + '`)')

    # Setup Clang bindings.
    setup_clang_bindings(config['runner']['clang_dir'])

    # Arguments.
    args = parse_args()

    # Support for stopping the tests. The stop_testing below needs to be global
    # because it is used in a signal handler.
    stop_testing = False
    if args.support_stop:
        install_stop_testing_handler()

    # Quality of Service.
    qos_enabled = config.getboolean('qos', 'enabled')
    qos_max_tries = int(config['qos']['max_tries'])
    qos_wait_time = int(config['qos']['wait_time'])

    # Database.
    db = DB(config['db']['conn_url'])
    if qos_enabled:
        db = WithQoS(db, qos_max_tries, qos_wait_time)

    # Command runner.
    cmd_runner = CmdRunner()
    tools_dir = Directory(os.path.join(config['runner']['retdec_install_dir'], 'bin'))

    # Adjustment of the environment (e.g. update of PATH).
    adjust_environment(config)

    # Tests.

    # We need a lock due to parallel access (1) to the database and (2)
    # to the filesystem to prevent mixed text on the standard output.
    lock = mp.Lock()

    # Directories.
    tests_root_dir = Directory(config['runner']['tests_root_dir'])
    tests_dir = get_tests_dir(args.tests_dir, tests_root_dir)
    excluded_dirs = get_excluded_dirs(tests_root_dir, config)

    # Workers (spawned processes by the multiprocessing module) need access to
    # the test cases, so get them. They need to be stored in a global variable.
    # The main process gets them after a checkout of the appropriate commit
    # from the repository.
    if __name__ != '__main__':
        test_cases = get_test_cases_to_run(
            tests_dir,
            tests_root_dir,
            excluded_dirs,
            config,
            args
        )

    if __name__ == '__main__':
        # The main process.

        # Repository.
        repo = Repository(config['runner']['retdec_repo_dir'], cmd_runner)
        if qos_enabled:
            repo = WithQoS(repo, qos_max_tries, qos_wait_time)

        # Tested commit.
        if args.commit is not None:
            repo.update()
            tested_commit = repo.get_commit_from_hash(args.commit)
        else:
            tested_commit = repo.get_current_commit()
        db.initialize_commit_records(
            tested_commit,
            # When the user does not want to re-run tests that have already run
            # (i.e. he or she wants to resume the execution), do not remove
            # existing test results and sent emails from the database.
            remove_test_results=not args.resume,
            remove_emails=not args.resume
        )

        with repo.checkout(tested_commit):
            # RetDec build.
            if args.build:
                run_retdec_build(config, db, cmd_runner, tested_commit)

            remove_results_from_previous_test_runs(tests_dir)

            # Find tests.
            test_cases = get_test_cases_to_run(
                tests_dir,
                tests_root_dir,
                excluded_dirs,
                config,
                args
            )
            if not test_cases:
                relative_excluded_dirs = ', '.join(
                    os.path.relpath(dir.path, tests_root_dir.path) for dir in excluded_dirs
                )
                print_error('no {}tests found in {} (excluded directories: {})'.format(
                    'critical ' if args.only_critical else '', tests_dir.path,
                    relative_excluded_dirs))
                sys.exit(1)

            # Run them.
            print_prologue(tests_dir.path, test_cases, tested_commit, args.resume)
            tests_results = run_test_cases(
                test_cases,
                tested_commit,
                procs=get_num_of_procs_for_tests(config),
                resume=args.resume,
                lock=lock
            )
            print_summary(tests_results)

            # Send notifications (if needed).
            if not stop_testing:
                send_email_for_commit_if_needed(config, db, tested_commit)

        sys.exit(0)
except Exception:
    logging.exception('unhandled exception')
    raise
