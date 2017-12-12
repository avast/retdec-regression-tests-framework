"""
    Tests for the :mod:`regression_tests.tools.fileinfo_arguments` module.
"""

import os
import unittest

from regression_tests.filesystem.directory import Directory
from regression_tests.filesystem.file import File
from regression_tests.filesystem.file import StandaloneFile
from regression_tests.test_settings import InvalidTestSettingsError
from regression_tests.tools.fileinfo_arguments import FileinfoArguments
from regression_tests.tools.fileinfo_test_settings import FileinfoTestSettings
from tests.filesystem.directory_tests import ROOT_DIR


class FileinfoArgumentsTests(unittest.TestCase):
    """Tests for `FileinfoArguments`."""

    def test_input_file_returns_file_with_correct_name(self):
        args = FileinfoArguments(
            input_files=(StandaloneFile('file.exe'),)
        )
        self.assertEqual(args.input_file.name, 'file.exe')

    def test_as_list_returns_empty_list_when_nothing_is_set(self):
        args = FileinfoArguments()
        self.assertEqual(args.as_list, [])

    def test_as_list_returns_correct_list_when_just_input_files_are_set(self):
        args = FileinfoArguments(
            input_files=(StandaloneFile('file.exe'),)
        )
        self.assertEqual(args.as_list, ['file.exe'])

    def test_as_list_returns_correct_list_when_config_file_is_set(self):
        args = FileinfoArguments(
            input_files=(StandaloneFile('file.exe'),),
            config_file=StandaloneFile('file.json')
        )
        self.assertEqual(args.as_list, ['file.exe', '-c', 'file.json'])

    def test_as_list_returns_correct_list_when_just_args_is_set(self):
        args = FileinfoArguments(
            args='  --arg1   --arg2  '
        )
        self.assertEqual(args.as_list, ['--arg1', '--arg2'])

    def test_from_test_settings_input_files_are_present_when_set(self):
        test_settings = FileinfoTestSettings(input='test.exe')
        args = FileinfoArguments.from_test_settings(test_settings)
        self.assertEqual(len(args.input_files), 1)
        self.assertEqual(args.input_files[0].name, test_settings.input)

    def test_from_test_settings_config_file_is_present_when_set(self):
        test_settings = FileinfoTestSettings(input='test.exe')
        args = FileinfoArguments.from_test_settings(test_settings)
        self.assertEqual(args.config_file.name, 'test.exe.json')

    def test_from_test_settings_args_is_present_when_set(self):
        test_settings = FileinfoTestSettings(input='test.exe', args='--arg1 --arg2')
        args = FileinfoArguments.from_test_settings(test_settings)
        self.assertEqual(args.args, test_settings.args)

    def scenario_invalid_settings_error_is_raised(self, test_settings, ref_exc_substr):
        with self.assertRaises(InvalidTestSettingsError) as cm:
            FileinfoArguments.from_test_settings(test_settings)
        self.assertIn(ref_exc_substr, str(cm.exception))

    def test_from_test_settings_error_is_raised_when_there_is_no_input(self):
        test_settings = FileinfoTestSettings(input=None)
        self.scenario_invalid_settings_error_is_raised(test_settings, 'input')

    def test_from_test_settings_error_is_raised_when_input_is_list(self):
        test_settings = FileinfoTestSettings(input=['test1.exe', 'test2.exe'])
        self.scenario_invalid_settings_error_is_raised(test_settings, 'input')

    def test_from_test_settings_error_is_raised_when_args_is_list(self):
        test_settings = FileinfoTestSettings(input='test.exe', args=['--arg1', '--arg2'])
        self.scenario_invalid_settings_error_is_raised(test_settings, 'args')

    def test_without_paths_and_output_files_returns_same_args_when_there_are_no_files(self):
        args = FileinfoArguments()
        self.assertEqual(args, args.without_paths_and_output_files)

    def test_without_paths_and_output_files_returns_correct_args_when_there_are_files(self):
        args = FileinfoArguments(
            input_files=(File('file.exe', Directory(os.path.join(ROOT_DIR, 'inputs'))),),
            config_file=File('file.json', Directory(os.path.join(ROOT_DIR, 'outputs')))
        )
        stripped_args = args.without_paths_and_output_files
        self.assertEqual(len(stripped_args.input_files), 1)
        self.assertEqual(stripped_args.input_files[0].path, 'file.exe')
        self.assertIsNone(stripped_args.config_file)

    def test_with_rebased_files_returns_same_args_when_there_are_no_files(self):
        args = FileinfoArguments()
        rebased_args = args.with_rebased_files(
            Directory(os.path.join(ROOT_DIR, 'inputs')),
            Directory(os.path.join(ROOT_DIR, 'outputs'))
        )
        self.assertEqual(args, rebased_args)

    def test_with_rebased_files_returns_correct_args_when_there_are_files(self):
        args = FileinfoArguments(
            input_files=(StandaloneFile('file.exe'),),
            config_file=StandaloneFile('file.json')
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
            rebased_args.config_file.path,
            os.path.join(ROOT_DIR, 'outputs', 'file.json')
        )

    def test_clone_returns_other_args_equal_to_original_args(self):
        args = FileinfoArguments(
            input_files=(StandaloneFile('file.exe'),),
            config_file=StandaloneFile('file.json'),
            args='--arg'
        )
        cloned_args = args.clone()
        self.assertIsNot(args, cloned_args)
        self.assertEqual(args, cloned_args)

    def test_two_args_having_same_data_are_equal(self):
        args1 = FileinfoArguments(
            input_files=(StandaloneFile('file.exe'),),
            args='--arg'
        )
        args2 = FileinfoArguments(
            input_files=(StandaloneFile('file.exe'),),
            args='--arg'
        )
        self.assertEqual(args1, args2)

    def test_two_args_having_different_input_files_are_not_equal(self):
        args1 = FileinfoArguments(
            input_files=(StandaloneFile('file1.exe'),)
        )
        args2 = FileinfoArguments(
            input_files=(StandaloneFile('file2.exe'),)
        )
        self.assertNotEqual(args1, args2)

    def test_two_args_having_different_config_file_are_not_equal(self):
        args1 = FileinfoArguments(
            config_file=StandaloneFile('file1.json')
        )
        args2 = FileinfoArguments(
            config_file=StandaloneFile('file2.json')
        )
        self.assertNotEqual(args1, args2)

    def test_two_args_having_different_args_are_not_equal(self):
        args1 = FileinfoArguments(
            input_files=(StandaloneFile('file.exe'),),
            args='--arg'
        )
        args2 = FileinfoArguments(
            input_files=(StandaloneFile('file.exe'),),
            args='--other-arg'
        )
        self.assertNotEqual(args1, args2)

    def test_repr_returns_executable_repr_that_creates_original_args(self):
        args = FileinfoArguments(
            input_files=(StandaloneFile('file.exe'),),
            config_file=StandaloneFile('file.json'),
            args='--arg'
        )
        self.assertEqual(args, eval(repr(args)))
