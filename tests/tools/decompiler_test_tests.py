"""
    Tests for the :mod:`regression_tests.tools.decompiler_test` module.
"""

import abc
import re
import unittest
from unittest import mock

from regression_tests.parsers.config_parser import Config
from regression_tests.parsers.fileinfo_output_parser import FileinfoOutput
from regression_tests.test_settings import TestSettings
from regression_tests.tools.decompiler import Decompiler
from regression_tests.tools.decompiler_test import DecompilerTest
from regression_tests.utils.os import on_windows
from tests.matchers import AnyStrWith
from tests.matchers import Anything


class BaseDecompilerTestTests(unittest.TestCase):
    """A base class for all tests of `DecompilerTest`."""

    def setUp(self):
        self.decompiler = mock.Mock(spec_set=Decompiler)

    # The method cannot be named 'create_test' because unittest then treats it
    # as a test method.
    def create(self, test_settings):
        """Creates an instance of `DecompilerTest` with the given settings.
        """
        return DecompilerTest(self.decompiler, test_settings)

    def is_gcc(self, args):
        """Checks if GCC is run in the given arguments."""
        # On Windows, GCC is run via `sh.exe windows-gcc-X.sh` instead of `gcc`.
        if on_windows():
            return len(args[0]) > 1 and args[0][1].startswith('windows-gcc-')
        return args[0][0] == 'gcc'


class DecompilerTestTests(BaseDecompilerTestTests):
    """Tests for `DecompilerTest`."""

    def test_decomp_returns_given_decompilation(self):
        test = self.create(TestSettings(input='file.exe'))
        self.assertEqual(test.decompiler, self.decompiler)

    def test_decomp_cannot_be_changed(self):
        test = self.create(TestSettings(input='file.exe'))
        with self.assertRaises(AttributeError):
            test.decompiler = mock.Mock(spec_set=Decompiler)

    def test_out_c_returns_same_result_as_decomp_out_c(self):
        test = self.create(TestSettings(input='file.exe'))
        self.assertEqual(test.out_c, test.decompiler.out_c)

    def test_out_dsm_returns_same_result_as_decomp_out_dsm(self):
        test = self.create(TestSettings(input='file.exe'))
        self.assertEqual(test.out_dsm, test.decompiler.out_dsm)

    def test_out_ll_returns_same_result_as_decomp_out_ll(self):
        test = self.create(TestSettings(input='file.exe'))
        self.assertEqual(test.out_ll, test.decompiler.out_ll)

    def test_out_config_returns_same_result_as_decomp_out_config(self):
        test = self.create(TestSettings(input='file.json'))
        self.assertEqual(test.out_config, test.decompiler.out_config)

    def test_settings_returns_given_test_settings(self):
        TEST_SETTINGS = TestSettings(input='file.exe')
        test = self.create(TEST_SETTINGS)
        self.assertEqual(test.settings, TEST_SETTINGS)

    def test_settings_cannot_be_changed(self):
        test = self.create(TestSettings(input='file.exe'))
        with self.assertRaises(AttributeError):
            test.settings = TestSettings(input='file.exe')


class WithDecompilerTestTests(BaseDecompilerTestTests):
    """A base class for all tests with a `DecompilerTest` instance."""

    def setUp(self):
        super().setUp()
        self.test = self.create(TestSettings(input='file.exe'))


class DecompilerTestSetUpTests(WithDecompilerTestTests):
    """Tests for `DecompilerTest.setUp()`."""

    def test_raises_assertion_error_with_output_when_decompilation_timeouted(self):
        self.decompiler.name = 'decompiler'
        self.decompiler.end_of_output.return_value = 'END OF OUTPUT'
        type(self.decompiler).timeouted = mock.PropertyMock(return_value=1)
        with self.assertRaisesRegex(
                AssertionError,
                re.compile(r'.*decompiler.*timeouted.*END OF OUTPUT.*', re.DOTALL)):
            self.test.setUp()

    def test_raises_assertion_error_with_output_when_decompilation_failed(self):
        self.decompiler.name = 'decompiler'
        self.decompiler.end_of_output.return_value = 'END OF OUTPUT'
        type(self.decompiler).timeouted = mock.PropertyMock(return_value=0)
        type(self.decompiler).return_code = mock.PropertyMock(return_value=1)
        with self.assertRaisesRegex(
                AssertionError,
                re.compile(r'.*decompiler.*failed.*END OF OUTPUT.*', re.DOTALL)):
            self.test.setUp()


class BaseCompilationAssertionsTests(WithDecompilerTestTests):
    """A base class for all assertions concerning compilation."""

    def setUp(self):
        super().setUp()
        self.decompiler.dir.get_file().exists.return_value = False
        type(self.decompiler.input_file).name = mock.PropertyMock(return_value='file.exe')
        type(self.decompiler.out_c_file).name = mock.PropertyMock(return_value='file.out.c')
        self.decompiler.out_c_file.renamed().exists.return_value = False
        self.decompiler.fileinfo_outputs = []

        def run_cmd_side_effect(*args, **kwargs):
            return '', 0, False
        self.decompiler._run_cmd.side_effect = run_cmd_side_effect

    @abc.abstractmethod
    def run_method_so_it_succeeds(self):
        """Runs the tested method so it succeeds."""
        raise NotImplementedError

    def scenario_out_c_is_fixed_for_arch_when_input_is_c(self, arch):
        self.test = self.create(TestSettings(input='file.exe', arch=arch))

        self._check_out_c_gets_fixed()

    def scenario_out_c_is_fixed_for_arch_when_input_is_binary(self, arch):
        self.test = self.create(TestSettings(input='file.exe'))
        # For binary files, the architecture is obtained from fileinfo (writers
        # of regression tests do not usually specify the architecture for
        # binary files because such a specification is useless).
        #
        # We also test that the architecture is parsed properly.
        self.decompiler.fileinfo_outputs = [
            FileinfoOutput(
                '\n...\nArchitecture: {} (some irrelevant arch info)\n...'.format(
                    arch
                )
            )
        ]

        self._check_out_c_gets_fixed()

    def scenario_out_c_is_fixed_when_needed_for_c_file(self):
        self.scenario_out_c_is_fixed_for_arch_when_input_is_c('arm')
        self.scenario_out_c_is_fixed_for_arch_when_input_is_c('x86')

    def scenario_out_c_is_fixed_when_needed_for_binary_file(self):
        # fileinfo emits 'ARM ...' for the ARM architecture, so use uppercase
        # ARM to match the test with the real output from fileinfo.
        self.scenario_out_c_is_fixed_for_arch_when_input_is_binary('ARM')
        self.scenario_out_c_is_fixed_for_arch_when_input_is_binary('x86')

    def scenario_passes_m32_to_gcc_by_default(self):
        self.run_method_so_it_succeeds()

        for call in self.decompiler._run_cmd.call_args_list:
            # We need to check only positional arguments.
            if '-m32' in call[0][0]:
                break
        else:  # nobreak
            self.fail('did not find any calls to GCC with -m32')

    def scenario_passes_m64_to_gcc_when_decompiling_64b_binary(self):
        self.decompiler.out_config = Config("""{
            "architecture": {
                "bitSize": 64
            }
        }""")

        self.run_method_so_it_succeeds()

        for call in self.decompiler._run_cmd.call_args_list:
            # We need to check only positional arguments.
            if '-m64' in call[0][0]:
                break
        else:  # nobreak
            self.fail('did not find any calls to GCC with -m64')

    def _check_out_c_gets_fixed(self):
        type(self.decompiler).out_c = mock.PropertyMock(return_value='')
        self.decompiler.dir.store_file.reset_mock()

        self.run_method_so_it_succeeds()

        self.decompiler.dir.store_file.assert_called_once_with(
            Anything(),
            AnyStrWith('.*COMPILATION.*')
        )


class TestAssertCProducesOutputWhenRunTests(BaseCompilationAssertionsTests):
    """Tests for `DecompilerTest.assert_c_produces_output_when_run()`."""

    def test_raises_assertion_error_when_output_file_is_not_c_file(self):
        self.decompiler.out_hll_is_c.return_value = False
        self.test = self.create(TestSettings(input='file.exe'))
        with self.assertRaisesRegex(AssertionError, r'.*C file.*'):
            self.test.assert_c_produces_output_when_run('input', 'expected output')

    def test_raises_assertion_error_when_file_fails_to_compile(self):
        def run_cmd_side_effect(*args, **kwargs):
            if self.is_gcc(args):
                return 'error: xxx', 1, False
            return '', 0, False
        self.decompiler._run_cmd.side_effect = run_cmd_side_effect
        with self.assertRaisesRegex(
                AssertionError,
                r'.*compil.*output:\serror: xxx.*'):
            self.test.assert_c_produces_output_when_run('input', 'expected output')

    def test_raises_assertion_error_when_compiled_file_run_timeouts(self):
        def run_cmd_side_effect(*args, **kwargs):
            if self.is_gcc(args):
                return '', 0, False
            return 'timeout', 1, True
        self.decompiler._run_cmd.side_effect = run_cmd_side_effect
        with self.assertRaisesRegex(AssertionError, r'.*timeouted.*'):
            self.test.assert_c_produces_output_when_run('input', 'expected output')

    def test_raises_assertion_error_when_outputs_differ(self):
        def run_cmd_side_effect(*args, **kwargs):
            return 'other than expected output', 0, False
        self.decompiler._run_cmd.side_effect = run_cmd_side_effect
        with self.assertRaisesRegex(
                AssertionError,
                r'.*other than expected output.*!=.*expected output.*'):
            self.test.assert_c_produces_output_when_run('input', 'expected output')

    def test_raises_assertion_error_when_return_codes_differ(self):
        def run_cmd_side_effect(*args, **kwargs):
            if self.is_gcc(args):
                return '', 0, False
            return 'expected output', 5, False
        self.decompiler._run_cmd.side_effect = run_cmd_side_effect
        with self.assertRaisesRegex(AssertionError, r'.*5.*!=.*0.*'):
            self.test.assert_c_produces_output_when_run(
                'input',
                'expected output',
                expected_return_code=0
            )

    def run_method_so_it_succeeds(self):
        def run_cmd_side_effect(*args, **kwargs):
            return 'expected output', 0, False
        self.decompiler._run_cmd.side_effect = run_cmd_side_effect
        self.test.assert_c_produces_output_when_run('input', 'expected output')

    def test_out_c_is_fixed_when_needed(self):
        self.scenario_out_c_is_fixed_when_needed_for_c_file()
        self.scenario_out_c_is_fixed_when_needed_for_binary_file()

    def test_passes_correct_arch_bitsize_to_gcc(self):
        self.scenario_passes_m32_to_gcc_by_default()
        self.scenario_passes_m64_to_gcc_when_decompiling_64b_binary()


class TestAssertIsCompilable(BaseCompilationAssertionsTests):
    """Tests for `DecompilerTest.assert_out_c_is_compilable()`."""

    def test_raises_assertion_error_when_output_file_is_not_c_file(self):
        self.decompiler.out_hll_is_c.return_value = False
        self.test = self.create(TestSettings(input='file.exe'))
        with self.assertRaisesRegex(AssertionError, r'.*C file.*'):
            self.test.assert_out_c_is_compilable()

    def test_raises_assertion_error_when_file_fails_to_compile_due_to_error(self):
        def run_cmd_side_effect(*args, **kwargs):
            return 'error: xxx', 1, False
        self.decompiler._run_cmd.side_effect = run_cmd_side_effect
        with self.assertRaisesRegex(
                AssertionError,
                r'.*compil.*output:\serror: xxx.*'):
            self.test.assert_out_c_is_compilable()

    def test_raises_assertion_error_when_file_fails_to_compile_due_to_timeout(self):
        def run_cmd_side_effect(*args, **kwargs):
            return 'timeout', 1, True
        self.decompiler._run_cmd.side_effect = run_cmd_side_effect
        with self.assertRaisesRegex(AssertionError, r'.*timeouted.*'):
            self.test.assert_out_c_is_compilable()

    def run_method_so_it_succeeds(self):
        self.test.assert_out_c_is_compilable()

    def test_out_c_is_fixed_when_needed(self):
        self.scenario_out_c_is_fixed_when_needed_for_c_file()
        self.scenario_out_c_is_fixed_when_needed_for_binary_file()

    def test_passes_correct_arch_bitsize_to_gcc(self):
        self.scenario_passes_m32_to_gcc_by_default()
        self.scenario_passes_m64_to_gcc_when_decompiling_64b_binary()
