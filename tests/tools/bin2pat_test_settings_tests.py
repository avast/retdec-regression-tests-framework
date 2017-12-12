"""
    Tests for the :mod:`regression_tests.tools.bin2pat_test_settings` module.
"""

import unittest

from regression_tests.test_settings import TestSettings
from regression_tests.tools.bin2pat_arguments import Bin2PatArguments
from regression_tests.tools.bin2pat_runner import Bin2PatRunner
from regression_tests.tools.bin2pat_test import Bin2PatTest
from regression_tests.tools.bin2pat_test_settings import Bin2PatTestSettings


class Bin2PatTestSettingsTests(unittest.TestCase):
    """Tests for `Bin2PatTestSettings`."""

    def test_test_settings_creates_bin2pat_test_settings_when_tool_is_specified(self):
        settings = TestSettings(tool=Bin2PatTestSettings.TOOL, input='mod.o')
        self.assertIsInstance(settings, Bin2PatTestSettings)

    def test_tool_returns_correct_value(self):
        settings = Bin2PatTestSettings(input='mod.o')
        self.assertEqual(settings.tool, Bin2PatTestSettings.TOOL)

    def test_input_passed_to_constructor_is_accessible(self):
        INPUT = 'mod.o'
        settings = Bin2PatTestSettings(input=INPUT)
        self.assertEqual(INPUT, settings.input)

    def test_args_passed_to_constructor_are_accessible(self):
        ARGS = '--help'
        settings = Bin2PatTestSettings(input='mod.o', args=ARGS)
        self.assertEqual(ARGS, settings.args)

    def test_timeout_passed_to_constructor_is_accessible(self):
        TIMEOUT = 100
        settings = Bin2PatTestSettings(input='mod.o', timeout=TIMEOUT)
        self.assertEqual(settings.timeout, TIMEOUT)

    def test_tool_arguments_class_returns_correct_value(self):
        settings = Bin2PatTestSettings(input='mod.o')
        self.assertEqual(settings.tool_arguments_class, Bin2PatArguments)

    def test_tool_runner_class_returns_correct_value(self):
        settings = Bin2PatTestSettings(input='mod.o')
        self.assertEqual(settings.tool_runner_class, Bin2PatRunner)

    def test_tool_test_class_returns_correct_value(self):
        settings = Bin2PatTestSettings(input='mod.o')
        self.assertEqual(settings.tool_test_class, Bin2PatTest)
