"""
    Settings for bin2pat tests.
"""

from regression_tests.tools.bin2pat_arguments import Bin2PatArguments
from regression_tests.tools.bin2pat_runner import Bin2PatRunner
from regression_tests.tools.bin2pat_test import Bin2PatTest
from regression_tests.tools.tool_test_settings import ToolTestSettings
from regression_tests.utils import overrides


class Bin2PatTestSettings(ToolTestSettings):
    """Settings for bin2pat tests.

    See the description of :class:`.ToolTestSettings` for additional
    attributes.
    """

    #: Name of the tool.
    TOOL = 'bin2pat'

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
        return Bin2PatArguments

    @property
    @overrides(ToolTestSettings)
    def tool_runner_class(self):
        return Bin2PatRunner

    @property
    @overrides(ToolTestSettings)
    def tool_test_class(self):
        return Bin2PatTest

    @classmethod
    @overrides(ToolTestSettings)
    def should_be_created_from(cls, **kwargs):
        return kwargs.get('tool') == cls.TOOL
