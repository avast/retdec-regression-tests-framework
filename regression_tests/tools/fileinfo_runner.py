"""
    A runner of fileinfo.
"""

from regression_tests.tools.fileinfo import Fileinfo
from regression_tests.tools.tool_runner import ToolRunner
from regression_tests.utils import overrides


class FileinfoRunner(ToolRunner):
    """A runner of fileinfo."""

    @property
    @overrides(ToolRunner)
    def _tool_class(self):
        return Fileinfo

    @overrides(ToolRunner)
    def _get_tool_executable_name(self, tool_name):
        return 'retdec-fileinfo.py'
