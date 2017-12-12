"""
    Tests for the :mod:`regression_tests.tools.unpacker_runner` module.
"""

import os
import unittest
from unittest import mock

from regression_tests.cmd_runner import CmdRunner
from regression_tests.tools.fileinfo_arguments import FileinfoArguments
from regression_tests.tools.unpacker import Unpacker
from regression_tests.tools.unpacker_arguments import UnpackerArguments
from regression_tests.tools.unpacker_runner import UnpackerRunner


class UnpackerRunnerTests(unittest.TestCase):
    """Tests for `UnpackerRunner()`."""

    def setUp(self):
        self.cmd_runner = mock.Mock(spec_set=CmdRunner)
        self.tools_dir = mock.MagicMock()
        self.test_settings = mock.Mock()
        self.unpacker_args = mock.Mock()
        self.unpacker_dir = mock.Mock()
        self.unpacker_runner = UnpackerRunner(
            self.cmd_runner,
            self.tools_dir,
            self.test_settings
        )

    def run_get_tool(self, **kwargs):
        """Runs `_get_tool()` with the given arguments.

        When a required argument is not given, a default value is used.
        """
        return self.unpacker_runner._get_tool(
            tool_name=kwargs.get('tool_name', 'unpacker'),
            args=kwargs.get('args', self.unpacker_args),
            dir=kwargs.get('dir', self.unpacker_dir),
            output=kwargs.get('output', ''),
            return_code=kwargs.get('return_code', 0),
            timeout=kwargs.get('timeout', 10),
            timeouted=kwargs.get('timeouted', False)
        )

    def test_tool_class_returns_unpacker(self):
        self.assertIs(self.unpacker_runner._tool_class, Unpacker)

    def test_get_tool_does_not_run_fileinfo_when_fileinfo_run_was_not_requested(self):
        self.test_settings.run_fileinfo = False

        unpacker = self.run_get_tool()

        with self.assertRaisesRegex(AssertionError, r'.*fileinfo.*'):
            unpacker.fileinfo

    def test_get_tool_runs_fileinfo_when_fileinfo_run_was_requested(self):
        self.test_settings.run_fileinfo = True
        self.test_settings.fileinfo_args = '--json --verbose'
        self.test_settings.fileinfo_timeout = 60
        self.tools_dir.path = 'bin'
        self.cmd_runner.run_cmd.return_value = ('fileinfo output', 0, False)

        unpacker = self.run_get_tool()

        self.cmd_runner.run_cmd.assert_called_once_with(
            [
                os.path.join('bin', 'fileinfo'),
                self.unpacker_args.output_file.path,
                '--json',
                '--verbose'
            ],
            strip_shell_colors=True,
            timeout=60
        )
        self.assertEqual(unpacker.fileinfo.return_code, 0)
        self.assertEqual(unpacker.fileinfo.output, 'fileinfo output')
        self.assertFalse(unpacker.fileinfo.timeouted)

    def test_create_log_returns_just_unpacker_log_when_fileinfo_did_not_run(self):
        self.test_settings.run_fileinfo = False
        unpacker = mock.Mock()
        unpacker.name = 'unpacker'
        unpacker.output = 'unpacker output\n'
        unpacker.timeouted = False
        unpacker.return_code = 0
        unpacker.args = UnpackerArguments(args='--unpacker-arg')

        log = self.unpacker_runner._create_log(unpacker, timeout=100)

        expected_log = '\n'.join([
            '# Command: unpacker --unpacker-arg',
            '# Timeout: 100 seconds',
            '',
            'unpacker output',
            '',
            '# Return code: 0',
            '# Timeouted:   no',
            ''
        ])

        self.assertEqual(log, expected_log)

    def test_create_log_returns_combined_log_when_fileinfo_run(self):
        self.test_settings.run_fileinfo = True
        self.test_settings.fileinfo_timeout = 60
        unpacker = mock.Mock()
        unpacker.name = 'unpacker'
        unpacker.output = 'unpacker output\n'
        unpacker.timeouted = False
        unpacker.return_code = 0
        unpacker.args = UnpackerArguments(args='--unpacker-arg')
        unpacker.fileinfo = mock.Mock()
        unpacker.fileinfo.name = 'fileinfo'
        unpacker.fileinfo.output = 'fileinfo output\n'
        unpacker.fileinfo.timeouted = True
        unpacker.fileinfo.return_code = 1
        unpacker.fileinfo.args = FileinfoArguments(args='--fileinfo-arg')

        log = self.unpacker_runner._create_log(unpacker, timeout=100)

        expected_log = '\n'.join([
            '# Command: unpacker --unpacker-arg',
            '# Timeout: 100 seconds',
            '',
            'unpacker output',
            '',
            '# Return code: 0',
            '# Timeouted:   no',
            '',
            '# ------------------------------------------------------------------------------',
            '',
            '# Command: fileinfo --fileinfo-arg',
            '# Timeout: 60 seconds',
            '',
            'fileinfo output',
            '',
            '# Return code: 1',
            '# Timeouted:   yes',
            ''
        ])

        self.assertEqual(log, expected_log)
