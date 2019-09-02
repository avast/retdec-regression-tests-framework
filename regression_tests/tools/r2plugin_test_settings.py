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

    def __init__(self, project=None, commands=None, **kwargs):
        """
        :param str project: R2 project file.

        See the description of :class:`.ToolTestSettings` for additional
        parameters.
        """
        kwargs['tool'] = self.TOOL
        ToolTestSettings.__init__(self, **kwargs)

        # r2 project
        self.project = self._merge_duplicates(project)
        self.commands = commands

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

    @property
    def project_as_list(self):
        """R2 project file(s) as a list.

        When the R2 project file is not set, the empty list is returned.
        When there is only a single R2 project file, a singleton list is
        returned. When there are multiple files, the list is returned directly.
        """
        return as_list(self.project)

    @property
    def commands_as_list(self):
        """R2 project file(s) as a list.

        When the R2 commands are not set, the empty list is returned.
        When there is only a single R2 command, a singleton list is
        returned. When there are multiple commands, the list is returned
        directly.
        """
        return as_list(self.commands)

    def has_multiple_projects(self):
        """Checks if the settings contains multiple R2 project files.

        :returns: ``True`` if the settings contains multiple R2 project
                  files, ``False`` otherwise.
        """
        return self._has_multiple_values_for_attr('project')
