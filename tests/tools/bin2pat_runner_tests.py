"""
    Tests for the :mod:`regression_tests.tools.bin2pat_runner` module.
"""

import unittest
from unittest import mock

from regression_tests.cmd_runner import CmdRunner
from regression_tests.tools.bin2pat import Bin2Pat
from regression_tests.tools.bin2pat_runner import Bin2PatRunner
from regression_tests.tools.tool_test_settings import ToolTestSettings


class Bin2PatRunnerTests(unittest.TestCase):
    """Tests for `Bin2PatRunner()`."""

    def setUp(self):
        self.cmd_runner = mock.Mock(spec_set=CmdRunner)
        self.tools_dir = mock.Mock()
        self.test_settings = mock.Mock(spec_set=ToolTestSettings)
        self.decomp_runner = Bin2PatRunner(
            self.cmd_runner,
            self.tools_dir,
            self.test_settings
        )

    def test_tool_class_returns_bin2pat(self):
        self.assertIs(self.decomp_runner._tool_class, Bin2Pat)

    def test_get_tool_executable_name_returns_correct_name(self):
        self.assertEqual(
            self.decomp_runner._get_tool_executable_name('bin2pat'),
            'bin2pat'
        )
