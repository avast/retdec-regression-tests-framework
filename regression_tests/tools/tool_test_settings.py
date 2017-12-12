"""
    Generic tool test settings.
"""

from regression_tests.test_settings import TestSettings
from regression_tests.tools.tool_arguments import ToolArguments
from regression_tests.tools.tool_runner import ToolRunner
from regression_tests.tools.tool_test import ToolTest
from regression_tests.utils.list import as_list


class ToolTestSettings(TestSettings):
    """Generic tool test settings."""

    def __init__(self, *, tool, input=None, args=None, timeout=1200, **kwargs):
        """
        :param str tool: Name of the tested tool.
        :param str/list input: Input file(s).
        :param str/list args: Arguments passed directly to the tool.
        :param int timeout: Timeout for the tool.

        The `input` and `args` parameters can be either a single item or a
        non-empty list of items. If any of the lists contains duplicates, they
        are merged.
        """
        TestSettings.__init__(self, **kwargs)

        self._verify_not_empty_list(input, 'input')
        self._verify_not_empty_list(args, 'args')

        self.tool = tool
        self.input = self._merge_duplicates(input)
        self.args = self._merge_duplicates(args)
        self.timeout = timeout

    @property
    def input_as_list(self):
        """Input file(s) as a list.

        When the input is not set, the empty list is returned. When there is
        only a single input, a singleton list is returned. When the input is a
        list, it is returned directly.
        """
        return as_list(self.input)

    def has_multiple_inputs(self):
        """Checks if the settings contains multiple inputs.

        :returns: ``True`` if the settings contains multiple inputs, ``False``
                  otherwise.
        """
        return self._has_multiple_values_for_attr('input')

    @property
    def args_as_list(self):
        """Arguments passed directly to the tool as a list.

        When there are no arguments, the empty list is returned. When there are
        only a single arguments, a singleton list is returned. When there are
        multiple arguments, a list of them is returned.
        """
        return as_list(self.args)

    def has_multiple_args(self):
        """Checks if the settings contains multiple high-level languages.

        :returns: ``True`` if the settings contains multiple high-level
                  languages, ``False`` otherwise.
        """
        return self._has_multiple_values_for_attr('args')

    @property
    def tool_arguments_class(self):
        """Class to be used to instantiate an instance of
        :class:`.ToolArguments` or its subclass.
        """
        return ToolArguments

    @property
    def tool_arguments(self):
        """Arguments for the tool created from the test settings."""
        return self.tool_arguments_class.from_test_settings(self)

    @property
    def tool_runner_class(self):
        """Class to be used to instantiate an instance of :class:`.ToolRunner`
        or its subclass.
        """
        return ToolRunner

    def get_tool_runner(self, cmd_runner, tools_dir):
        """Returns a runner for the tool.

        :param CmdRunner cmd_runner: Runner of external commands to be used.
        :param Directory tools_dir: Directory where the tested tools are
                                    located.
        """
        return self.tool_runner_class(cmd_runner, tools_dir, self)

    @property
    def tool_test_class(self):
        """Class to be used to instantiate an instance of :class:`.ToolTest` or
        its subclass.
        """
        return ToolTest

    @classmethod
    def should_be_created_from(cls, **kwargs):
        """Should the test settings be created from the given arguments?"""
        return kwargs.get('tool', False)
