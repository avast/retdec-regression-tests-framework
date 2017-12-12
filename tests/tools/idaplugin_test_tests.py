"""
    Tests for the :mod:`regression_tests.tools.idaplugin_test` module.
"""

import re
import unittest
from unittest import mock

from regression_tests.tools.idaplugin import IDAPlugin
from regression_tests.tools.idaplugin_test import IDAPluginTest
from regression_tests.tools.idaplugin_test_settings import IDAPluginTestSettings


class IDAPluginTestTests(unittest.TestCase):
    """Tests for `IDAPluginTest`."""

    def setUp(self):
        self.idaplugin = mock.Mock(spec_set=IDAPlugin)
        self.idaplugin.name = 'idaplugin'
        # The following variable has to be set so that ToolTest.__getattr__()
        # works correctly.
        self.idaplugin.safe_name = self.idaplugin.name

    def test_out_c_returns_same_result_as_idaplugin_out_c(self):
        test = IDAPluginTest(self.idaplugin, IDAPluginTestSettings(input='file.exe'))
        self.assertEqual(test.out_c, test.idaplugin.out_c)

    def test_setup_raises_assertion_error_with_output_when_idaplugin_timeouted(self):
        test = IDAPluginTest(self.idaplugin, IDAPluginTestSettings(input='file.exe'))
        self.idaplugin.end_of_output.return_value = 'END OF OUTPUT'
        self.idaplugin.timeouted = 1
        with self.assertRaisesRegex(
                AssertionError,
                re.compile(r'.*idaplugin.*timeouted.*END OF OUTPUT.*', re.DOTALL)):
            test.setUp()

    def test_setup_raises_assertion_error_with_output_when_idaplugin_failed(self):
        test = IDAPluginTest(self.idaplugin, IDAPluginTestSettings(input='file.exe'))
        self.idaplugin.end_of_output.return_value = 'END OF OUTPUT'
        self.idaplugin.timeouted = 0
        self.idaplugin.succeeded = False
        with self.assertRaisesRegex(
                AssertionError,
                re.compile(r'.*idaplugin.*failed.*END OF OUTPUT.*', re.DOTALL)):
            test.setUp()
