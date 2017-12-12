"""
    Name of a test case.
"""

import re


class TestCaseName(str):
    """Name of a test case.

    It behaves like a string with additional methods.

    The name should be of the following form: ``'$CLASS_NAME ($INPUT_FILES
    $ARGUMENTS)'``. Both ``$INPUT_FILES`` and ``$ARGUMENTS`` are optional.
    """

    @property
    def class_name(self):
        """Class name."""
        return re.sub(r'^([^ ]+) \(.*\)$', r'\1', self)

    @property
    def input_files(self):
        """Input files."""
        files_and_args = re.sub(r'^[^ ]+ \((.*)\)$', r'\1', self)
        files = re.sub(r' -.*', '', files_and_args)
        return files if not files.startswith('-') else ''

    @property
    def tool_args(self):
        """Tool arguments, including input files."""
        return re.sub(r'^[^ ]+ \((.*)\)$', r'\1', self)

    def short_tool_args(self, limit=30):
        """Returns shortened tool arguments, including input files."""
        return self._shorten_args_if_necessary(self.tool_args, limit)

    @property
    def args(self):
        """Arguments, excluding input files."""
        return self.tool_args[len(self.input_files):].strip()

    def short_args(self, limit=30):
        """Returns shortened arguments, excluding input files."""
        return self._shorten_args_if_necessary(self.args, limit)

    def with_short_args(self, limit=30):
        """Returns a name with shortened arguments.

        See the description of :func:`short_args()` for more details.
        """
        short_args = self.short_args(limit)
        return self.__class__(
            '{} ({}{}{})'.format(
                self.class_name,
                self.input_files,
                ' ' if short_args else '',
                short_args
            )
        )

    @classmethod
    def from_tool_arguments(cls, test_name, tool_arguments):
        """Creates :class:`.TestCaseName` from the given arguments.

        :param str test_name: Name of the test.
        :param ToolArguments tool_arguments: Arguments of the tool.
        """
        return TestCaseName(
            '{} ({})'.format(
                test_name,
                tool_arguments.without_paths_and_output_files.as_str
            )
        )

    @staticmethod
    def _shorten_args_if_necessary(args, limit):
        """Shortens the given arguments when they are longer than `limit`."""
        if len(args) <= limit:
            return args

        ellipsis = '[..]'
        return args[:limit - len(ellipsis)] + ellipsis
