"""
    Tests for the :mod:`regression_tests.test_case_name_tests` module.
"""

import unittest

from regression_tests.filesystem.file import StandaloneFile
from regression_tests.test_case import TestCaseName
from regression_tests.tools.tool_arguments import ToolArguments


class TestCaseNameTests(unittest.TestCase):
    """Tests for `TestCaseName`."""

    def test_class_name_returns_correct_value(self):
        name = TestCaseName(
            'Test (gcd.exe -a x86)'
        )
        self.assertEqual(name.class_name, 'Test')

    def test_input_files_returns_correct_value_when_there_is_single_input_file(self):
        name = TestCaseName(
            'Test (gcd.exe -a x86)'
        )
        self.assertEqual(name.input_files, 'gcd.exe')

    def test_input_files_returns_correct_value_when_there_is_single_input_file_with_dash(self):
        name = TestCaseName(
            'Test (my-file.exe -a x86)'
        )
        self.assertEqual(name.input_files, 'my-file.exe')

    def test_input_files_returns_correct_value_when_there_are_multiple_input_files(self):
        name = TestCaseName(
            'Test (file1.exe file2.exe -f json)'
        )
        self.assertEqual(name.input_files, 'file1.exe file2.exe')

    def test_input_files_returns_empty_string_if_there_are_no_input_files(self):
        name = TestCaseName(
            'Test (-v)'
        )
        self.assertEqual(name.input_files, '')

    def test_tool_args_returns_correct_value_when_only_input_file_is_given(self):
        name = TestCaseName('Test (gcd.exe)')
        self.assertEqual(name.tool_args, 'gcd.exe')

    def test_tool_args_returns_correct_value_when_additional_parameters_are_given(self):
        name = TestCaseName(
            'Test (gcd.exe -a x86)'
        )
        self.assertEqual(name.tool_args, 'gcd.exe -a x86')

    def test_tool_args_returns_empty_string_when_there_are_no_arguments_or_input_files(self):
        name = TestCaseName('Test ()')
        self.assertEqual(name.tool_args, '')

    def test_short_tool_args_returns_correct_value_when_shorter_than_limit(self):
        name = TestCaseName(
            'Test (gcd.exe -a x86)'
        )
        self.assertEqual(name.short_tool_args(200), 'gcd.exe -a x86')

    def test_short_tool_args_returns_correct_value_when_longer_than_limit(self):
        name = TestCaseName(
            'Test (gcd.exe -a x86)'
        )
        self.assertEqual(name.short_tool_args(10), 'gcd.ex[..]')

    def test_args_returns_correct_value_when_only_input_file_is_used(self):
        name = TestCaseName('Test (gcd.exe)')
        self.assertEqual(name.args, '')

    def test_args_returns_correct_value_when_additional_parameters_are_given(self):
        name = TestCaseName(
            'Test (gcd.exe -a x86)'
        )
        self.assertEqual(name.args, '-a x86')

    def test_args_returns_correct_value_when_there_are_multiple_input_files(self):
        name = TestCaseName('Test (gcd1.exe gcd2.exe)')
        self.assertEqual(name.args, '')

    def test_args_returns_correct_value_when_there_are_multiple_input_files_and_other_arguments(self):
        name = TestCaseName('Test (gcd1.exe gcd2.exe -f json)')
        self.assertEqual(name.args, '-f json')

    def test_args_returns_empty_string_when_there_are_no_arguments_or_input_files(self):
        name = TestCaseName('Test ()')
        self.assertEqual(name.args, '')

    def test_short_args_returns_correct_value_when_shorter_than_limit(self):
        name = TestCaseName(
            'Test (gcd.exe -a x86)'
        )
        self.assertEqual(name.short_args(200), '-a x86')

    def test_short_args_returns_correct_value_when_longer_than_limit(self):
        name = TestCaseName(
            'Test (gcd.exe -a x86)'
        )
        self.assertEqual(name.short_args(5), '-[..]')

    def test_with_short_args_returns_correct_value_when_shorter_than_limit(self):
        name = TestCaseName(
            'Test (gcd.exe -a x86)'
        )
        self.assertEqual(
            name.with_short_args(200),
            'Test (gcd.exe -a x86)'
        )

    def test_with_short_args_returns_correct_value_when_longer_than_limit(self):
        name = TestCaseName(
            'Test (gcd.exe -a x86)'
        )
        self.assertEqual(name.with_short_args(4), 'Test (gcd.exe [..])')

    def test_with_short_args_returns_correct_value_when_only_input_file_is_used(self):
        name = TestCaseName('Test (gcd.exe)')
        self.assertEqual(name.with_short_args(10), 'Test (gcd.exe)')

    def test_with_short_args_returns_correct_value_when_there_are_no_arguments_or_input_files(self):
        name = TestCaseName('Test ()')
        self.assertEqual(name.with_short_args(10), 'Test ()')

    def test_from_tool_arguments_returns_correct_test_case_name(self):
        name = TestCaseName.from_tool_arguments(
            test_name='Test',
            tool_arguments=ToolArguments(
                input_files=(StandaloneFile('gcd.exe'),),
                args='-a x86'
            )
        )
        self.assertEqual(name, 'Test (gcd.exe -a x86)')
