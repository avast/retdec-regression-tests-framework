"""
    Tests for the :mod:`regression_tests.tools.unpacker_test_settings` module.
"""

import unittest

from regression_tests.test_settings import InvalidTestSettingsError
from regression_tests.test_settings import TestSettings
from regression_tests.tools.unpacker_arguments import UnpackerArguments
from regression_tests.tools.unpacker_runner import UnpackerRunner
from regression_tests.tools.unpacker_test import UnpackerTest
from regression_tests.tools.unpacker_test_settings import UnpackerTestSettings


class UnpackerTestSettingsTests(unittest.TestCase):
    """Tests for `UnpackerTestSettings`."""

    def test_test_settings_creates_unpacker_test_settings_when_tool_is_specified(self):
        settings = TestSettings(tool=UnpackerTestSettings.TOOL, input='file.exe')
        self.assertIsInstance(settings, UnpackerTestSettings)

    def test_tool_returns_correct_value(self):
        settings = UnpackerTestSettings(input='file.exe')
        self.assertEqual(settings.tool, UnpackerTestSettings.TOOL)

    def test_input_passed_to_constructor_is_accessible(self):
        INPUT = 'file.exe'
        settings = UnpackerTestSettings(input=INPUT)
        self.assertEqual(INPUT, settings.input)

    def test_args_passed_to_constructor_are_accessible(self):
        ARGS = '--help'
        settings = UnpackerTestSettings(input='file.exe', args=ARGS)
        self.assertEqual(ARGS, settings.args)

    def test_timeout_passed_to_constructor_is_accessible(self):
        TIMEOUT = 100
        settings = UnpackerTestSettings(input='file.exe', timeout=TIMEOUT)
        self.assertEqual(settings.timeout, TIMEOUT)

    def test_tool_arguments_class_returns_correct_value(self):
        settings = UnpackerTestSettings(input='file.exe')
        self.assertEqual(settings.tool_arguments_class, UnpackerArguments)

    def test_tool_runner_class_returns_correct_value(self):
        settings = UnpackerTestSettings(input='file.exe')
        self.assertEqual(settings.tool_runner_class, UnpackerRunner)

    def test_tool_test_class_returns_correct_value(self):
        settings = UnpackerTestSettings(input='file.exe')
        self.assertEqual(settings.tool_test_class, UnpackerTest)

    def test_run_fileinfo_returns_false_when_it_is_not_set_in_constructor(self):
        settings = UnpackerTestSettings(input='file.exe')
        self.assertFalse(settings.run_fileinfo)

    def test_run_fileinfo_returns_true_when_it_is_set_to_true_in_constructor(self):
        settings = UnpackerTestSettings(input='file.exe', run_fileinfo=True)
        self.assertTrue(settings.run_fileinfo)

    def test_run_fileinfo_has_to_be_bool(self):
        with self.assertRaisesRegex(InvalidTestSettingsError,
                                    r'.*run_fileinfo.*bool.*not.*list'):
            UnpackerTestSettings(input='file.exe', run_fileinfo=[1])

    def test_fileinfo_args_returns_correct_value_when_set_in_constructor(self):
        ARGS = '--json'
        settings = UnpackerTestSettings(input='file.exe', fileinfo_args=ARGS)
        self.assertEqual(settings.fileinfo_args, ARGS)

    def test_fileinfo_args_has_to_be_string(self):
        with self.assertRaisesRegex(InvalidTestSettingsError,
                                    r'.*fileinfo_args.*str.*not.*list'):
            UnpackerTestSettings(input='file.exe', fileinfo_args=[1])

    def test_fileinfo_timeout_returns_correct_value_when_set_in_constructor(self):
        TIMEOUT = 120
        settings = UnpackerTestSettings(input='file.exe', fileinfo_timeout=TIMEOUT)
        self.assertEqual(settings.fileinfo_timeout, TIMEOUT)

    def test_fileinfo_timeout_has_to_be_int(self):
        with self.assertRaisesRegex(InvalidTestSettingsError,
                                    r'.*fileinfo_timeout.*int.*not.*list'):
            UnpackerTestSettings(input='file.exe', fileinfo_timeout=[1])
