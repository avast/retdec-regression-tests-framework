"""
    Tests for the :mod:`regression_tests.tools.r2plugin_runner` module.
"""

import unittest
from unittest import mock

from regression_tests.cmd_runner import CmdRunner
from regression_tests.tools.r2plugin import R2Plugin
from regression_tests.tools.r2plugin_runner import R2PluginRunner
from regression_tests.tools.tool_test_settings import ToolTestSettings


class R2PluginRunnerTests(unittest.TestCase):
    """Tests for `R2PluginRunner()`."""

    def setUp(self):
        self.cmd_runner = mock.Mock(spec_set=CmdRunner)
        self.tools_dir = mock.Mock()
        self.test_settings = mock.Mock(spec_set=ToolTestSettings)
        self.decomp_runner = R2PluginRunner(
            self.cmd_runner,
            self.tools_dir,
            self.test_settings
        )

    def test_tool_class_returns_r2plugin(self):
        self.assertIs(self.decomp_runner._tool_class, R2Plugin)

    def test_get_tool_executable_name_returns_correct_name(self):
        self.assertEqual(
            self.decomp_runner._get_tool_executable_name('r2plugin'),
            'run-r2-decompilation.py'
        )
