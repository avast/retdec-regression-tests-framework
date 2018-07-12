"""
    Tests for the :mod:`regression_tests.tools.fileinfo_runner` module.
"""

import unittest
from unittest import mock

from regression_tests.cmd_runner import CmdRunner
from regression_tests.tools.fileinfo import Fileinfo
from regression_tests.tools.fileinfo_runner import FileinfoRunner
from regression_tests.tools.tool_test_settings import ToolTestSettings


class FileinfoRunnerTests(unittest.TestCase):
    """Tests for `FileinfoRunner()`."""

    def setUp(self):
        self.cmd_runner = mock.Mock(spec_set=CmdRunner)
        self.tools_dir = mock.Mock()
        self.test_settings = mock.Mock(spec_set=ToolTestSettings)
        self.decomp_runner = FileinfoRunner(
            self.cmd_runner,
            self.tools_dir,
            self.test_settings
        )

    def test_tool_class_returns_fileinfo(self):
        self.assertIs(self.decomp_runner._tool_class, Fileinfo)

    def test_get_tool_executable_name_returns_correct_name(self):
        self.assertEqual(
            self.decomp_runner._get_tool_executable_name('fileinfo'),
            'retdec_fileinfo.py'
        )
