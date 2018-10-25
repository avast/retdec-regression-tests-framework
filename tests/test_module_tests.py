"""
    Tests for the :mod:`regression_tests.test_module_tests` module.
"""

import contextlib
import os
import unittest

from regression_tests.filesystem.directory import Directory
from regression_tests.filesystem.file import File
from regression_tests.test_module import TestModule
from regression_tests.tools.decompiler_test import DecompilerTest
from regression_tests.tools.tool_test import ToolTest
from tests.utils import TemporaryFile


# We can only have one module source file for all the tests due to how Python
# caches the loaded modules. Maybe if we placed the test.py files in different
# directories, we would be able to overcome this limitation since the modules
# would have different names. However, for now, we have to satisfy with a
# single module.
MODULE_SRC = """
from regression_tests import *

import unittest

class NonTest1:
    pass

class NonTest2(unittest.TestCase):
    pass

class MyTest1(Test):
    settings = TestSettings(
        input='file1.exe',
        arch='x86'
    )

class MyTest2(Test):
    settings1 = TestSettings(
        input='file2.exe',
        arch='arm'
    )
    settings2 = TestSettings(
        input='file3.exe',
        arch='x86'
    )

# The following test is used to check that we can have settings for different
# tool in a single test.
class MyTest3(Test):
    # Settings for a generic tool (not decompiler).
    settings1 = TestSettings(
        tool='my tool'
    )

    # Settings for decompiler.
    settings2 = TestSettings(
        input='file2.exe'
    )

# The following test is used to check that the base class is correctly set even
# for tests that inherit from other tests, not directly from Test.
class FirstBaseTest(Test):
    pass
class SecondBaseTest(FirstBaseTest):
    pass
class MyTest4(SecondBaseTest):
    settings = TestSettings(
        input='file2.exe'
    )
"""


class TestModuleTests(unittest.TestCase):
    """Tests for `TestModule`."""

    def test_file_returns_correct_file(self):
        FILE = File('test.py', Directory('/tests/dir/subdir'))
        module = TestModule(FILE, '/tests')
        self.assertEqual(module.file, FILE)

    def test_root_dir_returns_correct_dir(self):
        ROOT_DIR = Directory('/tests')
        module = TestModule(
            File('test.py', Directory('/tests/dir/subdir')),
            ROOT_DIR
        )
        self.assertEqual(module.root_dir, ROOT_DIR)

    def test_dir_returns_correct_dir(self):
        MODULE_DIR = Directory('/tests/dir/subdir')
        module = TestModule(File('test.py', MODULE_DIR), Directory('/tests'))
        self.assertEqual(module.dir, MODULE_DIR)

    def test_name_returns_correct_name_when_there_is_package(self):
        module = TestModule(
            File('test.py', Directory('/tests/dir/subdir')),
            Directory('/tests')
        )
        self.assertEqual(module.name, 'dir.subdir')

    def test_name_returns_correct_name_when_there_is_no_package(self):
        module = TestModule(
            File('test.py', Directory('/tests')),
            Directory('/tests')
        )
        self.assertEqual(module.name, '')

    @contextlib.contextmanager
    def loaded_module(self):
        """A context manager returning a loaded module."""
        with TemporaryFile(MODULE_SRC) as f:
            f_dir = os.path.dirname(f.path)
            yield TestModule(
                File(f.path, Directory(f_dir)),
                Directory(f_dir)
            )

    def test_test_cases_returns_correct_number_of_cases_when_only_for_tool_is_given(self):
        with self.loaded_module() as module:
            test_cases = module.test_cases(only_for_tool='decompiler')
            self.assertEqual(len(test_cases), 5)

            test_cases = module.test_cases(only_for_tool='my tool')
            self.assertEqual(len(test_cases), 1)

    def test_test_cases_returns_correct_number_of_cases_when_only_matching_is_given(self):
        with self.loaded_module() as module:
            test_cases = module.test_cases(only_matching=r'file2.exe')
            self.assertEqual(len(test_cases), 3)

            test_cases = module.test_cases(only_matching=r'x86')
            self.assertEqual(len(test_cases), 2)

    def test_test_cases_returns_cases_with_test_classes_having_correct_base_class(self):
        with self.loaded_module() as module:
            test_cases = module.test_cases()
            for test_case in test_cases:
                first_base = test_case.test_class.__bases__[0]
                if test_case.test_class.__name__ in ['MyTest1', 'MyTest2']:
                    self.assertEqual(first_base, DecompilerTest)
                elif test_case.test_class.__name__ == 'MyTest4':
                    self.assertEqual(first_base, DecompilerTest)
                elif test_case.test_class.__name__ == 'MyTest3':
                    # This test has settings for both a generic tool and
                    # decompiler.
                    if test_case.test_settings.tool == 'my tool':
                        self.assertEqual(first_base, ToolTest)
                    else:
                        self.assertEqual(first_base, DecompilerTest)
