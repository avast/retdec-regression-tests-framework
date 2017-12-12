"""
    Tests for the :mod:`regression_tests.tools.decompilation_runner` module.
"""

import unittest
from unittest import mock

from regression_tests.cmd_runner import CmdRunner
from regression_tests.filesystem.file import File
from regression_tests.tools.decompilation import Decompilation
from regression_tests.tools.decompilation_arguments import DecompilationArguments
from regression_tests.tools.decompilation_runner import DecompilationRunner
from regression_tests.tools.tool_test_settings import ToolTestSettings


class DecompilationRunnerTests(unittest.TestCase):
    """Tests for `DecompilationRunner()`."""

    def setUp(self):
        self.cmd_runner = mock.Mock(spec_set=CmdRunner)
        self.tools_dir = mock.Mock()
        self.test_settings = mock.Mock(spec_set=ToolTestSettings)
        self.decomp_runner = DecompilationRunner(
            self.cmd_runner,
            self.tools_dir,
            self.test_settings
        )

    def test_tool_class_returns_decompilation(self):
        self.assertIs(self.decomp_runner._tool_class, Decompilation)

    def test_initialize_tool_dir_and_args_just_returns_args_when_config_file_is_not_set(self):
        input_dir = mock.Mock()
        tool_dir = mock.Mock()
        args = DecompilationArguments(
            input_files=(File('file.exe', input_dir),)
        )

        new_args = self.decomp_runner._initialize_tool_dir_and_args(
            tool_dir, args
        )

        self.assertIs(new_args, args)

    def test_initialize_tool_dir_and_args_copies_config_file_when_it_is_set(self):
        input_dir = mock.Mock()
        tool_dir = mock.Mock()
        tool_dir.copy_file.return_value = File('file.json', tool_dir)
        args = DecompilationArguments(
            input_files=(File('file.exe', input_dir),),
            config_file=File('file.json', input_dir)
        )

        new_args = self.decomp_runner._initialize_tool_dir_and_args(
            tool_dir, args
        )

        tool_dir.copy_file.assert_called_once_with(args.config_file)
        self.assertEqual(new_args.config_file.dir, tool_dir)
