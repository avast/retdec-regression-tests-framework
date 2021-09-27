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
from regression_tests.filesystem.directory import Directory
from regression_tests.io import print_error
from regression_tests.io import print_prologue
from regression_tests.io import print_summary
from regression_tests.io import print_test_results
from regression_tests.logging import setup_logging
from regression_tests.test_finder import find_tests
from regression_tests.test_finder import get_tests_dir
from regression_tests.test_results import TestResults
from regression_tests.test_results import TestsResults
from regression_tests.test_settings import TestSettings


def parse_args():
    """Parses command-line arguments and returns them."""
    parser = argparse.ArgumentParser(description='Runner of regression tests.')
    parser.add_argument('tests_dir', type=str, metavar='PATH', nargs='?',
                        help='Explicit path to the tests.')
    parser.add_argument('-r', '--regexp', type=str, metavar='REGEXP', dest='regexp',
                        help='Run only tests matching the given regular expression.')
    parser.add_argument('-t', '--tool', type=str, metavar='TOOL', dest='tool',
                        help='Run only tests for the given tool.')
    parser.add_argument('--skip-c-compilation-tests', action='store_true',
                        dest='skip_c_compilation_tests',
                        help='Skip tests that compile the output C source code.')
    args = parser.parse_args()

    return args


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
    elif not (os.path.exists(os.path.join(retdec_install_dir, 'bin', 'retdec-decompiler')) or
              os.path.exists(os.path.join(retdec_install_dir, 'bin', 'retdec-decompiler.exe'))):
        print_error("'retdec_install_dir' in the [runner] section of config_local.ini "
                    "does not seem to point to RetDec")
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

    if config['runner'].getboolean('r2plugin_tests_enabled'):
        # [runner] -> r2plugin_script
        r2plugin_script = config['runner']['r2plugin_script']
        if not r2plugin_script:
            print_error("no 'r2plugin_script' in the [runner] section of config_local.ini "
                        "(you have to add it to run tests for our IDA plugin)")
            sys.exit(1)
        elif not os.path.exists(r2plugin_script):
            print_error("'r2plugin_script' in the [runner] section of config_local.ini "
                        "points to a non-existing file")
            sys.exit(1)


def adjust_environment(config, args):
    """Adjusts the environment so that the regression tests may run (e.g.
    update PATH).
    """
    if config['runner'].getboolean('idaplugin_tests_enabled'):
        tools_dir = os.path.join(config['runner']['retdec_install_dir'], 'bin')

        # run-ida-decompilation.py requires retdec-decompiler to be reachable from PATH.
        os.environ['PATH'] = tools_dir + os.pathsep + os.environ['PATH']

        # run-ida-decompilation.py requires path to IDA Pro.
        os.environ['IDA_DIR'] = config['runner']['idaplugin_ida_dir']

        # Copy run-ida-decompilation.py into the directory where other tools
        # are located so it can be found. However, do this only when runner.py
        # is run (not for spawned processes to prevent multiple processes from
        # overwriting the same file).
        if __name__ == '__main__':
            target_script_path = os.path.join(tools_dir, 'run-ida-decompilation.py')
            shutil.copyfile(config['runner']['idaplugin_script'], target_script_path)
            # We also need to ensure that the copied file is executable by the
            # current user.
            os.chmod(
                target_script_path,
                os.stat(target_script_path).st_mode | stat.S_IXUSR
            )

    if config['runner'].getboolean('r2plugin_tests_enabled'):
        tools_dir = os.path.join(config['runner']['retdec_install_dir'], 'bin')

        # run-r2-decompilation.py requires retdec-decompiler to be reachable from PATH.
        os.environ['PATH'] = tools_dir + os.pathsep + os.environ['PATH']

        # Copy run-r2-decompilation.py into the directory where other tools
        # are located so it can be found. However, do this only when runner.py
        # is run (not for spawned processes to prevent multiple processes from
        # overwriting the same file).
        if __name__ == '__main__':
            target_script_path = os.path.join(tools_dir, 'run-r2-decompilation.py')
            shutil.copyfile(config['runner']['r2plugin_script'], target_script_path)
            # We also need to ensure that the copied file is executable by the
            # current user.
            os.chmod(
                target_script_path,
                os.stat(target_script_path).st_mode | stat.S_IXUSR
            )

    # We have to provide path to our supportive scripts (e.g.
    # regression_tests.tools.decompiler_test.DecompilerTest._get_compiler_for_out_c()
    # relies on windows-gcc-32.sh being in PATH).
    root_path = os.path.dirname(__file__)
    scripts_dir = os.path.join(root_path, 'support', 'scripts')
    os.environ['PATH'] = scripts_dir + os.pathsep + os.environ['PATH']

    # We use environment variables to send configuration to tests as there is
    # currently no better way.
    if should_skip_c_compilation_tests(config, args):
        os.environ['RETDEC_TESTS_SKIP_C_COMPILATION_TESTS'] = '1'


def should_skip_c_compilation_tests(config, args):
    """Should we skip tests that want to compile output C file?"""
    return args.skip_c_compilation_tests or \
        config['runner'].getboolean('skip_c_compilation_tests')


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

    # When tests for r2 plugin are disabled, we have to exclude their
    # directory so they are not discovered by automatic test discovery.
    if not config['runner'].getboolean('r2plugin_tests_enabled'):
        dir_paths.append(os.path.join('tools', 'r2plugin'))

    excluded_dirs = [tests_root_dir.get_dir(path) for path in dir_paths]
    return excluded_dirs


def get_test_cases_to_run(tests_dir, tests_root_dir, excluded_dirs, config, args):
    """Returns test cases to be run."""
    return find_tests(
        tests_dir,
        tests_root_dir,
        config['runner']['test_file'],
        excluded_dirs,
        only_for_tool=args.tool,
        only_matching=args.regexp
    )


def initialize_worker(mp_lock):
    """Initializes a worker that runs test cases."""
    # The lock has to be made global through an initialization function when
    # creating mp.Pool(). Otherwise, interpreter instances on Windows would not
    # share a single lock but each interpreter would create its own lock. This
    # would cause race conditions when emitting output.
    # Based on http://stackoverflow.com/a/28721419.
    global lock
    lock = mp_lock

    # Block SIGINT in the workers so that Ctrl+C kills only the main process.
    # It then terminates the workers. Otherwise, stack traces from all workers
    # would be printed to the standard error when Ctrl+C is used.
    # Based on http://stackoverflow.com/a/11312948.
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


def run_test_cases(test_cases, procs, lock):
    """Runs the given test cases and returns a list of results."""
    pool = mp.Pool(
        processes=procs,
        initializer=initialize_worker,
        initargs=(lock,)
    )

    # Ensure that when the runner (= main process) is killed (either via Ctrl-C
    # or SIGTERM), it terminates all the workers in the pool so they can
    # terminate their subprocesses.
    def handler(signum, frame):
        pool.terminate()
        pool.join()
        sys.exit(1)
    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGTERM, handler)

    try:
        run_test_case_on_index_args = ordered_indexes(test_cases)
        test_results = TestsResults(
            pool.map(
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
        return test_results
    finally:
        pool.close()
        pool.join()


def run_test_case_on_index(i):
    """Runs a test case on the given index."""
    global cmd_runner
    global lock
    global test_cases
    global tools_dir

    test_case = test_cases[i]

    tool_runner = test_case.test_settings.get_tool_runner(
        cmd_runner,
        tools_dir
    )
    test_results = run_test_case(test_case, tool_runner)
    with lock:
        print_test_results(test_results)
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
        test_result.skipped = []

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
        len(test_result.skipped),
        test_output.getvalue(),
    )


try:
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

    # Command runner.
    cmd_runner = CmdRunner()
    tools_dir = Directory(os.path.join(config['runner']['retdec_install_dir'], 'bin'))

    # Adjustment of the environment (e.g. update of PATH).
    adjust_environment(config, args)

    # Tests.

    # We need a lock due to prevent mixed text on the standard output.
    lock = mp.Lock()

    # Directories.
    tests_root_dir = Directory(config['runner']['tests_root_dir'])
    tests_dir = get_tests_dir(args.tests_dir, tests_root_dir)
    excluded_dirs = get_excluded_dirs(tests_root_dir, config)

    # Workers (spawned processes by the multiprocessing module) need access to
    # the test cases, so get them. They need to be stored in a global variable.
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
            print_error('no tests found in {} (excluded directories: {})'.format(
                tests_dir.path,
                relative_excluded_dirs,
            ))
            sys.exit(1)

        # Run them.
        print_prologue(tests_dir.path, test_cases)
        tests_results = run_test_cases(
            test_cases,
            procs=get_num_of_procs_for_tests(config),
            lock=lock
        )
        print_summary(tests_results)

        sys.exit(0 if tests_results.succeeded else 1)
except Exception:
    logging.exception('unhandled exception')
    raise
