"""
    Tests for the :mod:`regression_tests.tools.fileinfo_test_settings` module.
"""

import unittest

from regression_tests.test_settings import TestSettings
from regression_tests.tools.fileinfo_arguments import FileinfoArguments
from regression_tests.tools.fileinfo_runner import FileinfoRunner
from regression_tests.tools.fileinfo_test import FileinfoTest
from regression_tests.tools.fileinfo_test_settings import FileinfoTestSettings


class FileinfoTestSettingsTests(unittest.TestCase):
    """Tests for `FileinfoTestSettings`."""

    def test_test_settings_creates_fileinfo_test_settings_when_tool_is_specified(self):
        settings = TestSettings(tool=FileinfoTestSettings.TOOL, input='file.exe')
        self.assertIsInstance(settings, FileinfoTestSettings)

    def test_tool_returns_correct_value(self):
        settings = FileinfoTestSettings(input='file.exe')
        self.assertEqual(settings.tool, FileinfoTestSettings.TOOL)

    def test_input_passed_to_constructor_is_accessible(self):
        INPUT = 'file.exe'
        settings = FileinfoTestSettings(input=INPUT)
        self.assertEqual(INPUT, settings.input)

    def test_args_passed_to_constructor_are_accessible(self):
        ARGS = '--all'
        settings = FileinfoTestSettings(input='file.exe', args=ARGS)
        self.assertEqual(ARGS, settings.args)

    def test_timeout_passed_to_constructor_is_accessible(self):
        TIMEOUT = 100
        settings = FileinfoTestSettings(input='file.exe', timeout=TIMEOUT)
        self.assertEqual(settings.timeout, TIMEOUT)

    def test_tool_arguments_class_returns_correct_value(self):
        settings = FileinfoTestSettings(input='file.exe')
        self.assertEqual(settings.tool_arguments_class, FileinfoArguments)

    def test_tool_runner_class_returns_correct_value(self):
        settings = FileinfoTestSettings(input='file.exe')
        self.assertEqual(settings.tool_runner_class, FileinfoRunner)

    def test_tool_test_class_returns_correct_value(self):
        settings = FileinfoTestSettings(input='file.exe')
        self.assertEqual(settings.tool_test_class, FileinfoTest)
