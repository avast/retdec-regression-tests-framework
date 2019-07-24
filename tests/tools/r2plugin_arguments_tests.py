"""
    Tests for the :mod:`regression_tests.tools.r2plugin_arguments` module.
"""

import os
import unittest

from regression_tests.filesystem.directory import Directory
from regression_tests.filesystem.file import File
from regression_tests.filesystem.file import StandaloneFile
from regression_tests.test_settings import InvalidTestSettingsError
from regression_tests.tools.r2plugin_arguments import R2PluginArguments
from regression_tests.tools.r2plugin_test_settings import R2PluginTestSettings
from tests.filesystem.directory_tests import ROOT_DIR


class R2PluginArgumentsTests(unittest.TestCase):
    """Tests for `R2PluginArguments`."""

    def test_input_file_returns_file_with_correct_name(self):
        args = R2PluginArguments(
            input_files=(StandaloneFile('file.exe'),)
        )
        self.assertEqual(args.input_file.name, 'file.exe')

    def test_as_list_returns_empty_list_when_nothing_is_set(self):
        args = R2PluginArguments()
        self.assertEqual(args.as_list, [])

    def test_as_list_returns_correct_list_when_just_input_files_are_set(self):
        args = R2PluginArguments(
            input_files=(StandaloneFile('file.exe'),)
        )
        self.assertEqual(args.as_list, ['file.exe'])

    def test_as_list_returns_correct_list_when_project_file_is_set(self):
        args = R2PluginArguments(
            input_files=(StandaloneFile('file.exe'),),
            project_file=StandaloneFile('rc')
        )
        self.assertEqual(args.as_list, ['file.exe', '--project', 'rc'])

    def test_as_list_returns_correct_list_when_output_file_is_set(self):
        args = R2PluginArguments(
            input_files=(StandaloneFile('file.exe'),),
            output_file=StandaloneFile('file.c')
        )
        self.assertEqual(args.as_list, ['file.exe', '-o', 'file.c'])

    def test_as_list_returns_correct_list_when_just_args_is_set(self):
        args = R2PluginArguments(
            args='  --arg1   --arg2  '
        )
        self.assertEqual(args.as_list, ['--arg1', '--arg2'])

    def test_from_test_settings_input_files_are_present_when_set(self):
        test_settings = R2PluginTestSettings(input='test.exe')
        args = R2PluginArguments.from_test_settings(test_settings)
        self.assertEqual(len(args.input_files), 1)
        self.assertEqual(args.input_files[0].name, test_settings.input)

    def test_from_test_settings_project_is_present_when_set(self):
        test_settings = R2PluginTestSettings(input='test.exe', project='rc')
        args = R2PluginArguments.from_test_settings(test_settings)
        self.assertEqual(args.project_file.name, test_settings.project)

    def test_from_test_settings_output_file_is_automatically_set(self):
        test_settings = R2PluginTestSettings(input='test.exe')
        args = R2PluginArguments.from_test_settings(test_settings)
        self.assertIsNotNone(args.output_file)

    def test_from_test_settings_output_file_has_correct_name_when_it_ends_with_exe(self):
        test_settings = R2PluginTestSettings(input='test.exe')
        args = R2PluginArguments.from_test_settings(test_settings)
        self.assertEqual(args.output_file.name, 'test.c')

    def test_from_test_settings_output_file_has_correct_name_when_it_does_not_end_with_exe(self):
        test_settings = R2PluginTestSettings(input='test.elf')
        args = R2PluginArguments.from_test_settings(test_settings)
        self.assertEqual(args.output_file.name, 'test.elf.c')

    def test_from_test_settings_args_is_present_when_set(self):
        test_settings = R2PluginTestSettings(input='test.exe', args='--arg1 --arg2')
        args = R2PluginArguments.from_test_settings(test_settings)
        self.assertEqual(args.args, test_settings.args)

    def scenario_invalid_settings_error_is_raised(self, test_settings, ref_exc_substr):
        with self.assertRaises(InvalidTestSettingsError) as cm:
            R2PluginArguments.from_test_settings(test_settings)
        self.assertIn(ref_exc_substr, str(cm.exception))

    def test_from_test_settings_error_is_raised_when_there_is_no_input(self):
        test_settings = R2PluginTestSettings(input=None)
        self.scenario_invalid_settings_error_is_raised(test_settings, 'input')

    def test_from_test_settings_error_is_raised_when_input_is_list(self):
        test_settings = R2PluginTestSettings(input=['test1.exe', 'test2.exe'])
        self.scenario_invalid_settings_error_is_raised(test_settings, 'input')

    def test_from_test_settings_error_is_raised_when_project_is_list(self):
        test_settings = R2PluginTestSettings(input='test.exe', project=['rc2', 'rc1'])
        self.scenario_invalid_settings_error_is_raised(test_settings, 'project')

    def test_from_test_settings_error_is_raised_when_args_is_list(self):
        test_settings = R2PluginTestSettings(input='test.exe', args=['--arg1', '--arg2'])
        self.scenario_invalid_settings_error_is_raised(test_settings, 'args')

    def test_without_paths_and_output_files_returns_same_args_when_there_are_no_files(self):
        args = R2PluginArguments()
        self.assertEqual(args, args.without_paths_and_output_files)

    def test_without_paths_and_output_files_returns_correct_args_when_there_are_files(self):
        args = R2PluginArguments(
            input_files=(File('file.exe', Directory(os.path.join(ROOT_DIR, 'inputs'))),),
            project_file=File('rc', Directory(os.path.join(ROOT_DIR, 'inputs'))),
            output_file=File('file.c', Directory(os.path.join(ROOT_DIR, 'outputs')))
        )
        stripped_args = args.without_paths_and_output_files
        self.assertEqual(len(stripped_args.input_files), 1)
        self.assertEqual(stripped_args.input_files[0].path, 'file.exe')
        self.assertIsNone(stripped_args.output_file)

    def test_with_rebased_files_returns_same_args_when_there_are_no_files(self):
        args = R2PluginArguments()
        rebased_args = args.with_rebased_files(
            Directory(os.path.join(ROOT_DIR, 'inputs')),
            Directory(os.path.join(ROOT_DIR, 'outputs'))
        )
        self.assertEqual(args, rebased_args)

    def test_with_rebased_files_returns_correct_args_when_there_are_files(self):
        args = R2PluginArguments(
            input_files=(StandaloneFile('file.exe'),),
            project_file=StandaloneFile('rc'),
            output_file=StandaloneFile('file.c')
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
        self.assertEqual(
            rebased_args.project_file.path,
            os.path.join(ROOT_DIR, 'inputs', 'rc')
        )
        self.assertEqual(
            rebased_args.output_file.path,
            os.path.join(ROOT_DIR, 'outputs', 'file.c')
        )

    def test_clone_returns_other_args_equal_to_original_args(self):
        args = R2PluginArguments(
            input_files=(StandaloneFile('file.exe'),),
            project_file=StandaloneFile('rc'),
            output_file=StandaloneFile('file.c'),
            args='--arg'
        )
        cloned_args = args.clone()
        self.assertIsNot(args, cloned_args)
        self.assertEqual(args, cloned_args)

    def test_two_args_having_same_data_are_equal(self):
        args1 = R2PluginArguments(
            input_files=(StandaloneFile('file.exe'),),
            project_file=StandaloneFile('rc'),
            args='--arg'
        )
        args2 = R2PluginArguments(
            input_files=(StandaloneFile('file.exe'),),
            project_file=StandaloneFile('rc'),
            args='--arg'
        )
        self.assertEqual(args1, args2)

    def test_two_args_having_different_input_files_are_not_equal(self):
        args1 = R2PluginArguments(
            input_files=(StandaloneFile('file.exe'),)
        )
        args2 = R2PluginArguments(
            input_files=(StandaloneFile('file2.exe'),)
        )
        self.assertNotEqual(args1, args2)

    def test_two_args_having_different_project_files_are_not_equal(self):
        args1 = R2PluginArguments(
            project_file=StandaloneFile('rc1')
        )
        args2 = R2PluginArguments(
            project_file=StandaloneFile('rc2')
        )
        self.assertNotEqual(args1, args2)

    def test_two_args_having_different_output_file_are_not_equal(self):
        args1 = R2PluginArguments(
            output_file=StandaloneFile('file1.c')
        )
        args2 = R2PluginArguments(
            output_file=StandaloneFile('file2.c')
        )
        self.assertNotEqual(args1, args2)

    def test_two_args_having_different_args_are_not_equal(self):
        args1 = R2PluginArguments(
            input_files=(StandaloneFile('file.exe'),),
            args='--arg'
        )
        args2 = R2PluginArguments(
            input_files=(StandaloneFile('file.exe'),),
            args='--other-arg'
        )
        self.assertNotEqual(args1, args2)

    def test_repr_returns_executable_repr_that_creates_original_args(self):
        args = R2PluginArguments(
            input_files=(StandaloneFile('file.exe'),),
            project_file=StandaloneFile('rc'),
            output_file=StandaloneFile('file.c'),
            args='--arg'
        )
        self.assertEqual(args, eval(repr(args)))
