"""
    Tests for the :mod:`regression_tests.tools.decompilation_test_settings` module.
"""

import unittest

from regression_tests.test_settings import TestSettings
from regression_tests.tools.decompilation_arguments import DecompilationArguments
from regression_tests.tools.decompilation_runner import DecompilationRunner
from regression_tests.tools.decompilation_test import DecompilationTest
from regression_tests.tools.decompilation_test_settings import DecompilationTestSettings


class DecompilationTestSettingsTests(unittest.TestCase):
    """Tests for `DecompilationTestSettings`."""

    def test_test_settings_creates_decompilation_test_settings_when_tool_is_not_specified(self):
        settings = TestSettings(input='file.exe')
        self.assertIsInstance(settings, DecompilationTestSettings)

    def test_test_settings_creates_decompilation_test_settings_when_tool_is_specified(self):
        settings = TestSettings(tool=DecompilationTestSettings.TOOL, input='file.exe')
        self.assertIsInstance(settings, DecompilationTestSettings)

    def test_tool_returns_correct_value(self):
        settings = DecompilationTestSettings(input='file.exe')
        self.assertEqual(settings.tool, DecompilationTestSettings.TOOL)

    def test_input_passed_to_constructor_is_accessible(self):
        INPUT = 'file.exe'
        settings = DecompilationTestSettings(input=INPUT)
        self.assertEqual(INPUT, settings.input)

    def test_args_passed_to_constructor_are_accessible(self):
        ARGS = '--keep-unreachable-funcs'
        settings = DecompilationTestSettings(input='file.exe', args=ARGS)
        self.assertEqual(ARGS, settings.args)

    def test_timeout_passed_to_constructor_is_accessible(self):
        TIMEOUT = 100
        settings = DecompilationTestSettings(input='file.exe', timeout=TIMEOUT)
        self.assertEqual(settings.timeout, TIMEOUT)

    def test_pdb_passed_to_constructor_is_accessible(self):
        PDB = 'file.pdb'
        settings = DecompilationTestSettings(input='file.exe', pdb=PDB)
        self.assertEqual(PDB, settings.pdb)

    def test_pdb_as_list_returns_empty_list_if_pdb_is_not_set(self):
        settings = DecompilationTestSettings(input='file.exe', pdb=None)
        self.assertEqual([], settings.pdb_as_list)

    def test_pdb_as_list_returns_pdb_when_pdb_is_list(self):
        PDB = ['file1.pdb', 'file2.pdb']
        settings = DecompilationTestSettings(input='file.exe', pdb=PDB)
        self.assertEqual(PDB, settings.pdb_as_list)

    def test_pdb_as_list_returns_list_when_pdb_is_single_file(self):
        PDB = 'file.pdb'
        settings = DecompilationTestSettings(input='file.exe', pdb=PDB)
        self.assertEqual([PDB], settings.pdb_as_list)

    def test_has_multiple_pdbs_returns_true_when_there_are_multiple_pdbs(self):
        settings = DecompilationTestSettings(input='file.exe', pdb=['file1.pdb', 'file2.pdb'])
        self.assertTrue(settings.has_multiple_pdbs())

    def test_has_multiple_pdbs_returns_false_when_there_is_just_single_pdb(self):
        settings = DecompilationTestSettings(input='file.exe', pdb='file.pdb')
        self.assertFalse(settings.has_multiple_pdbs())

    def test_duplicate_pdbs_are_merged(self):
        settings = DecompilationTestSettings(input='file.exe', pdb=['file.pdb', 'file.pdb'])
        self.assertEqual(settings.pdb, 'file.pdb')

        settings = DecompilationTestSettings(
            input='file.exe',
            pdb=['file.pdb', 'other.pdb', 'file.pdb']
        )
        self.assertEqual(settings.pdb, ['file.pdb', 'other.pdb'])

    def test_config_passed_to_constructor_is_accessible(self):
        CONFIG = 'file.json'
        settings = DecompilationTestSettings(input='file.exe', config=CONFIG)
        self.assertEqual(CONFIG, settings.config)

    def test_config_as_list_returns_empty_list_if_config_is_not_set(self):
        settings = DecompilationTestSettings(input='file.exe', config=None)
        self.assertEqual([], settings.config_as_list)

    def test_config_as_list_returns_config_when_config_is_list(self):
        CONFIG = ['file1.json', 'file2.json']
        settings = DecompilationTestSettings(input='file.exe', config=CONFIG)
        self.assertEqual(CONFIG, settings.config_as_list)

    def test_config_as_list_returns_list_when_config_is_single_file(self):
        CONFIG = 'file.json'
        settings = DecompilationTestSettings(input='file.exe', config=CONFIG)
        self.assertEqual([CONFIG], settings.config_as_list)

    def test_has_multiple_configs_returns_true_when_there_are_multiple_configs(self):
        settings = DecompilationTestSettings(input='file.exe', config=['file1.json', 'file2.json'])
        self.assertTrue(settings.has_multiple_configs())

    def test_has_multiple_configs_returns_false_when_there_is_just_single_config(self):
        settings = DecompilationTestSettings(input='file.exe', config='file.json')
        self.assertFalse(settings.has_multiple_configs())

    def test_duplicate_configs_are_merged(self):
        settings = DecompilationTestSettings(input='file.exe', config=['file.json', 'file.json'])
        self.assertEqual(settings.config, 'file.json')

        settings = DecompilationTestSettings(
            input='file.exe',
            config=['file.json', 'other.json', 'file.json']
        )
        self.assertEqual(settings.config, ['file.json', 'other.json'])

    def test_static_code_archive_passed_to_constructor_is_accessible(self):
        STATIC_CODE_ARCHIVE = 'file.a'
        settings = DecompilationTestSettings(input='file.exe', static_code_archive=STATIC_CODE_ARCHIVE)
        self.assertEqual(STATIC_CODE_ARCHIVE, settings.static_code_archive)

    def test_static_code_archive_as_list_returns_empty_list_if_static_code_archive_is_not_set(self):
        settings = DecompilationTestSettings(input='file.exe', static_code_archive=None)
        self.assertEqual([], settings.static_code_archive_as_list)

    def test_static_code_archive_as_list_returns_static_code_archive_when_static_code_archive_is_list(self):
        STATIC_CODE_ARCHIVE = ['file1.a', 'file2.a']
        settings = DecompilationTestSettings(input='file.exe', static_code_archive=STATIC_CODE_ARCHIVE)
        self.assertEqual(STATIC_CODE_ARCHIVE, settings.static_code_archive_as_list)

    def test_static_code_archive_as_list_returns_list_when_static_code_archive_is_single_file(self):
        STATIC_CODE_ARCHIVE = 'file.a'
        settings = DecompilationTestSettings(input='file.exe', static_code_archive=STATIC_CODE_ARCHIVE)
        self.assertEqual([STATIC_CODE_ARCHIVE], settings.static_code_archive_as_list)

    def test_has_multiple_static_code_archives_returns_true_when_there_are_multiple_static_code_archives(self):
        settings = DecompilationTestSettings(input='file.exe', static_code_archive=['file1.a', 'file2.a'])
        self.assertTrue(settings.has_multiple_static_code_archives())

    def test_has_multiple_static_code_archives_returns_false_when_there_is_just_single_static_code_archive(self):
        settings = DecompilationTestSettings(input='file.exe', static_code_archive='file.a')
        self.assertFalse(settings.has_multiple_static_code_archives())

    def test_duplicate_static_code_archives_are_merged(self):
        settings = DecompilationTestSettings(input='file.exe', static_code_archive=['file.a', 'file.a'])
        self.assertEqual(settings.static_code_archive, 'file.a')

        settings = DecompilationTestSettings(
            input='file.exe',
            static_code_archive=['file.a', 'other.a', 'file.a']
        )
        self.assertEqual(settings.static_code_archive, ['file.a', 'other.a'])

    def test_static_code_sigfile_passed_to_constructor_is_accessible(self):
        STATIC_CODE_SIGFILE = 'file.sig'
        settings = DecompilationTestSettings(input='file.exe', static_code_sigfile=STATIC_CODE_SIGFILE)
        self.assertEqual(STATIC_CODE_SIGFILE, settings.static_code_sigfile)

    def test_static_code_sigfile_as_list_returns_empty_list_if_static_code_sigfile_is_not_set(self):
        settings = DecompilationTestSettings(input='file.exe', static_code_sigfile=None)
        self.assertEqual([], settings.static_code_sigfile_as_list)

    def test_static_code_sigfile_as_list_returns_static_code_sigfile_when_static_code_sigfile_is_list(self):
        STATIC_CODE_SIGFILE = ['file1.sig', 'file2.sig']
        settings = DecompilationTestSettings(input='file.exe', static_code_sigfile=STATIC_CODE_SIGFILE)
        self.assertEqual(STATIC_CODE_SIGFILE, settings.static_code_sigfile_as_list)

    def test_static_code_sigfile_as_list_returns_list_when_static_code_sigfile_is_single_file(self):
        STATIC_CODE_SIGFILE = 'file.sig'
        settings = DecompilationTestSettings(input='file.exe', static_code_sigfile=STATIC_CODE_SIGFILE)
        self.assertEqual([STATIC_CODE_SIGFILE], settings.static_code_sigfile_as_list)

    def test_has_multiple_static_code_sigfiles_returns_true_when_there_are_multiple_static_code_sigfiles(self):
        settings = DecompilationTestSettings(input='file.exe', static_code_sigfile=['file1.sig', 'file2.sig'])
        self.assertTrue(settings.has_multiple_static_code_sigfiles())

    def test_has_multiple_static_code_sigfiles_returns_false_when_there_is_just_single_static_code_sigfile(self):
        settings = DecompilationTestSettings(input='file.exe', static_code_sigfile='file.sig')
        self.assertFalse(settings.has_multiple_static_code_sigfiles())

    def test_duplicate_static_code_sigfiles_are_merged(self):
        settings = DecompilationTestSettings(input='file.exe', static_code_sigfile=['file.sig', 'file.sig'])
        self.assertEqual(settings.static_code_sigfile, 'file.sig')

        settings = DecompilationTestSettings(
            input='file.exe',
            static_code_sigfile=['file.sig', 'other.sig', 'file.sig']
        )
        self.assertEqual(settings.static_code_sigfile, ['file.sig', 'other.sig'])

    def test_arch_passed_to_constructor_is_accessible(self):
        ARCH = 'x86'
        settings = DecompilationTestSettings(input='file.exe', arch=ARCH)
        self.assertEqual(ARCH, settings.arch)

    def test_arch_as_list_returns_empty_list_if_arch_is_not_set(self):
        settings = DecompilationTestSettings(input='file.exe')
        self.assertEqual([], settings.arch_as_list)

    def test_arch_as_list_returns_arch_when_arch_is_list(self):
        ARCH = ['x86', 'arm']
        settings = DecompilationTestSettings(input='file.exe', arch=ARCH)
        self.assertEqual(ARCH, settings.arch_as_list)

    def test_arch_as_list_returns_list_when_there_is_single_arch(self):
        ARCH = 'x86'
        settings = DecompilationTestSettings(input='file.exe', arch=ARCH)
        self.assertEqual([ARCH], settings.arch_as_list)

    def test_has_multiple_archs_returns_true_when_there_are_multiple_archs(self):
        settings = DecompilationTestSettings(input='file.exe', arch=['x86', 'arm'])
        self.assertTrue(settings.has_multiple_archs())

    def test_has_multiple_archs_returns_false_when_there_is_just_single_arch(self):
        settings = DecompilationTestSettings(input='file.exe', arch='x86')
        self.assertFalse(settings.has_multiple_archs())

    def test_duplicate_archs_are_merged(self):
        settings = DecompilationTestSettings(input=['file.exe'], arch=['x86', 'x86'])
        self.assertEqual(settings.arch, 'x86')

        settings = DecompilationTestSettings(input=['file.exe'], arch=['x86', 'arm', 'x86'])
        self.assertEqual(settings.arch, ['x86', 'arm'])

    def test_format_passed_to_constructor_is_accessible(self):
        FORMAT = 'elf'
        settings = DecompilationTestSettings(input='file.exe', format=FORMAT)
        self.assertEqual(FORMAT, settings.format)

    def test_format_as_list_returns_empty_list_if_format_is_not_set(self):
        settings = DecompilationTestSettings(input='file.exe')
        self.assertEqual([], settings.format_as_list)

    def test_format_as_list_returns_format_when_format_is_list(self):
        FORMAT = ['elf', 'pe']
        settings = DecompilationTestSettings(input='file.exe', format=FORMAT)
        self.assertEqual(FORMAT, settings.format_as_list)

    def test_format_as_list_returns_list_when_there_is_single_format(self):
        FORMAT = 'elf'
        settings = DecompilationTestSettings(input='file.exe', format=FORMAT)
        self.assertEqual([FORMAT], settings.format_as_list)

    def test_has_multiple_formats_returns_true_when_there_are_multiple_formats(self):
        settings = DecompilationTestSettings(input='file.exe', format=['elf', 'pe'])
        self.assertTrue(settings.has_multiple_formats())

    def test_has_multiple_formats_returns_false_when_there_is_just_single_format(self):
        settings = DecompilationTestSettings(input='file.exe', format='elf')
        self.assertFalse(settings.has_multiple_formats())

    def test_duplicate_formats_are_merged(self):
        settings = DecompilationTestSettings(input=['file.exe'], format=['elf', 'elf'])
        self.assertEqual(settings.format, 'elf')

        settings = DecompilationTestSettings(input=['file.exe'], format=['elf', 'pe', 'elf'])
        self.assertEqual(settings.format, ['elf', 'pe'])

    def test_mode_passed_to_constructor_is_accessible(self):
        MODE = 'bin'
        settings = DecompilationTestSettings(input='file.exe', mode=MODE)
        self.assertEqual(MODE, settings.mode)

    def test_mode_or_default_returns_mode_when_set(self):
        mode = 'raw'
        settings = DecompilationTestSettings(input='file.exe', mode=mode)
        self.assertEqual(mode, settings.mode_or_default)

    def test_mode_or_default_returns_default_mode_when_mode_is_not_set(self):
        settings = DecompilationTestSettings(input='file.exe')
        self.assertEqual(settings.mode_or_default, 'bin')

    def test_mode_as_list_returns_empty_list_if_mode_is_not_set(self):
        settings = DecompilationTestSettings(input='file.exe')
        self.assertEqual([], settings.mode_as_list)

    def test_mode_as_list_returns_mode_when_mode_is_list(self):
        MODE = ['bin', 'raw']
        settings = DecompilationTestSettings(input='file.exe', mode=MODE)
        self.assertEqual(MODE, settings.mode_as_list)

    def test_mode_as_list_returns_list_when_there_is_single_mode(self):
        MODE = 'bin'
        settings = DecompilationTestSettings(input='file.exe', mode=MODE)
        self.assertEqual([MODE], settings.mode_as_list)

    def test_has_multiple_modes_returns_true_when_there_are_multiple_modes(self):
        settings = DecompilationTestSettings(input='file.exe', mode=['bin', 'raw'])
        self.assertTrue(settings.has_multiple_modes())

    def test_has_multiple_modes_returns_false_when_there_is_just_single_mode(self):
        settings = DecompilationTestSettings(input='file.exe', mode='bin')
        self.assertFalse(settings.has_multiple_modes())

    def test_duplicate_modes_are_merged(self):
        settings = DecompilationTestSettings(input=['file.exe'], mode=['bin', 'bin'])
        self.assertEqual(settings.mode, 'bin')

    def test_hll_passed_to_constructor_is_accessible(self):
        HLL = 'c'
        settings = DecompilationTestSettings(input='file.exe', hll=HLL)
        self.assertEqual(HLL, settings.hll)

    def test_hll_as_list_returns_empty_list_if_hll_is_not_set(self):
        settings = DecompilationTestSettings(input='file.exe')
        self.assertEqual([], settings.hll_as_list)

    def test_hll_as_list_returns_hll_when_hll_is_list(self):
        HLL = ['c', 'py']
        settings = DecompilationTestSettings(input='file.exe', hll=HLL)
        self.assertEqual(HLL, settings.hll_as_list)

    def test_hll_as_list_returns_list_when_there_is_single_hll(self):
        HLL = 'c'
        settings = DecompilationTestSettings(input='file.exe', hll=HLL)
        self.assertEqual([HLL], settings.hll_as_list)

    def test_has_multiple_hlls_returns_true_when_there_are_multiple_hlls(self):
        settings = DecompilationTestSettings(input='file.exe', hll=['c', 'py'])
        self.assertTrue(settings.has_multiple_hlls())

    def test_has_multiple_hlls_returns_false_when_there_is_just_single_hll(self):
        settings = DecompilationTestSettings(input='file.exe', hll='c')
        self.assertFalse(settings.has_multiple_hlls())

    def test_duplicate_hlls_are_merged(self):
        settings = DecompilationTestSettings(input=['file.exe'], hll=['c', 'c'])
        self.assertEqual(settings.hll, 'c')

        settings = DecompilationTestSettings(input=['file.exe'], hll=['c', 'py', 'c'])
        self.assertEqual(settings.hll, ['c', 'py'])

    def test_ar_index_passed_to_constructor_is_accessible(self):
        AR_INDEX = 0
        settings = DecompilationTestSettings(input='archive.a', ar_index=AR_INDEX)
        self.assertEqual(AR_INDEX, settings.ar_index)

    def test_ar_index_as_list_returns_empty_list_if_ar_index_is_not_set(self):
        settings = DecompilationTestSettings(input='archive.a')
        self.assertEqual([], settings.ar_index_as_list)

    def test_ar_index_as_list_returns_ar_index_when_ar_index_is_list(self):
        AR_INDEX = [0, 1]
        settings = DecompilationTestSettings(input='archive.a', ar_index=AR_INDEX)
        self.assertEqual(AR_INDEX, settings.ar_index_as_list)

    def test_ar_index_as_list_returns_list_when_there_is_single_ar_index(self):
        AR_INDEX = 0
        settings = DecompilationTestSettings(input='archive.a', ar_index=AR_INDEX)
        self.assertEqual([AR_INDEX], settings.ar_index_as_list)

    def test_has_multiple_ar_indexes_returns_true_when_there_are_multiple_ar_indexes(self):
        settings = DecompilationTestSettings(input='archive.a', ar_index=[0, 1])
        self.assertTrue(settings.has_multiple_ar_indexes())

    def test_has_multiple_ar_indexes_returns_false_when_there_is_just_single_ar_index(self):
        settings = DecompilationTestSettings(input='archive.a', ar_index=0)
        self.assertFalse(settings.has_multiple_ar_indexes())

    def test_duplicate_ar_indexes_are_merged(self):
        settings = DecompilationTestSettings(input=['archive.a'], ar_index=[0, 0])
        self.assertEqual(settings.ar_index, 0)

        settings = DecompilationTestSettings(input=['archive.a'], ar_index=[0, 1, 0])
        self.assertEqual(settings.ar_index, [0, 1])

    def test_ar_name_passed_to_constructor_is_accessible(self):
        AR_NAME = 'file.o'
        settings = DecompilationTestSettings(input='archive.a', ar_name=AR_NAME)
        self.assertEqual(AR_NAME, settings.ar_name)

    def test_ar_name_as_list_returns_empty_list_if_ar_name_is_not_set(self):
        settings = DecompilationTestSettings(input='archive.a')
        self.assertEqual([], settings.ar_name_as_list)

    def test_ar_name_as_list_returns_ar_name_when_ar_name_is_list(self):
        AR_NAME = ['file1.o', 'file2.o']
        settings = DecompilationTestSettings(input='archive.a', ar_name=AR_NAME)
        self.assertEqual(AR_NAME, settings.ar_name_as_list)

    def test_ar_name_as_list_returns_list_when_there_is_single_ar_name(self):
        AR_NAME = 'file.o'
        settings = DecompilationTestSettings(input='archive.a', ar_name=AR_NAME)
        self.assertEqual([AR_NAME], settings.ar_name_as_list)

    def test_has_multiple_ar_names_returns_true_when_there_are_multiple_ar_names(self):
        settings = DecompilationTestSettings(
            input='archive.a',
            ar_name=['file1.o', 'file2.o']
        )
        self.assertTrue(settings.has_multiple_ar_names())

    def test_has_multiple_ar_names_returns_false_when_there_is_just_single_ar_name(self):
        settings = DecompilationTestSettings(input='archive.a', ar_name='file.o')
        self.assertFalse(settings.has_multiple_ar_names())

    def test_duplicate_ar_names_are_merged(self):
        settings = DecompilationTestSettings(
            input=['archive.a'],
            ar_name=['file.o', 'file.o']
        )
        self.assertEqual(settings.ar_name, 'file.o')

        settings = DecompilationTestSettings(
            input=['archive.a'],
            ar_name=['file1.o', 'file2.o', 'file1.o']
        )
        self.assertEqual(settings.ar_name, ['file1.o', 'file2.o'])

    def test_tool_arguments_class_returns_correct_value(self):
        settings = DecompilationTestSettings(input='file.exe')
        self.assertEqual(settings.tool_arguments_class, DecompilationArguments)

    def test_tool_runner_class_returns_correct_value(self):
        settings = DecompilationTestSettings(input='file.exe')
        self.assertEqual(settings.tool_runner_class, DecompilationRunner)

    def test_tool_test_class_returns_correct_value(self):
        settings = DecompilationTestSettings(input='file.exe')
        self.assertEqual(settings.tool_test_class, DecompilationTest)
