"""
    Tests for the :mod:`regression_tests.tools.tool_test` module.
"""

import unittest
from unittest import mock

from regression_tests.test_settings import TestSettings
from regression_tests.tools.tool import Tool
from regression_tests.tools.tool_test import ToolTest


class ToolTestTests(unittest.TestCase):
    """Tests for `ToolTest`."""

    def setUp(self):
        self.tool = mock.Mock(spec_set=Tool)
        self.test_settings = mock.Mock(spec_set=TestSettings)
        self.test = ToolTest(self.tool, self.test_settings)

    def test_tool_returns_given_tool(self):
        self.assertEqual(self.test.tool, self.tool)

    def test_tool_cannot_be_changed(self):
        with self.assertRaises(AttributeError):
            self.test.tool = mock.Mock(spec_set=Tool)

    def test_tool_can_be_accessed_through_its_safe_name(self):
        self.tool.safe_name = 'fileinfo'
        self.assertEqual(self.test.fileinfo, self.tool)

    def test_raises_exception_when_tools_safe_name_does_not_correspond_to_used_name(self):
        self.tool.safe_name = 'fileinfo'
        with self.assertRaisesRegex(AttributeError, r'.*ToolTest.*my_tool.*'):
            self.assertEqual(self.test.my_tool, self.tool)
