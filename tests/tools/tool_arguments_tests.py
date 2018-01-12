"""
    Tests for the :mod:`regression_tests.tools.tool_arguments` module.
"""

import os
import unittest

from regression_tests.filesystem.directory import Directory
from regression_tests.filesystem.file import File
from regression_tests.filesystem.file import StandaloneFile
from regression_tests.test_settings import InvalidTestSettingsError
from regression_tests.tools.decompiler_arguments import DecompilerArguments
from regression_tests.tools.tool_arguments import ToolArguments
from regression_tests.tools.tool_test_settings import ToolTestSettings
from tests.filesystem.directory_tests import ROOT_DIR


class ToolArgumentsTests(unittest.TestCase):
    """Tests for `ToolArguments`."""

    def test_args_is_set_to_none_when_empty_args_are_passed(self):
        # When a user writes the following settings
        #
        #     args=''
        #
        # we want to consider it as
        #
        #     args=None
        #
        # Otherwise, the runner would pass an extra empty argument when running
        # the tool.
        args = ToolArguments(args='')
        self.assertIsNone(args.args)

    def test_as_list_returns_empty_list_when_nothing_is_set(self):
        args = ToolArguments()
        self.assertEqual(args.as_list, [])

    def test_as_list_returns_correct_list_when_just_input_file_is_set(self):
        args = ToolArguments(
            input_files=(StandaloneFile('file.exe'),)
        )
        self.assertEqual(args.as_list, ['file.exe'])

    def test_as_list_returns_correct_list_when_just_args_is_set(self):
        args = ToolArguments(
            args='  --arg1   --arg2  '
        )
        self.assertEqual(args.as_list, ['--arg1', '--arg2'])

    def test_as_str_returns_space_separated_string_of_arguments(self):
        args = ToolArguments(
            input_files=(StandaloneFile('file.exe'),),
            args='--arg1 --arg2'
        )
        self.assertEqual(args.as_str, 'file.exe --arg1 --arg2')

    def test_args_as_list_returns_empty_list_when_no_args(self):
        args = ToolArguments(
            args=None
        )
        self.assertEqual(args.args_as_list, [])

    def test_args_as_list_separates_args_by_whitespace(self):
        args = ToolArguments(
            args=' \t  --arg1    \t    --arg2  \t  '
        )
        self.assertEqual(args.args_as_list, ['--arg1', '--arg2'])

    def test_from_test_settings_input_files_are_present_when_single_input_is_given(self):
        test_settings = ToolTestSettings(tool='tool', input='test.exe')
        args = ToolArguments.from_test_settings(test_settings)
        self.assertEqual(len(args.input_files), 1)
        self.assertEqual(args.input_files[0].name, 'test.exe')

    def test_from_test_settings_input_files_are_present_when_two_inputs_are_given(self):
        test_settings = ToolTestSettings(tool='tool', input=('test1.exe', 'test2.exe'))
        args = ToolArguments.from_test_settings(test_settings)
        self.assertEqual(len(args.input_files), 2)
        self.assertEqual(args.input_files[0].name, 'test1.exe')
        self.assertEqual(args.input_files[1].name, 'test2.exe')

    def test_from_test_settings_input_files_is_empty_tuple_when_input_is_not_given(self):
        test_settings = ToolTestSettings(tool='tool')
        args = ToolArguments.from_test_settings(test_settings)
        self.assertEqual(args.input_files, ())

    def test_from_test_settings_args_is_present_when_set(self):
        test_settings = ToolTestSettings(
            tool='tool',
            input='test.exe',
            args='--arg1 --arg2'
        )
        args = ToolArguments.from_test_settings(test_settings)
        self.assertEqual(args.args, test_settings.args)

    def scenario_invalid_settings_error_is_raised(self, test_settings, ref_exc_substr):
        with self.assertRaises(InvalidTestSettingsError) as cm:
            ToolArguments.from_test_settings(test_settings)
        self.assertIn(ref_exc_substr, str(cm.exception))

    def test_from_test_settings_error_is_raised_when_input_is_list(self):
        test_settings = ToolTestSettings(
            tool='tool',
            input=['test1.exe', 'test2.exe']
        )
        self.scenario_invalid_settings_error_is_raised(test_settings, 'input')

    def test_from_test_settings_error_is_raised_when_args_is_list(self):
        test_settings = ToolTestSettings(
            tool='tool',
            input='test.exe',
            args=['--arg1', '--arg2']
        )
        self.scenario_invalid_settings_error_is_raised(test_settings, 'args')

    def test_without_paths_and_output_files_returns_same_args_when_there_are_no_files(self):
        args = ToolArguments()
        self.assertEqual(args, args.without_paths_and_output_files)

    def test_without_paths_and_output_files_returns_correct_args_when_there_are_files(self):
        args = ToolArguments(
            input_files=(File('file.exe', Directory(os.path.join(ROOT_DIR, 'inputs'))),),
        )
        stripped_args = args.without_paths_and_output_files
        self.assertEqual(len(stripped_args.input_files), 1)
        self.assertEqual(stripped_args.input_files[0].path, 'file.exe')

    def test_with_rebased_files_returns_same_args_when_there_are_no_files(self):
        args = ToolArguments()
        rebased_args = args.with_rebased_files(
            Directory(os.path.join(ROOT_DIR, 'inputs')),
            Directory(os.path.join(ROOT_DIR, 'outputs'))
        )
        self.assertEqual(args, rebased_args)

    def test_with_rebased_files_returns_correct_args_when_there_are_files(self):
        args = ToolArguments(
            input_files=(StandaloneFile('file.exe'),)
        )
        rebased_args = args.with_rebased_files(
            Directory(os.path.join(ROOT_DIR, 'inputs')),
            Directory(os.path.join(ROOT_DIR, 'outputs'))
        )
        self.assertEqual(len(rebased_args.input_files), 1)
        self.assertEqual(
            rebased_args.input_files[0].path,
            os.path.join(ROOT_DIR, 'inputs', 'file.exe')
        )

    def test_clone_returns_other_args_equal_to_original_args(self):
        args = ToolArguments(
            input_files=(StandaloneFile('file.exe'),),
            args='--arg'
        )
        cloned_args = args.clone()
        self.assertIsNot(args, cloned_args)
        self.assertEqual(args, cloned_args)

    def test_clone_preserves_instance_type(self):
        args = DecompilerArguments()
        cloned_args = args.clone()
        self.assertIsInstance(cloned_args, DecompilerArguments)

    def test_clone_but_returns_other_args_equal_to_original_args_except_for_changed_attributes(self):
        args = ToolArguments(
            input_files=(StandaloneFile('file.exe'),),
            args='--arg'
        )
        cloned_args = args.clone_but(args='--other-arg')
        self.assertIsNot(args, cloned_args)
        self.assertEqual(cloned_args.input_files, args.input_files)
        self.assertEqual(cloned_args.args, '--other-arg')

    def test_clone_but_preserves_instance_type(self):
        args = DecompilerArguments()
        cloned_args = args.clone_but()
        self.assertIsInstance(cloned_args, DecompilerArguments)

    def test_two_args_having_same_data_are_equal(self):
        args1 = ToolArguments(
            input_files=(StandaloneFile('file.exe'),),
            args='--arg'
        )
        args2 = ToolArguments(
            input_files=(StandaloneFile('file.exe'),),
            args='--arg'
        )
        self.assertEqual(args1, args2)

    def test_two_args_having_different_input_file_are_not_equal(self):
        args1 = ToolArguments(
            input_files=(StandaloneFile('file1.exe'),)
        )
        args2 = ToolArguments(
            input_files=(StandaloneFile('file2.exe'),)
        )
        self.assertNotEqual(args1, args2)

    def test_two_args_having_different_args_are_not_equal(self):
        args1 = ToolArguments(
            input_files=(StandaloneFile('file.exe'),),
            args='--arg'
        )
        args2 = ToolArguments(
            input_files=(StandaloneFile('file.exe'),),
            args='--other-arg'
        )
        self.assertNotEqual(args1, args2)

    def test_repr_returns_executable_repr_that_creates_original_args(self):
        args = ToolArguments(
            input_files=(StandaloneFile('file.exe'),),
            args='--arg'
        )
        self.assertEqual(args, eval(repr(args)))
