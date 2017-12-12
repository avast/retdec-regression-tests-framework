"""
    Finding of regression tests.
"""

import os


from regression_tests.filesystem.directory import Directory
from regression_tests.test_module import TestModule
from regression_tests.test_settings import TestSettings


def get_tests_dir(tests_dir_path, tests_root_dir):
    """Returns the base directory from which (and its subdirectories) tests
    should be run.

    :param str tests_dir_path: Path to the directory with the tests to be run
                               (can be ``None``).
    :param Directory tests_root_dir: Root directory of the tests.
    """
    if tests_dir_path is None:
        # No explicit path was given, so use the root directory.
        return tests_root_dir

    if os.path.isabs(tests_dir_path):
        # And absolute path to a directory was given.
        return Directory(tests_dir_path)

    # Try replacing dots with path separators. This allows users to use e.g.
    # "integration.factorial" instead of "integration/factorial".
    replaced_tests_dir_path = tests_dir_path.replace('.', os.path.sep)
    if tests_root_dir.dir_exists(replaced_tests_dir_path):
        return tests_root_dir.get_dir(replaced_tests_dir_path)

    # No luck, so just consider tests_dir_path to be relative to
    # tests_root_dir.
    return tests_root_dir.get_dir(tests_dir_path)


def find_tests(dir, root_dir, test_file_name, excluded_dirs=None,
               only_critical=False, only_for_tool=None, only_matching=None):
    """Finds all tests in the given directory and subdirectories.

    :param Directory dir: Directory in which tests will be searched.
    :param Directory root_dir: Root directory of all the tests.
    :param str test_file_name: Name of the file containing test configuration.
    :param list excluded_dirs: A list of directories to be excluded from
                               searching.
    :param bool only_critical: Include only critical tests.
    :param str only_for_tool: When given, include only tests for the given
                              tool.
    :param str only_matching: When given, include only tests matching the given
                              regular expression.

    :returns: A list of all the found tests (instances of :class:`.TestCase`).
    """
    tests = []
    for curr_dir, _, files in dir.walk():
        if _should_be_excluded_from_searching(curr_dir, excluded_dirs):
            continue
        for file in files:
            if file.name == test_file_name:
                test_module = TestModule(file, root_dir)
                for test_case in test_module.test_cases(
                        only_critical, only_for_tool, only_matching):
                    tests.append(test_case)
    return tests


def _should_be_excluded_from_searching(dir, excluded_dirs):
    """Should the given directory be excluded from searching?"""
    # First, check for some generic directories that should be skipped.
    if dir.name in ['.git', '__pycache__', TestSettings.outputs_dir_name]:
        return True

    # Now, move on to check for user-specified directories to skip.
    excluded_dirs = excluded_dirs or []
    for excluded_dir in excluded_dirs:
        if dir.path.startswith(excluded_dir.path):
            return True
    return False
