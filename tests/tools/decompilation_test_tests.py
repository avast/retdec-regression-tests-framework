"""
    Tests for the :mod:`regression_tests.tools.decompilation_test` module.
"""

import abc
import re
import unittest
from unittest import mock

from regression_tests.parsers.fileinfo_output_parser import FileinfoOutput
from regression_tests.test_settings import TestSettings
from regression_tests.tools.decompilation import Decompilation
from regression_tests.tools.decompilation_test import DecompilationTest
from regression_tests.utils.os import on_windows
from tests.matchers import AnyStrWith
from tests.matchers import Anything


class BaseDecompilationTestTests(unittest.TestCase):
    """A base class for all tests of `DecompilationTest`."""

    def setUp(self):
        self.decomp = mock.Mock(spec_set=Decompilation)

    # The method cannot be named 'create_test' because unittest then treats it
    # as a test method.
    def create(self, test_settings):
        """Creates an instance of `DecompilationTest` with the given settings.
        """
        return DecompilationTest(self.decomp, test_settings)

    def is_gcc(self, args):
        """Checks if GCC is run in the given arguments."""
        # On Windows, GCC is run via `sh.exe windows-gcc-32` instead of `gcc`.
        if on_windows():
            return len(args[0]) > 1 and args[0][1] == 'windows-gcc-32.sh'
        return args[0][0] == 'gcc'


class DecompilationTestTests(BaseDecompilationTestTests):
    """Tests for `DecompilationTest`."""

    def test_decomp_returns_given_decompilation(self):
        test = self.create(TestSettings(input='file.exe'))
        self.assertEqual(test.decomp, self.decomp)

    def test_decomp_cannot_be_changed(self):
        test = self.create(TestSettings(input='file.exe'))
        with self.assertRaises(AttributeError):
            test.decomp = mock.Mock(spec_set=Decompilation)

    def test_out_c_returns_same_result_as_decomp_out_c(self):
        test = self.create(TestSettings(input='file.exe'))
        self.assertEqual(test.out_c, test.decomp.out_c)

    def test_out_dsm_returns_same_result_as_decomp_out_dsm(self):
        test = self.create(TestSettings(input='file.exe'))
        self.assertEqual(test.out_dsm, test.decomp.out_dsm)

    def test_out_config_returns_same_result_as_decomp_out_config(self):
        test = self.create(TestSettings(input='file.json'))
        self.assertEqual(test.out_config, test.decomp.out_config)

    def test_settings_returns_given_test_settings(self):
        TEST_SETTINGS = TestSettings(input='file.exe')
        test = self.create(TEST_SETTINGS)
        self.assertEqual(test.settings, TEST_SETTINGS)

    def test_settings_cannot_be_changed(self):
        test = self.create(TestSettings(input='file.exe'))
        with self.assertRaises(AttributeError):
            test.settings = TestSettings(input='file.exe')


class WithDecompilationTestTests(BaseDecompilationTestTests):
    """A base class for all tests with a `DecompilationTest` instance."""

    def setUp(self):
        super().setUp()
        self.test = self.create(TestSettings(input='file.exe'))


class DecompilationTestSetUpTests(WithDecompilationTestTests):
    """Tests for `DecompilationTest.setUp()`."""

    def test_raises_assertion_error_with_output_when_decompilation_timeouted(self):
        self.decomp.name = 'decompile.sh'
        self.decomp.end_of_output.return_value = 'END OF OUTPUT'
        type(self.decomp).timeouted = mock.PropertyMock(return_value=1)
        with self.assertRaisesRegex(
                AssertionError,
                re.compile(r'.*decompile.sh.*timeouted.*END OF OUTPUT.*', re.DOTALL)):
            self.test.setUp()

    def test_raises_assertion_error_with_output_when_decompilation_failed(self):
        self.decomp.name = 'decompile.sh'
        self.decomp.end_of_output.return_value = 'END OF OUTPUT'
        type(self.decomp).timeouted = mock.PropertyMock(return_value=0)
        type(self.decomp).return_code = mock.PropertyMock(return_value=1)
        with self.assertRaisesRegex(
                AssertionError,
                re.compile(r'.*decompile.sh.*failed.*END OF OUTPUT.*', re.DOTALL)):
            self.test.setUp()


class BaseCompilationAssertionsTests(WithDecompilationTestTests):
    """A base class for all assertions concerning compilation."""

    def setUp(self):
        super().setUp()
        self.decomp.dir.get_file().exists.return_value = False
        type(self.decomp.input_file).name = mock.PropertyMock(return_value='file.exe')
        type(self.decomp.out_c_file).name = mock.PropertyMock(return_value='file.out.c')
        self.decomp.out_c_file.renamed().exists.return_value = False
        self.decomp.fileinfo_outputs = []

        def run_cmd_side_effect(*args, **kwargs):
            return '', 0, False
        self.decomp._run_cmd.side_effect = run_cmd_side_effect

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
        self.decomp.fileinfo_outputs = [
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

    def _check_out_c_gets_fixed(self):
        type(self.decomp).out_c = mock.PropertyMock(return_value='')
        self.decomp.dir.store_file.reset_mock()

        self.run_method_so_it_succeeds()

        self.decomp.dir.store_file.assert_called_once_with(
            Anything(),
            AnyStrWith('.*COMPILATION.*')
        )


class TestAssertCProducesOutputWhenRunTests(BaseCompilationAssertionsTests):
    """Tests for `DecompilationTest.assert_c_produces_output_when_run()`."""

    def test_raises_assertion_error_when_output_file_is_not_c_file(self):
        self.decomp.out_hll_is_c.return_value = False
        self.test = self.create(TestSettings(input='file.exe'))
        with self.assertRaisesRegex(AssertionError, r'.*C file.*'):
            self.test.assert_c_produces_output_when_run('input', 'expected output')

    def test_raises_assertion_error_when_file_fails_to_compile(self):
        def run_cmd_side_effect(*args, **kwargs):
            if self.is_gcc(args):
                return 'error: xxx', 1, False
            return '', 0, False
        self.decomp._run_cmd.side_effect = run_cmd_side_effect
        with self.assertRaisesRegex(
                AssertionError,
                r'.*compil.*output:\serror: xxx.*'):
            self.test.assert_c_produces_output_when_run('input', 'expected output')

    def test_raises_assertion_error_when_compiled_file_run_timeouts(self):
        def run_cmd_side_effect(*args, **kwargs):
            if self.is_gcc(args):
                return '', 0, False
            return 'timeout', 1, True
        self.decomp._run_cmd.side_effect = run_cmd_side_effect
        with self.assertRaisesRegex(AssertionError, r'.*timeouted.*'):
            self.test.assert_c_produces_output_when_run('input', 'expected output')

    def test_raises_assertion_error_when_outputs_differ(self):
        def run_cmd_side_effect(*args, **kwargs):
            return 'other than expected output', 0, False
        self.decomp._run_cmd.side_effect = run_cmd_side_effect
        with self.assertRaisesRegex(
                AssertionError,
                r'.*other than expected output.*!=.*expected output.*'):
            self.test.assert_c_produces_output_when_run('input', 'expected output')

    def test_raises_assertion_error_when_return_codes_differ(self):
        def run_cmd_side_effect(*args, **kwargs):
            if self.is_gcc(args):
                return '', 0, False
            return 'expected output', 5, False
        self.decomp._run_cmd.side_effect = run_cmd_side_effect
        with self.assertRaisesRegex(AssertionError, r'.*5.*!=.*0.*'):
            self.test.assert_c_produces_output_when_run(
                'input',
                'expected output',
                expected_return_code=0
            )

    def run_method_so_it_succeeds(self):
        def run_cmd_side_effect(*args, **kwargs):
            return 'expected output', 0, False
        self.decomp._run_cmd.side_effect = run_cmd_side_effect
        self.test.assert_c_produces_output_when_run('input', 'expected output')

    def test_out_c_is_fixed_when_needed(self):
        self.scenario_out_c_is_fixed_when_needed_for_c_file()
        self.scenario_out_c_is_fixed_when_needed_for_binary_file()


class TestAssertIsCompilable(BaseCompilationAssertionsTests):
    """Tests for `DecompilationTest.assert_out_c_is_compilable()`."""

    def test_raises_assertion_error_when_output_file_is_not_c_file(self):
        self.decomp.out_hll_is_c.return_value = False
        self.test = self.create(TestSettings(input='file.exe'))
        with self.assertRaisesRegex(AssertionError, r'.*C file.*'):
            self.test.assert_out_c_is_compilable()

    def test_raises_assertion_error_when_file_fails_to_compile_due_to_error(self):
        def run_cmd_side_effect(*args, **kwargs):
            return 'error: xxx', 1, False
        self.decomp._run_cmd.side_effect = run_cmd_side_effect
        with self.assertRaisesRegex(
                AssertionError,
                r'.*compil.*output:\serror: xxx.*'):
            self.test.assert_out_c_is_compilable()

    def test_raises_assertion_error_when_file_fails_to_compile_due_to_timeout(self):
        def run_cmd_side_effect(*args, **kwargs):
            return 'timeout', 1, True
        self.decomp._run_cmd.side_effect = run_cmd_side_effect
        with self.assertRaisesRegex(AssertionError, r'.*timeouted.*'):
            self.test.assert_out_c_is_compilable()

    def run_method_so_it_succeeds(self):
        self.test.assert_out_c_is_compilable()

    def test_out_c_is_fixed_when_needed(self):
        self.scenario_out_c_is_fixed_when_needed_for_c_file()
        self.scenario_out_c_is_fixed_when_needed_for_binary_file()
