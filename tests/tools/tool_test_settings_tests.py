"""
    Tests for the :mod:`regression_tests.tools.tool_test_settings` module.
"""

import unittest
from unittest import mock

from regression_tests.test_settings import InvalidTestSettingsError
from regression_tests.test_settings import TestSettings
from regression_tests.tools.tool_arguments import ToolArguments
from regression_tests.tools.tool_runner import ToolRunner
from regression_tests.tools.tool_test import ToolTest
from regression_tests.tools.tool_test_settings import ToolTestSettings


class ToolTestSettingsTests(unittest.TestCase):
    """Tests for `ToolTestSettings`."""

    def test_test_settings_creates_tool_test_settings_when_custom_tool_is_specified(self):
        settings = TestSettings(tool='my tool')
        self.assertIsInstance(settings, ToolTestSettings)

    def test_tool_passed_to_constructor_is_accessible(self):
        TOOL = 'my tool'
        settings = ToolTestSettings(tool=TOOL)
        self.assertEqual(settings.tool, TOOL)

    def test_input_passed_to_constructor_is_accessible(self):
        INPUT = 'file.exe'
        settings = ToolTestSettings(tool='tool', input=INPUT)
        self.assertEqual(INPUT, settings.input)

    def test_exception_is_raised_when_empty_list_is_passed_as_input(self):
        with self.assertRaisesRegex(InvalidTestSettingsError, r'.*input.*empty.*'):
            ToolTestSettings(tool='tool', input=[])

    def test_input_as_list_returns_empty_list_if_input_is_not_set(self):
        settings = ToolTestSettings(tool='tool', input=None)
        self.assertEqual([], settings.input_as_list)

    def test_input_as_list_returns_input_when_input_is_list(self):
        INPUT = ['file1.exe', 'file2.exe']
        settings = ToolTestSettings(tool='tool', input=INPUT)
        self.assertEqual(INPUT, settings.input_as_list)

    def test_input_as_list_returns_list_when_input_is_single_file(self):
        INPUT = 'file.exe'
        settings = ToolTestSettings(tool='tool', input=INPUT)
        self.assertEqual([INPUT], settings.input_as_list)

    def test_input_as_list_returns_singleton_list_when_input_is_tuple(self):
        INPUT = ('file1.exe', 'file2.exe')
        settings = ToolTestSettings(tool='tool', input=INPUT)
        self.assertEqual([INPUT], settings.input_as_list)

    def test_has_multiple_inputs_returns_true_when_there_are_multiple_inputs(self):
        settings = ToolTestSettings(tool='tool', input=['file1.exe', 'file2.exe'])
        self.assertTrue(settings.has_multiple_inputs())

    def test_has_multiple_inputs_returns_false_when_there_is_just_single_input(self):
        settings = ToolTestSettings(tool='tool', input='file.exe')
        self.assertFalse(settings.has_multiple_inputs())

    def test_duplicate_inputs_are_merged(self):
        settings = ToolTestSettings(tool='tool', input=['file.exe', 'file.exe'])
        self.assertEqual(settings.input, 'file.exe')

        settings = ToolTestSettings(
            tool='tool',
            input=['file.exe', 'other.exe', 'file.exe']
        )
        self.assertEqual(settings.input, ['file.exe', 'other.exe'])

    def test_input_as_tuple_is_left_intact(self):
        settings = ToolTestSettings(tool='tool', input=('file.exe', 'file.exe'))
        self.assertEqual(settings.input, ('file.exe', 'file.exe'))

    def test_args_passed_to_constructor_is_accessible(self):
        ARGS = '--arg'
        settings = ToolTestSettings(tool='tool', args=ARGS)
        self.assertEqual(ARGS, settings.args)

    def test_exception_is_raised_when_empty_list_is_passed_as_args(self):
        with self.assertRaisesRegex(InvalidTestSettingsError, r'.*args.*empty.*'):
            ToolTestSettings(tool='tool', args=[])

    def test_args_as_list_returns_empty_list_if_args_is_not_set(self):
        settings = ToolTestSettings(tool='tool')
        self.assertEqual([], settings.args_as_list)

    def test_args_as_list_returns_args_when_args_is_list(self):
        ARGS = ['--arg1', '--arg2']
        settings = ToolTestSettings(tool='tool', args=ARGS)
        self.assertEqual(ARGS, settings.args_as_list)

    def test_args_as_list_returns_list_when_there_is_single_args(self):
        ARGS = '--arg'
        settings = ToolTestSettings(tool='tool', args=ARGS)
        self.assertEqual([ARGS], settings.args_as_list)

    def test_has_multiple_args_returns_true_when_there_are_multiple_args(self):
        settings = ToolTestSettings(tool='tool', args=['--arg1', '--arg2'])
        self.assertTrue(settings.has_multiple_args())

    def test_has_multiple_args_returns_false_when_there_is_just_single_args(self):
        settings = ToolTestSettings(tool='tool', args='--arg')
        self.assertFalse(settings.has_multiple_args())

    def test_duplicate_args_are_merged(self):
        settings = ToolTestSettings(tool='tool', args=['--arg', '--arg'])
        self.assertEqual(settings.args, '--arg')

        settings = ToolTestSettings(tool='tool', args=['--arg', '--other', '--arg'])
        self.assertEqual(settings.args, ['--arg', '--other'])

    def test_timeout_passed_to_constructor_is_accessible(self):
        TIMEOUT = 100
        settings = ToolTestSettings(tool='tool', timeout=TIMEOUT)
        self.assertEqual(settings.timeout, TIMEOUT)

    def test_tool_arguments_class_returns_correct_value(self):
        settings = ToolTestSettings(tool='tool')
        self.assertEqual(settings.tool_arguments_class, ToolArguments)

    def test_tool_arguments_returns_correct_value(self):
        ARGS = '-a -b'
        settings = ToolTestSettings(tool='tool', args=ARGS)

        tool_arguments = settings.tool_arguments

        self.assertEqual(tool_arguments.args, ARGS)

    def test_tool_runner_class_returns_correct_value(self):
        settings = ToolTestSettings(tool='tool')
        self.assertEqual(settings.tool_runner_class, ToolRunner)

    def test_get_runner_returns_tool_runner_with_given_arguments(self):
        settings = ToolTestSettings(tool='tool')
        cmd_runner = mock.Mock()
        tools_dir = mock.Mock()

        runner = settings.get_tool_runner(cmd_runner, tools_dir)

        self.assertIsInstance(runner, ToolRunner)

    def test_tool_test_class_returns_correct_value(self):
        settings = ToolTestSettings(tool='tool')
        self.assertEqual(settings.tool_test_class, ToolTest)
