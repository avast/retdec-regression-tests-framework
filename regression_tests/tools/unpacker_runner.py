"""
    A runner of unpacker.
"""

from regression_tests.tools.fileinfo import Fileinfo
from regression_tests.tools.fileinfo_arguments import FileinfoArguments
from regression_tests.tools.tool_runner import ToolRunner
from regression_tests.tools.unpacker import Unpacker
from regression_tests.utils import overrides


class UnpackerRunner(ToolRunner):
    """A runner of unpacker."""

    @property
    @overrides(ToolRunner)
    def _tool_class(self):
        return Unpacker

    @overrides(ToolRunner)
    def _get_tool_executable_name(self, tool_name):
        # retdec-unpacker for "unpacker", retdec-fileinfo for "fileinfo". The
        # reason for the support of two tools is that we have to potentially
        # run fileinfo (if it was requested).
        return 'retdec-{}'.format(tool_name)

    @overrides(ToolRunner)
    def _get_tool(self, tool_name, args, dir, output, return_code, timeout,
                  timeouted):
        # The only difference between this method and ToolRunner._get_tool() is
        # that we have to potentially run fileinfo (if it was requested).
        fileinfo = self._run_fileinfo_if_requested(dir, args)
        return self._tool_class(
            tool_name,
            dir,
            args,
            self._cmd_runner,
            output,
            return_code,
            timeouted,
            fileinfo=fileinfo
        )

    def _run_fileinfo_if_requested(self, dir, unpacker_args):
        """Runs fileinfo over the output from the unpacker, but only when such
        a run was requested by the user.
        """
        if not self._test_settings.run_fileinfo:
            return None

        fileinfo_args = FileinfoArguments(
            input_files=(unpacker_args.output_file,),
            args=self._test_settings.fileinfo_args
        )
        output, return_code, timeouted = self._run_tool(
            'fileinfo',
            fileinfo_args,
            self._test_settings.fileinfo_timeout
        )
        return Fileinfo(
            'fileinfo',
            dir,
            fileinfo_args,
            self._cmd_runner,
            output,
            return_code,
            timeouted
        )

    @overrides(ToolRunner)
    def _create_log(self, tool, timeout):
        unpacker_log = super()._create_log(tool, timeout)
        if not self._test_settings.run_fileinfo:
            return unpacker_log

        # Create a combined unpacker + fileinfo log.
        fileinfo_log = super()._create_log(
            tool.fileinfo,
            self._test_settings.fileinfo_timeout
        )
        return self._combine_logs(unpacker_log, fileinfo_log)
