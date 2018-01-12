"""
    Tests for the :mod:`regression_tests.tools.decompiler_arguments` module.
"""

import os
import unittest

from regression_tests.tools.decompiler_arguments import DecompilerArguments
from regression_tests.filesystem.directory import Directory
from regression_tests.filesystem.file import File
from regression_tests.filesystem.file import StandaloneFile
from regression_tests.test_settings import InvalidTestSettingsError
from regression_tests.test_settings import TestSettings
from tests.filesystem.directory_tests import ROOT_DIR


class DecompilerArgumentsTests(unittest.TestCase):
    """Tests for `DecompilerArguments`."""

    def test_input_file_returns_file_with_correct_name(self):
        args = DecompilerArguments(
            input_files=(StandaloneFile('file.exe'),)
        )
        self.assertEqual(args.input_file.name, 'file.exe')

    def test_as_list_returns_empty_list_when_nothing_is_set(self):
        args = DecompilerArguments()
        self.assertEqual(args.as_list, [])

    def test_as_list_returns_correct_list_when_just_input_files_are_set(self):
        args = DecompilerArguments(
            input_files=(StandaloneFile('file.exe'),)
        )
        self.assertEqual(args.as_list, ['file.exe'])

    def test_as_list_returns_correct_list_when_pdb_file_is_set(self):
        args = DecompilerArguments(
            input_files=(StandaloneFile('file.exe'),),
            pdb_file=StandaloneFile('file.pdb')
        )
        self.assertEqual(args.as_list, ['file.exe', '--pdb', 'file.pdb'])

    def test_as_list_returns_correct_list_when_config_file_is_set(self):
        args = DecompilerArguments(
            input_files=(StandaloneFile('file.exe'),),
            config_file=StandaloneFile('file.json')
        )
        self.assertEqual(args.as_list, ['file.exe', '--config', 'file.json'])

    def test_as_list_returns_correct_list_when_static_code_archive_is_set(self):
        args = DecompilerArguments(
            input_files=(StandaloneFile('file.exe'),),
            static_code_archive=StandaloneFile('file.a')
        )
        self.assertEqual(args.as_list, ['file.exe', '--static-code-archive', 'file.a'])

    def test_as_list_returns_correct_list_when_static_code_sigfile_is_set(self):
        args = DecompilerArguments(
            input_files=(StandaloneFile('file.exe'),),
            static_code_sigfile=StandaloneFile('file.sig')
        )
        self.assertEqual(args.as_list, ['file.exe', '--static-code-sigfile', 'file.sig'])

    def test_as_list_returns_correct_list_when_just_arch_is_set(self):
        args = DecompilerArguments(
            arch='x86'
        )
        self.assertEqual(args.as_list, ['-a', 'x86'])

    def test_as_list_returns_correct_list_when_just_format_is_set(self):
        args = DecompilerArguments(
            format='elf'
        )
        self.assertEqual(args.as_list, ['-f', 'elf'])

    def test_as_list_returns_correct_list_when_just_mode_is_set(self):
        args = DecompilerArguments(
            mode='bin'
        )
        self.assertEqual(args.as_list, ['-m', 'bin'])

    def test_as_list_returns_correct_list_when_just_hll_is_set(self):
        args = DecompilerArguments(
            hll='py'
        )
        self.assertEqual(args.as_list, ['-l', 'py'])

    def test_as_list_returns_correct_list_when_just_ar_index_is_set_as_int(self):
        args = DecompilerArguments(
            ar_index=0,
        )
        self.assertEqual(args.as_list, ['--ar-index', '0'])  # Converted to str.

    def test_as_list_returns_correct_list_when_just_ar_index_is_set_as_str(self):
        args = DecompilerArguments(
            ar_index='0',
        )
        self.assertEqual(args.as_list, ['--ar-index', '0'])

    def test_as_list_returns_correct_list_when_just_ar_name_is_set(self):
        args = DecompilerArguments(
            ar_name='file.o',
        )
        self.assertEqual(args.as_list, ['--ar-name', 'file.o'])

    def test_as_list_returns_correct_list_when_just_args_is_set(self):
        args = DecompilerArguments(
            args='  --arg1   --arg2  '
        )
        self.assertEqual(args.as_list, ['--arg1', '--arg2'])

    def test_as_list_returns_correct_list_when_just_output_is_set(self):
        args = DecompilerArguments(
            output_file=StandaloneFile('file.out.exe')
        )
        self.assertEqual(args.as_list, ['-o', 'file.out.exe'])

    def test_from_test_settings_input_files_are_present_when_set(self):
        test_settings = TestSettings(input='file.exe')
        args = DecompilerArguments.from_test_settings(test_settings)
        self.assertEqual(len(args.input_files), 1)
        self.assertEqual(args.input_files[0].name, test_settings.input)

    def test_from_test_settings_pdb_file_is_present_when_set(self):
        test_settings = TestSettings(input='test.exe', pdb='file.pdb')
        args = DecompilerArguments.from_test_settings(test_settings)
        self.assertEqual(args.pdb_file.name, test_settings.pdb)

    def test_from_test_settings_config_file_is_present_when_set(self):
        test_settings = TestSettings(input='test.exe', config='file.json')
        args = DecompilerArguments.from_test_settings(test_settings)
        self.assertEqual(args.config_file.name, test_settings.config)

    def test_from_test_settings_static_code_archive_is_present_when_set(self):
        test_settings = TestSettings(input='test.exe', static_code_archive='file.a')
        args = DecompilerArguments.from_test_settings(test_settings)
        self.assertEqual(args.static_code_archive.name, test_settings.static_code_archive)

    def test_from_test_settings_static_code_sigfile_is_present_when_set(self):
        test_settings = TestSettings(input='test.exe', static_code_sigfile='file.sig')
        args = DecompilerArguments.from_test_settings(test_settings)
        self.assertEqual(args.static_code_sigfile.name, test_settings.static_code_sigfile)

    def test_from_test_settings_arch_is_present_when_set(self):
        test_settings = TestSettings(input='file.exe', arch='x86')
        args = DecompilerArguments.from_test_settings(test_settings)
        self.assertEqual(args.arch, test_settings.arch)

    def test_from_test_settings_format_is_present_when_set(self):
        test_settings = TestSettings(input='file.exe', format='elf')
        args = DecompilerArguments.from_test_settings(test_settings)
        self.assertEqual(args.format, test_settings.format)

    def test_from_test_settings_mode_is_present_when_set(self):
        test_settings = TestSettings(input='file.exe', mode='bin')
        args = DecompilerArguments.from_test_settings(test_settings)
        self.assertEqual(args.mode, test_settings.mode)

    def test_from_test_settings_hll_is_present_when_set(self):
        test_settings = TestSettings(input='file.exe', hll='py')
        args = DecompilerArguments.from_test_settings(test_settings)
        self.assertEqual(args.hll, test_settings.hll)

    def test_from_test_settings_ar_index_is_present_when_set(self):
        test_settings = TestSettings(input='archive.a', ar_index=0)
        args = DecompilerArguments.from_test_settings(test_settings)
        self.assertEqual(args.ar_index, test_settings.ar_index)

    def test_from_test_settings_ar_name_is_present_when_set(self):
        test_settings = TestSettings(input='archive.a', ar_name='file.o')
        args = DecompilerArguments.from_test_settings(test_settings)
        self.assertEqual(args.ar_name, test_settings.ar_name)

    def test_from_test_settings_args_is_present_when_set(self):
        test_settings = TestSettings(input='file.exe', args='--arg1 --arg2')
        args = DecompilerArguments.from_test_settings(test_settings)
        self.assertEqual(args.args, test_settings.args)

    def test_from_test_settings_output_file_has_correct_name_when_input_is_exe_file(self):
        test_settings = TestSettings(input='file.exe')
        args = DecompilerArguments.from_test_settings(test_settings)
        self.assertEqual(args.output_file.name, 'file.c')

    def test_from_test_settings_output_file_has_correct_name_when_input_is_ll_file(self):
        test_settings = TestSettings(input='file.ll')
        args = DecompilerArguments.from_test_settings(test_settings)
        self.assertEqual(args.output_file.name, 'file.c')

    def test_from_test_settings_output_file_has_correct_name_when_input_is_other_file(self):
        test_settings = TestSettings(input='file')
        args = DecompilerArguments.from_test_settings(test_settings)
        self.assertEqual(args.output_file.name, 'file.c')

    def scenario_invalid_settings_error_is_raised(self, test_settings, ref_exc_substr):
        with self.assertRaises(InvalidTestSettingsError) as cm:
            DecompilerArguments.from_test_settings(test_settings)
        self.assertIn(ref_exc_substr, str(cm.exception))

    def test_from_test_settings_error_is_raised_when_there_is_no_input(self):
        test_settings = TestSettings(input=None)
        self.scenario_invalid_settings_error_is_raised(test_settings, 'input')

    def test_from_test_settings_error_is_raised_when_input_is_list(self):
        test_settings = TestSettings(input=['test1.exe', 'test2.exe'])
        self.scenario_invalid_settings_error_is_raised(test_settings, 'input')

    def test_from_test_settings_error_is_raised_when_pdb_is_list(self):
        test_settings = TestSettings(input='test.exe', pdb=['test1.pdb', 'test2.pdb'])
        self.scenario_invalid_settings_error_is_raised(test_settings, 'pdb')

    def test_from_test_settings_error_is_raised_when_config_is_list(self):
        test_settings = TestSettings(input='test.exe', config=['test1.json', 'test2.json'])
        self.scenario_invalid_settings_error_is_raised(test_settings, 'config')

    def test_from_test_settings_error_is_raised_when_static_code_archive_is_list(self):
        test_settings = TestSettings(input='test.exe', static_code_archive=['test1.a', 'test2.a'])
        self.scenario_invalid_settings_error_is_raised(test_settings, 'static_code_archive')

    def test_from_test_settings_error_is_raised_when_static_code_sigfile_is_list(self):
        test_settings = TestSettings(input='test.exe', static_code_sigfile=['test1.sig', 'test2.sig'])
        self.scenario_invalid_settings_error_is_raised(test_settings, 'static_code_sigfile')

    def test_from_test_settings_error_is_raised_when_arch_is_list(self):
        test_settings = TestSettings(input='file.exe', arch=['x86', 'arm'])
        self.scenario_invalid_settings_error_is_raised(test_settings, 'arch')

    def test_from_test_settings_error_is_raised_when_format_is_list(self):
        test_settings = TestSettings(input='file.exe', format=['elf', 'pe'])
        self.scenario_invalid_settings_error_is_raised(test_settings, 'format')

    def test_from_test_settings_error_is_raised_when_mode_is_list(self):
        test_settings = TestSettings(input='file.exe', mode=['bin', 'raw'])
        self.scenario_invalid_settings_error_is_raised(test_settings, 'mode')

    def test_from_test_settings_error_is_raised_when_hll_is_list(self):
        test_settings = TestSettings(input='file.exe', hll=['c', 'py'])
        self.scenario_invalid_settings_error_is_raised(test_settings, 'hll')

    def test_from_test_settings_error_is_raised_when_ar_index_is_list(self):
        test_settings = TestSettings(input='archive.a', ar_index=[0, 1])
        self.scenario_invalid_settings_error_is_raised(test_settings, 'ar_index')

    def test_from_test_settings_error_is_raised_when_ar_name_is_list(self):
        test_settings = TestSettings(input='archive.a', ar_name=['file1.o', 'file2.o'])
        self.scenario_invalid_settings_error_is_raised(test_settings, 'ar_name')

    def test_from_test_settings_error_is_raised_when_args_is_list(self):
        test_settings = TestSettings(input='file.exe', args=['--arg1', '--arg2'])
        self.scenario_invalid_settings_error_is_raised(test_settings, 'args')

    def test_without_paths_and_output_files_returns_same_args_when_there_are_no_files(self):
        args = DecompilerArguments()
        self.assertEqual(args, args.without_paths_and_output_files)

    def test_without_paths_and_output_files_returns_correct_args_when_there_are_files(self):
        args = DecompilerArguments(
            input_files=(File('file.exe', Directory(os.path.join(ROOT_DIR, 'inputs'))),),
            pdb_file=File('file.pdb', Directory(os.path.join(ROOT_DIR, 'inputs'))),
            config_file=File('file.json', Directory(os.path.join(ROOT_DIR, 'inputs'))),
            static_code_archive=File('file.a', Directory(os.path.join(ROOT_DIR, 'inputs'))),
            static_code_sigfile=File('file.sig', Directory(os.path.join(ROOT_DIR, 'inputs'))),
            output_file=File('file.c', Directory(os.path.join(ROOT_DIR, 'outputs')))
        )
        stripped_args = args.without_paths_and_output_files
        self.assertEqual(len(stripped_args.input_files), 1)
        self.assertEqual(stripped_args.input_files[0].path, 'file.exe')
        self.assertEqual(stripped_args.pdb_file.path, 'file.pdb')
        self.assertEqual(stripped_args.config_file.path, 'file.json')
        self.assertEqual(stripped_args.static_code_archive.path, 'file.a')
        self.assertEqual(stripped_args.static_code_sigfile.path, 'file.sig')
        self.assertIsNone(stripped_args.output_file)

    def test_with_rebased_files_returns_same_args_when_there_are_no_files(self):
        args = DecompilerArguments()
        rebased_args = args.with_rebased_files(
            Directory(os.path.join(ROOT_DIR, 'inputs')),
            Directory(os.path.join(ROOT_DIR, 'outputs'))
        )
        self.assertEqual(args, rebased_args)

    def test_with_rebased_files_returns_correct_args_when_there_are_files(self):
        args = DecompilerArguments(
            input_files=(StandaloneFile('file.exe'),),
            pdb_file=StandaloneFile('file.pdb'),
            config_file=StandaloneFile('file.json'),
            static_code_archive=StandaloneFile('file.a'),
            static_code_sigfile=StandaloneFile('file.sig'),
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
            rebased_args.pdb_file.path,
            os.path.join(ROOT_DIR, 'inputs', 'file.pdb')
        )
        self.assertEqual(
            rebased_args.config_file.path,
            os.path.join(ROOT_DIR, 'inputs', 'file.json')
        )
        self.assertEqual(
            rebased_args.static_code_archive.path,
            os.path.join(ROOT_DIR, 'inputs', 'file.a')
        )
        self.assertEqual(
            rebased_args.static_code_sigfile.path,
            os.path.join(ROOT_DIR, 'inputs', 'file.sig')
        )
        self.assertEqual(
            rebased_args.output_file.path,
            os.path.join(ROOT_DIR, 'outputs', 'file.c')
        )

    def test_clone_returns_other_args_equal_to_original_args(self):
        args = DecompilerArguments(
            input_files=(StandaloneFile('file.exe'),),
            pdb_file=StandaloneFile('file.pdb'),
            config_file=StandaloneFile('file.json'),
            static_code_archive=StandaloneFile('file.a'),
            static_code_sigfile=StandaloneFile('file.sig'),
            arch='x86',
            format='elf',
            mode='bin',
            hll='c',
            ar_index=0,
            ar_name='file.o',
            args='--arg'
        )
        cloned_args = args.clone()
        self.assertIsNot(args, cloned_args)
        self.assertEqual(args, cloned_args)

    def test_two_args_having_same_data_are_equal(self):
        args1 = DecompilerArguments(
            input_files=(StandaloneFile('file.exe'),),
            pdb_file=StandaloneFile('file.pdb'),
            config_file=StandaloneFile('file.json'),
            static_code_archive=StandaloneFile('file.a'),
            static_code_sigfile=StandaloneFile('file.sig'),
            arch='x86',
            format='elf',
            mode='bin',
            hll='c',
            ar_index=0,
            ar_name='file.o',
            args='--arg'
        )
        args2 = DecompilerArguments(
            input_files=(StandaloneFile('file.exe'),),
            pdb_file=StandaloneFile('file.pdb'),
            config_file=StandaloneFile('file.json'),
            static_code_archive=StandaloneFile('file.a'),
            static_code_sigfile=StandaloneFile('file.sig'),
            arch='x86',
            format='elf',
            mode='bin',
            hll='c',
            ar_index=0,
            ar_name='file.o',
            args='--arg'
        )
        self.assertEqual(args1, args2)

    def test_two_args_having_different_input_files_are_not_equal(self):
        args1 = DecompilerArguments(
            input_files=(StandaloneFile('file1.exe'),)
        )
        args2 = DecompilerArguments(
            input_files=(StandaloneFile('file2.exe'),)
        )
        self.assertNotEqual(args1, args2)

    def test_two_args_having_different_pdb_files_are_not_equal(self):
        args1 = DecompilerArguments(
            input_files=(StandaloneFile('file.exe'),),
            pdb_file=StandaloneFile('file1.pdb')
        )
        args2 = DecompilerArguments(
            input_files=(StandaloneFile('file.exe'),),
            pdb_file=StandaloneFile('file2.pdb')
        )
        self.assertNotEqual(args1, args2)

    def test_two_args_having_different_static_code_archives_are_not_equal(self):
        args1 = DecompilerArguments(
            input_files=(StandaloneFile('file.exe'),),
            static_code_archive=StandaloneFile('file1.a')
        )
        args2 = DecompilerArguments(
            input_files=(StandaloneFile('file.exe'),),
            static_code_archive=StandaloneFile('file2.a')
        )
        self.assertNotEqual(args1, args2)

    def test_two_args_having_different_static_code_sigfiles_are_not_equal(self):
        args1 = DecompilerArguments(
            input_files=(StandaloneFile('file.exe'),),
            static_code_sigfile=StandaloneFile('file1.sig')
        )
        args2 = DecompilerArguments(
            input_files=(StandaloneFile('file.exe'),),
            static_code_sigfile=StandaloneFile('file2.sig')
        )
        self.assertNotEqual(args1, args2)

    def test_two_args_having_different_config_files_are_not_equal(self):
        args1 = DecompilerArguments(
            input_files=(StandaloneFile('file.exe'),),
            config_file=StandaloneFile('file1.json')
        )
        args2 = DecompilerArguments(
            input_files=(StandaloneFile('file.exe'),),
            config_file=StandaloneFile('file2.json')
        )
        self.assertNotEqual(args1, args2)

    def test_two_args_having_different_arch_are_not_equal(self):
        args1 = DecompilerArguments(
            input_files=(StandaloneFile('file.exe'),),
            arch='x86'
        )
        args2 = DecompilerArguments(
            input_files=(StandaloneFile('file.exe'),),
            arch='arm'
        )
        self.assertNotEqual(args1, args2)

    def test_two_args_having_different_format_are_not_equal(self):
        args1 = DecompilerArguments(
            input_files=(StandaloneFile('file.exe'),),
            format='elf'
        )
        args2 = DecompilerArguments(
            input_files=(StandaloneFile('file.exe'),),
            format='pe'
        )
        self.assertNotEqual(args1, args2)

    def test_two_args_having_different_modes_are_not_equal(self):
        args1 = DecompilerArguments(
            input_files=(StandaloneFile('file.exe'),),
            mode='bin'
        )
        args2 = DecompilerArguments(
            input_files=(StandaloneFile('file.exe'),),
            mode='raw'
        )
        self.assertNotEqual(args1, args2)

    def test_two_args_having_different_hlls_are_not_equal(self):
        args1 = DecompilerArguments(
            input_files=(StandaloneFile('file.exe'),),
            hll='c'
        )
        args2 = DecompilerArguments(
            input_files=(StandaloneFile('file.exe'),),
            hll='py'
        )
        self.assertNotEqual(args1, args2)

    def test_two_args_having_different_ar_indexes_are_not_equal(self):
        args1 = DecompilerArguments(
            input_files=(StandaloneFile('archive.a'),),
            ar_index=0
        )
        args2 = DecompilerArguments(
            input_files=(StandaloneFile('archive.a'),),
            ar_index=1
        )
        self.assertNotEqual(args1, args2)

    def test_two_args_having_different_ar_names_are_not_equal(self):
        args1 = DecompilerArguments(
            input_files=(StandaloneFile('archive.a'),),
            ar_name='file1.o'
        )
        args2 = DecompilerArguments(
            input_files=(StandaloneFile('archive.a'),),
            ar_name='file2.o'
        )
        self.assertNotEqual(args1, args2)

    def test_two_args_having_different_args_are_not_equal(self):
        args1 = DecompilerArguments(
            input_files=(StandaloneFile('file.exe'),),
            args='--arg'
        )
        args2 = DecompilerArguments(
            input_files=(StandaloneFile('file.exe'),),
            args='--other-arg'
        )
        self.assertNotEqual(args1, args2)

    def test_repr_returns_executable_repr_that_creates_original_args(self):
        args = DecompilerArguments(
            input_files=(StandaloneFile('file.exe'),),
            pdb_file=StandaloneFile('file.pdb'),
            config_file=StandaloneFile('file.json'),
            static_code_archive=StandaloneFile('file.a'),
            static_code_sigfile=StandaloneFile('file.sig'),
            arch='x86',
            format='elf',
            mode='bin',
            hll='c',
            ar_index=0,
            ar_name='file.o',
            args='--arg'
        )
        self.assertEqual(args, eval(repr(args)))
