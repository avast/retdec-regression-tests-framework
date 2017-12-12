"""
    Settings for fileinfo.
"""

from regression_tests.tools.fileinfo_arguments import FileinfoArguments
from regression_tests.tools.fileinfo_runner import FileinfoRunner
from regression_tests.tools.fileinfo_test import FileinfoTest
from regression_tests.tools.tool_test_settings import ToolTestSettings
from regression_tests.utils import overrides


class FileinfoTestSettings(ToolTestSettings):
    """Settings for fileinfo tests.

    See the description of :class:`.ToolTestSettings` for additional
    attributes.
    """

    #: Name of the tool.
    TOOL = 'fileinfo'

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
        return FileinfoArguments

    @property
    @overrides(ToolTestSettings)
    def tool_runner_class(self):
        return FileinfoRunner

    @property
    @overrides(ToolTestSettings)
    def tool_test_class(self):
        return FileinfoTest

    @classmethod
    @overrides(ToolTestSettings)
    def should_be_created_from(cls, **kwargs):
        return kwargs.get('tool') == cls.TOOL
