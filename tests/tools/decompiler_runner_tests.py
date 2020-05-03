"""
    Tests for the :mod:`regression_tests.tools.decompiler_runner` module.
"""

import unittest
from unittest import mock

from regression_tests.cmd_runner import CmdRunner
from regression_tests.filesystem.file import File
from regression_tests.tools.decompiler import Decompiler
from regression_tests.tools.decompiler_arguments import DecompilerArguments
from regression_tests.tools.decompiler_runner import DecompilerRunner
from regression_tests.tools.tool_test_settings import ToolTestSettings


class DecompilerRunnerTests(unittest.TestCase):
    """Tests for `DecompilerRunner()`."""

    def setUp(self):
        self.cmd_runner = mock.Mock(spec_set=CmdRunner)
        self.tools_dir = mock.Mock()
        self.test_settings = mock.Mock(spec_set=ToolTestSettings)
        self.decomp_runner = DecompilerRunner(
            self.cmd_runner,
            self.tools_dir,
            self.test_settings
        )

    def test_tool_class_returns_decompilation(self):
        self.assertIs(self.decomp_runner._tool_class, Decompiler)

    def test_get_tool_executable_name_returns_correct_name(self):
        self.assertEqual(
            self.decomp_runner._get_tool_executable_name('decompiler'),
            'retdec-decompiler'
        )

    def test_initialize_tool_dir_and_args_just_returns_args_when_config_file_is_not_set(self):
        input_dir = mock.Mock()
        tool_dir = mock.Mock()
        args = DecompilerArguments(
            input_files=(File('file.exe', input_dir),)
        )

        new_args = self.decomp_runner._initialize_tool_dir_and_args(
            tool_dir, args
        )

        self.assertIs(new_args, args)

    def test_initialize_tool_dir_and_args_copies_config_file_when_it_is_set(self):
        input_dir = mock.Mock()
        tool_dir = mock.Mock()
        tool_dir.copy_file.return_value = File('file.config.json', tool_dir)
        args = DecompilerArguments(
            input_files=(File('file.exe', input_dir),),
            config_file=File('file.config.json', input_dir)
        )

        new_args = self.decomp_runner._initialize_tool_dir_and_args(
            tool_dir, args
        )

        tool_dir.copy_file.assert_called_once_with(args.config_file)
        self.assertEqual(new_args.config_file.dir, tool_dir)
