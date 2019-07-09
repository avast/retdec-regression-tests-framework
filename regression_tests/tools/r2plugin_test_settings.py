"""
    Settings for r2 plugin.
"""

from regression_tests.tools.r2plugin_arguments import R2PluginArguments
from regression_tests.tools.r2plugin_runner import R2PluginRunner
from regression_tests.tools.r2plugin_test import R2PluginTest
from regression_tests.tools.tool_test_settings import ToolTestSettings
from regression_tests.utils import overrides
from regression_tests.utils.list import as_list


class R2PluginTestSettings(ToolTestSettings):
    """Settings for r2 plugin tests.

    See the description of :class:`.ToolTestSettings` for additional
    attributes.
    """

    #: Name of the tool.
    TOOL = 'r2plugin'

    def __init__(self, **kwargs):
        """
        See the description of :class:`.ToolTestSettings` for additional
        parameters.
        """
        kwargs['tool'] = self.TOOL
        ToolTestSettings.__init__(self, **kwargs)

    @property
    @overrides(ToolTestSettings)
    def tool_arguments_class(self):
        return R2PluginArguments

    @property
    @overrides(ToolTestSettings)
    def tool_runner_class(self):
        return R2PluginRunner

    @property
    @overrides(ToolTestSettings)
    def tool_test_class(self):
        return R2PluginTest

    @classmethod
    @overrides(ToolTestSettings)
    def should_be_created_from(cls, **kwargs):
        return kwargs.get('tool') == cls.TOOL
