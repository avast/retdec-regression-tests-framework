"""
    Tests for the :mod:`regression_tests.test_case_tests` module.
"""

import os
import unittest
from unittest import mock

from regression_tests.filesystem.directory import Directory
from regression_tests.filesystem.file import File
from regression_tests.test import Test
from regression_tests.test_case import TestCase
from regression_tests.test_case import TestCaseName
from regression_tests.test_module import TestModule
from regression_tests.test_settings import CriticalTestSettings
from regression_tests.test_settings import TestSettings
from regression_tests.tools.tool_test_settings import ToolTestSettings
from regression_tests.utils.os import make_file_name_valid
from tests.filesystem.directory_tests import ROOT_DIR
from tests.matchers import Anything


class TestCaseTests(unittest.TestCase):
    """Tests for `TestCase`."""

    def setUp(self):
        self.test_module = TestModule(
            File('module.py', Directory(os.path.join(ROOT_DIR, 'tests', 'dir'))),
            Directory(os.path.join(ROOT_DIR, 'tests'))
        )
        self.test_class = Test
        self.test_settings = TestSettings(
            input='file.exe',
            arch='x86'
        )
        self.test_case = TestCase(
            self.test_module,
            self.test_class,
            self.test_settings
        )

    def test_test_module_returns_correct_value(self):
        self.assertEqual(self.test_case.test_module, self.test_module)

    def test_test_class_returns_correct_value(self):
        self.assertEqual(self.test_case.test_class, self.test_class)

    def test_test_settings_returns_correct_value(self):
        self.assertEqual(self.test_case.test_settings, self.test_settings)

    def test_name_returns_correct_value(self):
        self.assertEqual(self.test_case.name, 'Test (file.exe -a x86)')

    def test_name_returns_instance_of_TestCaseName(self):
        self.assertIsInstance(self.test_case.name, TestCaseName)

    def test_module_name_returns_correct_value(self):
        self.assertEqual(self.test_case.module_name, self.test_module.name)

    def test_full_name_returns_correct_value(self):
        self.assertEqual(self.test_case.full_name, 'dir.Test (file.exe -a x86)')

    def test_dir_returns_correct_value(self):
        self.assertEqual(self.test_case.dir, Directory(os.path.join(ROOT_DIR, 'tests', 'dir')))

    def test_tool_returns_correct_value(self):
        TOOL = 'tool'
        test_settings = TestSettings(
            tool=TOOL
        )
        test_case = TestCase(
            self.test_module,
            self.test_class,
            test_settings
        )
        self.assertEqual(test_case.tool, TOOL)

    def test_tool_arguments_returns_correct_value(self):
        tool_arguments = self.test_case.tool_arguments
        self.assertEqual(len(tool_arguments.input_files), 1)
        self.assertEqual(
            tool_arguments.input_files[0].path,
            os.path.join(ROOT_DIR, 'tests', 'dir', 'file.exe')
        )
        self.assertEqual(
            tool_arguments.output_file.path,
            os.path.join(ROOT_DIR, 'tests', 'dir', 'outputs',
                         'Test (file.exe -a x86)', 'file.c')
        )
        self.assertEqual(tool_arguments.arch, 'x86')

    def test_tool_dir_returns_correct_value(self):
        self.assertEqual(
            self.test_case.tool_dir,
            Directory(os.path.join(ROOT_DIR, 'tests', 'dir',
                                   'outputs', 'Test (file.exe -a x86)'))
        )

    def test_tool_dir_has_valid_file_name(self):
        test_settings = TestSettings(
            input='fi/le.exe',
            arch='x86'
        )
        test_case = TestCase(
            self.test_module,
            self.test_class,
            test_settings
        )
        self.assertEqual(
            test_case.tool_dir.name,
            make_file_name_valid(test_case.name)
        )

    @mock.patch('regression_tests.test_case.make_dir_name_valid')
    def test_tool_dir_calls_make_dir_name_valid_with_correct_arguments(
            self, make_dir_name_valid_mock):
        test_settings = TestSettings(
            input='file.exe'
        )
        test_case = TestCase(
            self.test_module,
            self.test_class,
            test_settings
        )
        make_dir_name_valid_mock.return_value = 'some_dir'  # Needed on Windows.

        test_case.tool_dir

        make_dir_name_valid_mock.assert_called_once_with(
            test_case.name,
            path_to_dir=os.path.join(ROOT_DIR, 'tests', 'dir', 'outputs'),
            max_nested_file_length=Anything()
        )

    @mock.patch('regression_tests.test_case.make_dir_name_valid')
    def test_tool_dir_calls_make_dir_name_valid_with_correct_arguments_when_there_is_no_input(
            self, make_dir_name_valid_mock):
        test_settings = ToolTestSettings(tool='my_tool')
        test_case = TestCase(
            self.test_module,
            self.test_class,
            test_settings
        )
        make_dir_name_valid_mock.return_value = 'some_dir'  # Needed on Windows.

        test_case.tool_dir

        make_dir_name_valid_mock.assert_called_once_with(
            test_case.name,
            path_to_dir=os.path.join(ROOT_DIR, 'tests', 'dir', 'outputs'),
            max_nested_file_length=0
        )

    def test_tool_timeout_returns_correct_value(self):
        test_settings = TestSettings(
            input='file.exe',
            timeout=250,
        )
        test_case = TestCase(
            self.test_module,
            self.test_class,
            test_settings
        )
        self.assertEqual(test_case.tool_timeout, 250)

    def test_is_critical_returns_true_when_settings_is_critical(self):
        test_case = TestCase(
            self.test_module,
            self.test_class,
            CriticalTestSettings(input='file.exe')
        )
        self.assertTrue(test_case.is_critical())

    def test_is_critical_returns_false_when_settings_is_not_critical(self):
        test_case = TestCase(
            self.test_module,
            self.test_class,
            TestSettings(input='file.exe')
        )
        self.assertFalse(test_case.is_critical())
