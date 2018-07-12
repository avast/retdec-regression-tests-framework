"""
    Tests for the :mod:`regression_tests.tools.idaplugin_runner` module.
"""

import unittest
from unittest import mock

from regression_tests.cmd_runner import CmdRunner
from regression_tests.tools.idaplugin import IDAPlugin
from regression_tests.tools.idaplugin_runner import IDAPluginRunner
from regression_tests.tools.tool_test_settings import ToolTestSettings


class IDAPluginRunnerTests(unittest.TestCase):
    """Tests for `IDAPluginRunner()`."""

    def setUp(self):
        self.cmd_runner = mock.Mock(spec_set=CmdRunner)
        self.tools_dir = mock.Mock()
        self.test_settings = mock.Mock(spec_set=ToolTestSettings)
        self.decomp_runner = IDAPluginRunner(
            self.cmd_runner,
            self.tools_dir,
            self.test_settings
        )

    def test_tool_class_returns_idaplugin(self):
        self.assertIs(self.decomp_runner._tool_class, IDAPlugin)

    def test_get_tool_executable_name_returns_correct_name(self):
        self.assertEqual(
            self.decomp_runner._get_tool_executable_name('idaplugin'),
            'run_ida_decompilation.py'
        )
