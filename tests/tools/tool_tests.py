"""
    Tests for the :mod:`regression_tests.tools.tool` module.
"""

import os
import unittest
from unittest import mock

from regression_tests.cmd_runner import CmdRunner
from regression_tests.filesystem.directory import Directory
from regression_tests.filesystem.file import File
from regression_tests.filesystem.file import StandaloneFile
from regression_tests.parsers.text_parser import Text
from regression_tests.tools.tool import Tool
from regression_tests.tools.tool_arguments import ToolArguments


class ToolTestsBase(unittest.TestCase):
    """A base class for all tool tests."""

    def setUp(self):
        self.name = 'tool'
        self.dir = mock.Mock(spec_set=Directory)
        type(self.dir).path = mock.PropertyMock(return_value='/test/outputs/tool')
        self.cmd_runner = mock.Mock(spec_set=CmdRunner)
        self.args = ToolArguments(
            input_files=(File('file.exe', Directory('/test')),)
        )
        self.output = 'output'
        self.return_code = 0
        self.timeouted = False

    def create_tool(self, cls=Tool, **kwargs):
        """Creates a tool of the given class with the given arguments."""
        kwargs.setdefault('name', self.name)
        kwargs.setdefault('dir', self.dir)
        kwargs.setdefault('args', self.args)
        kwargs.setdefault('cmd_runner', self.cmd_runner)
        kwargs.setdefault('output', self.output)
        kwargs.setdefault('return_code', self.return_code)
        kwargs.setdefault('timeouted', self.timeouted)
        return cls(**kwargs)

    def set_tool_log(self, log):
        """Sets the given log for the tool."""
        file = mock.Mock(spec_set=File)
        type(file).text = mock.PropertyMock(return_value=log)
        self.dir.get_file.return_value = file


class ToolTests(ToolTestsBase):
    """Tests for `Tool`."""

    def setUp(self):
        super().setUp()
        self.tool = self.create_tool()

    def test_name_returns_correct_value(self):
        self.assertEqual(self.tool.name, self.name)

    def test_name_cannot_be_changed(self):
        with self.assertRaises(AttributeError):
            self.tool.name = 'other tool'

    def assert_safe_name_returns(self, tool_name, expected_safe_name):
        tool = self.create_tool(name=tool_name)
        self.assertEqual(tool.safe_name, expected_safe_name)

    def test_safe_name_returns_name_when_name_is_already_safe(self):
        self.assert_safe_name_returns('Tool', 'Tool')

    def test_safe_name_replaces_invalid_characters_with_underscores(self):
        self.assert_safe_name_returns('test me.py', 'test_me_py')

    def test_safe_name_ensures_that_name_starts_with_letter_or_undesrscore(self):
        self.assert_safe_name_returns('9tool', '_9tool')

    def test_safe_name_ensures_that_name_is_not_empty(self):
        self.assert_safe_name_returns('', '_')

    def test_dir_returns_correct_value(self):
        self.assertEqual(self.tool.dir, self.dir)

    def test_dir_cannot_be_changed(self):
        with self.assertRaises(AttributeError):
            self.tool.dir = Directory('/other/test')

    def test_args_returns_correct_value(self):
        self.assertEqual(self.tool.args, self.args)

    def test_args_cannot_be_changed(self):
        with self.assertRaises(AttributeError):
            self.tool.args = ToolArguments(
                input_files=(File('other_file.exe', Directory('/test')),)
            )

    def test_output_returns_correct_value(self):
        self.assertEqual(self.tool.output, self.output)

    def test_output_is_text(self):
        self.assertIsInstance(self.tool.output, Text)

    def test_output_cannot_be_changed(self):
        with self.assertRaises(AttributeError):
            self.tool.output = 'new output'

    def test_end_of_output_returns_last_x_lines_from_output(self):
        self.tool = self.create_tool(
            output='line1\nline2\nline3'
        )
        self.assertEqual(self.tool.end_of_output(2), 'line2\nline3')

    def test_return_code_returns_correct_value(self):
        self.assertEqual(self.tool.return_code, self.return_code)

    def test_return_code_cannot_be_changed(self):
        with self.assertRaises(AttributeError):
            self.tool.return_code = 1

    def test_succeeded_returns_true_if_return_code_is_zero(self):
        self.tool = self.create_tool(
            return_code=0
        )
        self.assertTrue(self.tool.succeeded)

    def test_succeeded_returns_false_if_return_code_is_nonzero(self):
        self.tool = self.create_tool(
            return_code=1
        )
        self.assertFalse(self.tool.succeeded)

    def test_failed_returns_true_if_return_code_is_nonzero(self):
        self.tool = self.create_tool(
            return_code=1
        )
        self.assertTrue(self.tool.failed)

    def test_failed_returns_false_if_return_code_is_zero(self):
        self.tool = self.create_tool(
            return_code=0
        )
        self.assertFalse(self.tool.failed)

    def test_timeouted_returns_correct_value(self):
        self.assertEqual(self.tool.timeouted, self.timeouted)

    def test_timeouted_cannot_be_changed(self):
        with self.assertRaises(AttributeError):
            self.tool.timeouted = True

    def test_input_files_returns_correct_value(self):
        self.assertEqual(self.tool.input_files, self.args.input_files)

    def test_log_file_name_returns_correct_name_when_there_is_single_input_file(self):
        self.assertEqual(self.tool.log_file_name, self.args.input_files[0].name + '.log')

    def test_log_file_name_returns_correct_name_when_there_is_no_input_file(self):
        self.tool = self.create_tool(
            name='tool',
            args=ToolArguments()
        )
        self.assertEqual(self.tool.log_file_name, 'tool.log')

    def test_log_file_name_returns_correct_name_when_there_are_two_input_files(self):
        self.tool = self.create_tool(
            name='tool',
            args=ToolArguments(
                input_files=(StandaloneFile('file1.exe'), StandaloneFile('file2.exe'))
            )
        )
        self.assertEqual(self.tool.log_file_name, 'tool.log')

    def test_log_file_returns_file_with_correct_path(self):
        self.dir.get_file.return_value = File(self.tool.log_file_name, self.dir)
        self.assertEqual(
            self.tool.log_file.path,
            os.path.join(self.dir.path, self.tool.log_file_name)
        )

    def test_log_returns_contents_of_log_file(self):
        LOG = 'contents of the log file'
        self.set_tool_log(LOG)
        self.assertEqual(self.tool.log, LOG)

    def test_end_of_log_returns_last_x_lines_from_log(self):
        self.set_tool_log('line1\nline2\nline3')
        self.assertEqual(self.tool.end_of_log(2), 'line2\nline3')

    def test_run_cmd_passes_arguments_to_cmd_runner_and_returns_its_result(self):
        CMD = ['ls', '-l']
        TIMEOUT = 5
        result = self.tool._run_cmd(CMD, timeout=TIMEOUT)
        self.assertEqual(result, self.cmd_runner.run_cmd.return_value)
        self.cmd_runner.run_cmd.assert_called_once_with(CMD, timeout=TIMEOUT)
