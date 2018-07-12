"""
    A runner of the IDA plugin.
"""

from regression_tests.tools.idaplugin import IDAPlugin
from regression_tests.tools.tool_runner import ToolRunner
from regression_tests.utils import overrides


class IDAPluginRunner(ToolRunner):
    """A runner of the IDA plugin."""

    @property
    @overrides(ToolRunner)
    def _tool_class(self):
        return IDAPlugin

    @overrides(ToolRunner)
    def _get_tool_executable_name(self, tool_name):
        return 'run_ida_decompilation.py'
