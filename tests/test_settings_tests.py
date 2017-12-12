"""
    Tests for the :mod:`regression_tests.test_settings` module.
"""

import unittest

from regression_tests.test_settings import CriticalTestSettings
from regression_tests.test_settings import InvalidTestSettingsError
from regression_tests.test_settings import TestSettings
from regression_tests.tools.decompilation_test_settings import DecompilationTestSettings


class TestSettingsTests(unittest.TestCase):
    """Tests for `TestSettings`."""

    def test_creates_decompilation_test_settings_when_tool_is_not_specified(self):
        settings = TestSettings(input='file.exe')
        self.assertIsInstance(settings, DecompilationTestSettings)

    def test_raises_exception_when_no_viable_test_settings_are_found(self):
        with self.assertRaisesRegex(InvalidTestSettingsError, r".*tool=None.*"):
            TestSettings(tool=None, input='file.exe')

    def test_raises_exception_when_unsupported_argument_is_found(self):
        with self.assertRaisesRegex(InvalidTestSettingsError, r".*xxx='yyy'.*"):
            TestSettings(input='file.exe', xxx='yyy')

    def test_settings_are_not_critical(self):
        settings = TestSettings(input='file.exe')
        self.assertFalse(settings.critical)

    def test_outpus_dir_name_returns_correct_value(self):
        settings = TestSettings(input='file.exe')
        self.assertEqual(settings.outputs_dir_name, 'outputs')

    def scenario_combinations_returns_given_combinations(
            self, settings, ref_combinations):
        combinations = settings.combinations
        self.assertEqual(combinations, ref_combinations)

    def test_combinations_returns_same_settings_when_there_are_no_lists(self):
        settings = DecompilationTestSettings(
            input='file.exe',
            arch='x86',
            format='elf',
            mode='bin',
            hll='c',
            ar_index=0,
            ar_name='file.o',
            args='--arg'
        )
        ref_combinations = [settings]
        self.scenario_combinations_returns_given_combinations(
            settings, ref_combinations)

    def test_combinations_returns_two_settings_when_there_are_two_inputs(self):
        settings = DecompilationTestSettings(
            input=['file1.exe', 'file2.exe']
        )
        ref_combinations = [
            DecompilationTestSettings(
                input='file1.exe'
            ),
            DecompilationTestSettings(
                input='file2.exe'
            )
        ]
        self.scenario_combinations_returns_given_combinations(
            settings, ref_combinations)

    def test_combinations_returns_two_settings_when_there_are_two_archs(self):
        settings = DecompilationTestSettings(
            input='file.exe',
            arch=['x86', 'arm']
        )
        ref_combinations = [
            DecompilationTestSettings(
                input='file.exe',
                arch='x86'
            ),
            DecompilationTestSettings(
                input='file.exe',
                arch='arm'
            )
        ]
        self.scenario_combinations_returns_given_combinations(
            settings, ref_combinations)

    def test_combinations_returns_two_settings_when_there_are_two_formats(self):
        settings = DecompilationTestSettings(
            input='file.exe',
            format=['elf', 'pe']
        )
        ref_combinations = [
            DecompilationTestSettings(
                input='file.exe',
                format='elf'
            ),
            DecompilationTestSettings(
                input='file.exe',
                format='pe'
            )
        ]
        self.scenario_combinations_returns_given_combinations(
            settings, ref_combinations)

    def test_combinations_returns_two_settings_when_there_are_two_modes(self):
        settings = DecompilationTestSettings(
            input='file',
            mode=['bin', 'raw']
        )
        ref_combinations = [
            DecompilationTestSettings(
                input='file',
                mode='bin'
            ),
            DecompilationTestSettings(
                input='file',
                mode='raw'
            )
        ]
        self.scenario_combinations_returns_given_combinations(
            settings, ref_combinations)

    def test_combinations_returns_two_settings_when_there_are_two_hlls(self):
        settings = DecompilationTestSettings(
            input='file.exe',
            hll=['c', 'py']
        )
        ref_combinations = [
            DecompilationTestSettings(
                input='file.exe',
                hll='c'
            ),
            DecompilationTestSettings(
                input='file.exe',
                hll='py'
            )
        ]
        self.scenario_combinations_returns_given_combinations(
            settings, ref_combinations)

    def test_combinations_returns_two_settings_when_there_are_two_ar_indexes(self):
        settings = DecompilationTestSettings(
            input='archive.a',
            ar_index=[0, 1]
        )
        ref_combinations = [
            DecompilationTestSettings(
                input='archive.a',
                ar_index=0
            ),
            DecompilationTestSettings(
                input='archive.a',
                ar_index=1
            )
        ]
        self.scenario_combinations_returns_given_combinations(
            settings, ref_combinations)

    def test_combinations_returns_two_settings_when_there_are_two_ar_names(self):
        settings = DecompilationTestSettings(
            input='archive.a',
            ar_name=['file1.o', 'file2.o']
        )
        ref_combinations = [
            DecompilationTestSettings(
                input='archive.a',
                ar_name='file1.o'
            ),
            DecompilationTestSettings(
                input='archive.a',
                ar_name='file2.o'
            )
        ]
        self.scenario_combinations_returns_given_combinations(
            settings, ref_combinations)

    def test_combinations_returns_two_settings_when_there_are_two_args(self):
        settings = DecompilationTestSettings(
            input='file.exe',
            args=['--arg1', '--arg2']
        )
        ref_combinations = [
            DecompilationTestSettings(
                input='file.exe',
                args='--arg1'
            ),
            DecompilationTestSettings(
                input='file.exe',
                args='--arg2'
            )
        ]
        self.scenario_combinations_returns_given_combinations(
            settings, ref_combinations)

    def test_clone_returns_other_settings_equal_to_original_settings(self):
        settings = TestSettings(
            input='file.exe',
            arch='x86',
            format='elf',
            mode='bin',
            hll='c',
            ar_index=0,
            ar_name='file.o',
            args='--arg'
        )
        cloned_settings = settings.clone()
        self.assertIsNot(settings, cloned_settings)
        self.assertEqual(settings, cloned_settings)

    def test_clone_but_input_clones_settings_and_sets_different_input(self):
        settings = TestSettings(
            input='file.exe',
            arch='x86',
            format='elf',
            mode='bin',
            hll='c',
            ar_index=0,
            ar_name='file.o',
            args='--arg'
        )
        cloned_settings = settings.clone_but(input='file2.exe')
        self.assertEqual(settings.arch, cloned_settings.arch)
        self.assertEqual(settings.format, cloned_settings.format)
        self.assertEqual(settings.mode, cloned_settings.mode)
        self.assertEqual(settings.hll, cloned_settings.hll)
        self.assertEqual(settings.ar_index, cloned_settings.ar_index)
        self.assertEqual(settings.ar_name, cloned_settings.ar_name)
        self.assertEqual(settings.args, cloned_settings.args)
        self.assertEqual(cloned_settings.input, 'file2.exe')

    def test_from_settings_works_correctly_without_redefinitions(self):
        base_settings = TestSettings(input='file.exe', arch='x86')
        settings = TestSettings.from_settings(base_settings)
        self.assertEqual(settings.input, 'file.exe')
        self.assertEqual(settings.arch, 'x86')

    def test_from_settings_works_correctly_with_redefinitions(self):
        base_settings = TestSettings(input='file.exe', arch='x86')
        settings = TestSettings.from_settings(base_settings, arch='arm')
        self.assertEqual(settings.input, 'file.exe')
        self.assertEqual(settings.arch, 'arm')

    def test_supported_attr_names_returns_alphabetically_ordered_list(self):
        # Even though the method is internal, we test it nevertheless to ensure
        # that it returns an ordered list because this behavior is VERY
        # important. It would be impossible to test it indirectly (through a
        # public method) because the order in which attributes are stored in
        # __dict__ differs between interpreter instance runs, and all tests are
        # run in a single interpreter instance.
        settings = DecompilationTestSettings(input='file.exe')
        self.assertEqual(
            settings._supported_attr_names(),
            [
                'ar_index',
                'ar_name',
                'arch',
                'args',
                'config',
                'format',
                'hll',
                'input',
                'mode',
                'pdb',
                'static_code_archive',
                'static_code_sigfile',
                'timeout',
                'tool'
            ]
        )

    def test_two_settings_having_same_data_are_equal(self):
        settings1 = TestSettings(
            input=['file1.exe', 'file2.exe'],
            arch='x86',
            format='elf',
            mode='bin',
            hll='c',
            ar_index=0,
            ar_name='file.o',
            args='--arg'
        )
        settings2 = TestSettings(
            input=['file1.exe', 'file2.exe'],
            arch='x86',
            format='elf',
            mode='bin',
            hll='c',
            ar_index=0,
            ar_name='file.o',
            args='--arg'
        )
        self.assertEqual(settings1, settings2)

    def test_two_settings_having_different_input_are_not_equal(self):
        settings1 = TestSettings(
            input='file1.exe'
        )
        settings2 = TestSettings(
            input='file2.exe'
        )
        self.assertNotEqual(settings1, settings2)

    def test_two_settings_having_different_arch_are_not_equal(self):
        settings1 = TestSettings(
            input='file.exe',
            arch='x86'
        )
        settings2 = TestSettings(
            input='file.exe',
            arch='arm'
        )
        self.assertNotEqual(settings1, settings2)

    def test_two_settings_having_different_format_are_not_equal(self):
        settings1 = TestSettings(
            input='file.exe',
            format='elf'
        )
        settings2 = TestSettings(
            input='file.exe',
            format='pe'
        )
        self.assertNotEqual(settings1, settings2)

    def test_two_settings_having_different_mode_are_not_equal(self):
        settings1 = TestSettings(
            input='file.exe',
            mode='raw'
        )
        settings2 = TestSettings(
            input='file.exe',
            mode='bin'
        )
        self.assertNotEqual(settings1, settings2)

    def test_two_settings_having_different_hll_are_not_equal(self):
        settings1 = TestSettings(
            input='file.exe',
            hll='c'
        )
        settings2 = TestSettings(
            input='file.exe',
            hll='py'
        )
        self.assertNotEqual(settings1, settings2)

    def test_two_settings_having_different_ar_index_are_not_equal(self):
        settings1 = TestSettings(
            input='archive.a',
            ar_index=0
        )
        settings2 = TestSettings(
            input='archive.a',
            ar_index=1
        )
        self.assertNotEqual(settings1, settings2)

    def test_two_settings_having_different_ar_name_are_not_equal(self):
        settings1 = TestSettings(
            input='archive.a',
            ar_name='file1.o'
        )
        settings2 = TestSettings(
            input='archive.a',
            ar_name='file2.o'
        )
        self.assertNotEqual(settings1, settings2)

    def test_two_settings_having_different_args_are_not_equal(self):
        settings1 = TestSettings(
            input='file.exe',
            args='c'
        )
        settings2 = TestSettings(
            input='file.exe',
            args='py'
        )
        self.assertNotEqual(settings1, settings2)

    def test_repr_returns_executable_repr_that_creates_original_settings(self):
        settings = TestSettings(
            input=['file1.exe', 'file2.exe'],
            arch='x86',
            format='elf',
            mode='bin',
            hll='c',
            ar_index=0,
            ar_name='file.o',
            args='--arg'
        )
        self.assertEqual(settings, eval(repr(settings)))


class CriticalTestSettingsTests(unittest.TestCase):
    """Tests for `CriticalTestSettings`."""

    def test_settings_are_critical(self):
        settings = CriticalTestSettings(input='file.exe')
        self.assertTrue(settings.critical)
