"""
    Tests for the :mod:`regression_tests.tools.bin2pat_arguments` module.
"""

import os
import unittest

from regression_tests.filesystem.directory import Directory
from regression_tests.filesystem.file import File
from regression_tests.filesystem.file import StandaloneFile
from regression_tests.test_settings import InvalidTestSettingsError
from regression_tests.tools.bin2pat_arguments import Bin2PatArguments
from regression_tests.tools.bin2pat_test_settings import Bin2PatTestSettings
from tests.filesystem.directory_tests import ROOT_DIR


class Bin2PatArgumentsTests(unittest.TestCase):
    """Tests for `Bin2PatArguments`."""

    def test_input_file_returns_file_with_correct_name(self):
        args = Bin2PatArguments(
            input_files=(StandaloneFile('mod.o'),)
        )
        self.assertEqual(args.input_file.name, 'mod.o')

    def test_as_list_returns_empty_list_when_nothing_is_set(self):
        args = Bin2PatArguments()
        self.assertEqual(args.as_list, [])

    def test_as_list_returns_correct_list_when_just_input_files_are_set(self):
        args = Bin2PatArguments(
            input_files=(StandaloneFile('mod.o'),)
        )
        self.assertEqual(args.as_list, ['mod.o'])

    def test_as_list_returns_correct_list_when_output_file_is_set(self):
        args = Bin2PatArguments(
            input_files=(StandaloneFile('mod.o'),),
            output_file=StandaloneFile('mod.o.yara')
        )
        self.assertEqual(args.as_list, ['mod.o', '-o', 'mod.o.yara'])

    def test_as_list_returns_correct_list_when_just_args_is_set(self):
        args = Bin2PatArguments(
            args='  --arg1   --arg2  '
        )
        self.assertEqual(args.as_list, ['--arg1', '--arg2'])

    def test_from_test_settings_input_files_are_present_when_set(self):
        test_settings = Bin2PatTestSettings(input='mod.o')
        args = Bin2PatArguments.from_test_settings(test_settings)
        self.assertEqual(len(args.input_files), 1)
        self.assertEqual(args.input_files[0].name, test_settings.input)

    def test_from_test_settings_output_file_is_automatically_set(self):
        test_settings = Bin2PatTestSettings(input='mod.o')
        args = Bin2PatArguments.from_test_settings(test_settings)
        self.assertIsNotNone(args.output_file)

    def test_from_test_settings_output_file_has_correct_name(self):
        test_settings = Bin2PatTestSettings(input='mod.o')
        args = Bin2PatArguments.from_test_settings(test_settings)
        self.assertEqual(args.output_file.name, 'mod.o.yara')

    def test_from_test_settings_args_is_present_when_set(self):
        test_settings = Bin2PatTestSettings(input='mod.o', args='--arg1 --arg2')
        args = Bin2PatArguments.from_test_settings(test_settings)
        self.assertEqual(args.args, test_settings.args)

    def scenario_invalid_settings_error_is_raised(self, test_settings, ref_exc_substr):
        with self.assertRaises(InvalidTestSettingsError) as cm:
            Bin2PatArguments.from_test_settings(test_settings)
        self.assertIn(ref_exc_substr, str(cm.exception))

    def test_from_test_settings_error_is_raised_when_there_is_no_input(self):
        test_settings = Bin2PatTestSettings(input=None)
        self.scenario_invalid_settings_error_is_raised(test_settings, 'input')

    def test_from_test_settings_error_is_raised_when_input_is_list(self):
        test_settings = Bin2PatTestSettings(input=['mod1.o', 'mod2.o'])
        self.scenario_invalid_settings_error_is_raised(test_settings, 'input')

    def test_from_test_settings_error_is_raised_when_args_is_list(self):
        test_settings = Bin2PatTestSettings(input='mod.o', args=['--arg1', '--arg2'])
        self.scenario_invalid_settings_error_is_raised(test_settings, 'args')

    def test_without_paths_and_output_files_returns_same_args_when_there_are_no_files(self):
        args = Bin2PatArguments()
        self.assertEqual(args, args.without_paths_and_output_files)

    def test_without_paths_and_output_files_returns_correct_args_when_there_are_files(self):
        args = Bin2PatArguments(
            input_files=(File('mod.o', Directory(os.path.join(ROOT_DIR, 'inputs'))),),
            output_file=File('mod.o.yara', Directory(os.path.join(ROOT_DIR, 'outputs')))
        )
        stripped_args = args.without_paths_and_output_files
        self.assertEqual(len(stripped_args.input_files), 1)
        self.assertEqual(stripped_args.input_files[0].path, 'mod.o')
        self.assertIsNone(stripped_args.output_file)

    def test_with_rebased_files_returns_same_args_when_there_are_no_files(self):
        args = Bin2PatArguments()
        rebased_args = args.with_rebased_files(
            Directory(os.path.join(ROOT_DIR, 'inputs')),
            Directory(os.path.join(ROOT_DIR, 'outputs'))
        )
        self.assertEqual(args, rebased_args)

    def test_with_rebased_files_returns_correct_args_when_there_are_files(self):
        args = Bin2PatArguments(
            input_files=(StandaloneFile('mod.o'),),
            output_file=StandaloneFile('mod.o.yara')
        )
        rebased_args = args.with_rebased_files(
            Directory(os.path.join(ROOT_DIR, 'inputs')),
            Directory(os.path.join(ROOT_DIR, 'outputs'))
        )
        self.assertEqual(len(rebased_args.input_files), 1)
        self.assertEqual(
            rebased_args.input_files[0].path,
            os.path.join(ROOT_DIR, 'inputs', 'mod.o')
        )
        self.assertEqual(
            rebased_args.output_file.path,
            os.path.join(ROOT_DIR, 'outputs', 'mod.o.yara')
        )

    def test_clone_returns_other_args_equal_to_original_args(self):
        args = Bin2PatArguments(
            input_files=(StandaloneFile('mod.o'),),
            output_file=StandaloneFile('mod.o.yara'),
            args='--arg'
        )
        cloned_args = args.clone()
        self.assertIsNot(args, cloned_args)
        self.assertEqual(args, cloned_args)

    def test_two_args_having_same_data_are_equal(self):
        args1 = Bin2PatArguments(
            input_files=(StandaloneFile('mod.o'),),
            args='--arg'
        )
        args2 = Bin2PatArguments(
            input_files=(StandaloneFile('mod.o'),),
            args='--arg'
        )
        self.assertEqual(args1, args2)

    def test_two_args_having_different_input_files_are_not_equal(self):
        args1 = Bin2PatArguments(
            input_files=(StandaloneFile('mod1.o'),)
        )
        args2 = Bin2PatArguments(
            input_files=(StandaloneFile('mod2.o'),)
        )
        self.assertNotEqual(args1, args2)

    def test_two_args_having_different_output_file_are_not_equal(self):
        args1 = Bin2PatArguments(
            output_file=StandaloneFile('mod1.o.yara')
        )
        args2 = Bin2PatArguments(
            output_file=StandaloneFile('mod2.o.yara')
        )
        self.assertNotEqual(args1, args2)

    def test_two_args_having_different_args_are_not_equal(self):
        args1 = Bin2PatArguments(
            input_files=(StandaloneFile('mod.o'),),
            args='--arg'
        )
        args2 = Bin2PatArguments(
            input_files=(StandaloneFile('mod.o'),),
            args='--other-arg'
        )
        self.assertNotEqual(args1, args2)

    def test_repr_returns_executable_repr_that_creates_original_args(self):
        args = Bin2PatArguments(
            input_files=(StandaloneFile('mod.o'),),
            output_file=StandaloneFile('mod.o.yara'),
            args='--arg'
        )
        self.assertEqual(args, eval(repr(args)))
