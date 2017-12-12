"""
    Tests for the :mod:`regression_tests.tools.tool_runner` module.
"""

import os
import unittest
from unittest import mock

from regression_tests.cmd_runner import CmdRunner
from regression_tests.filesystem.directory import Directory
from regression_tests.filesystem.file import File
from regression_tests.tools.tool_arguments import ToolArguments
from regression_tests.tools.tool_runner import ToolRunner
from regression_tests.tools.tool_test_settings import ToolTestSettings


class ToolRunnerTests(unittest.TestCase):
    """Tests for `ToolRunner`."""

    def setUp(self):
        self.cmd_runner = mock.Mock(spec_set=CmdRunner)
        self.test_settings = mock.Mock(spec_set=ToolTestSettings)
        self.tool_name = 'tool'
        self.tool_output = 'output'
        self.tool_return_code = 0
        self.tool_timeout = 300
        self.tool_timeouted = False
        self.cmd_runner.run_cmd.return_value = (
            self.tool_output,
            self.tool_return_code,
            self.tool_timeouted
        )
        self.tools_dir = mock.Mock()
        self.tools_dir.path = '/path/to/retdec/bin'
        self.tool_runner = ToolRunner(
            self.cmd_runner,
            self.tools_dir,
            self.test_settings
        )
        self.tool_dir = mock.Mock()
        self.tool_dir.path = '/test/outputs/tool'
        self.tool_arguments = ToolArguments(
            input_files=(File('file.exe', Directory('/test')),)
        )

    def test_run_tool_erases_and_creates_tool_dir(self):
        self.tool_runner.run_tool(
            self.tool_name,
            self.tool_arguments,
            self.tool_dir,
            self.tool_timeout
        )

        self.tool_dir.create.assert_called_once_with(erase_if_exists=True)

    def test_run_tool_initializes_tool_dir_and_args(self):
        self.tool_runner._initialize_tool_dir_and_args = mock.Mock()
        self.tool_runner._initialize_tool_dir_and_args.return_value = self.tool_arguments

        self.tool_runner.run_tool(
            self.tool_name,
            self.tool_arguments,
            self.tool_dir,
            self.tool_timeout
        )

        self.tool_runner._initialize_tool_dir_and_args.assert_called_once_with(
            self.tool_dir,
            self.tool_arguments
        )

    def test_run_tool_runs_tool_with_correct_arguments(self):
        self.tool_runner.run_tool(
            self.tool_name,
            self.tool_arguments,
            self.tool_dir,
            self.tool_timeout
        )

        self.cmd_runner.run_cmd.assert_called_once_with(
            [os.path.join(self.tools_dir.path, self.tool_name)] + self.tool_arguments.as_list,
            strip_shell_colors=True,
            timeout=self.tool_timeout
        )

    def test_run_tool_stores_correct_log_to_correct_place(self):
        tool = self.tool_runner.run_tool(
            self.tool_name,
            self.tool_arguments,
            self.tool_dir,
            self.tool_timeout
        )

        expected_log = (
            '# Command: {}\n'.format(
                ' '.join(
                    [self.tool_name] + self.tool_arguments.without_paths_and_output_files.as_list
                )
            ) +
            '# Timeout: {} seconds\n'.format(self.tool_timeout) +
            '\n' +
            '{}\n'.format(self.tool_output) +
            '\n' +
            '# Return code: {}\n'.format(self.tool_return_code) +
            '# Timeouted:   {}\n'.format('yes' if self.tool_timeouted else 'no')
        )
        self.tool_dir.store_file.assert_called_once_with(
            tool.log_file_name,
            expected_log
        )

    def test_run_tool_returns_tool_with_correct_attributes(self):
        tool = self.tool_runner.run_tool(
            self.tool_name,
            self.tool_arguments,
            self.tool_dir,
            self.tool_timeout
        )

        self.assertEqual(tool.name, self.tool_name)
        self.assertEqual(tool.dir, self.tool_dir)
        self.assertEqual(tool.args, self.tool_arguments)
        self.assertEqual(tool.output, self.tool_output)
        self.assertEqual(tool.return_code, self.tool_return_code)
        self.assertEqual(tool.timeouted, self.tool_timeouted)
