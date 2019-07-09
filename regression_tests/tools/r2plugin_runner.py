"""
    A runner of the r2 plugin.
"""

from regression_tests.tools.r2plugin import R2Plugin
from regression_tests.tools.tool_runner import ToolRunner
from regression_tests.utils import overrides


class R2PluginRunner(ToolRunner):
    """A runner of the r2 plugin."""

    @property
    @overrides(ToolRunner)
    def _tool_class(self):
        return R2Plugin

    @overrides(ToolRunner)
    def _get_tool_executable_name(self, tool_name):
        return 'run-r2-decompilation.py'
