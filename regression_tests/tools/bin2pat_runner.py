"""
    A runner of bin2pat.
"""

from regression_tests.tools.bin2pat import Bin2Pat
from regression_tests.tools.tool_runner import ToolRunner
from regression_tests.utils import overrides


class Bin2PatRunner(ToolRunner):
    """A runner of bin2pat."""

    @property
    @overrides(ToolRunner)
    def _tool_class(self):
        return Bin2Pat

    @overrides(ToolRunner)
    def _get_tool_executable_name(self, tool_name):
        return 'retdec-bin2pat'
