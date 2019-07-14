"""
    Tests for the :mod:`regression_tests.tools.r2plugin_test` module.
"""

import re
import unittest
from unittest import mock

from regression_tests.tools.r2plugin import R2Plugin
from regression_tests.tools.r2plugin_test import R2PluginTest
from regression_tests.tools.r2plugin_test_settings import R2PluginTestSettings


class R2PluginTestTests(unittest.TestCase):
    """Tests for `R2PluginTest`."""

    def setUp(self):
        self.r2plugin = mock.Mock(spec_set=R2Plugin)
        self.r2plugin.name = 'r2plugin'
        # The following variable has to be set so that ToolTest.__getattr__()
        # works correctly.
        self.r2plugin.safe_name = self.r2plugin.name

    def test_out_c_returns_same_result_as_r2plugin_out_c(self):
        test = R2PluginTest(self.r2plugin, R2PluginTestSettings(input='file.exe'))
        self.assertEqual(test.out_c, test.r2plugin.out_c)

    def test_setup_raises_assertion_error_with_output_when_r2plugin_timeouted(self):
        test = R2PluginTest(self.r2plugin, R2PluginTestSettings(input='file.exe'))
        self.r2plugin.end_of_output.return_value = 'END OF OUTPUT'
        self.r2plugin.timeouted = 1
        with self.assertRaisesRegex(
                AssertionError,
                re.compile(r'.*r2plugin.*timeouted.*END OF OUTPUT.*', re.DOTALL)):
            test.setUp()

    def test_setup_raises_assertion_error_with_output_when_r2plugin_failed(self):
        test = R2PluginTest(self.r2plugin, R2PluginTestSettings(input='file.exe'))
        self.r2plugin.end_of_output.return_value = 'END OF OUTPUT'
        self.r2plugin.timeouted = 0
        self.r2plugin.succeeded = False
        with self.assertRaisesRegex(
                AssertionError,
                re.compile(r'.*r2plugin.*failed.*END OF OUTPUT.*', re.DOTALL)):
            test.setUp()
