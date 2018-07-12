"""
    A representation of a generic tool that has run.
"""

import re

from regression_tests.utils import memoize
from regression_tests.parsers.text_parser import Text


class Tool:
    """A representation of a generic tool that has run."""

    def __init__(self, name, dir, args, cmd_runner, output, return_code,
                 timeouted):
        """
        :param str name: Name of the tool.
        :param Directory dir: Base directory for the outputs of the tool.
        :param ToolArguments args: Arguments of the tool.
        :param CmdRunner cmd_runner: Runner of external commands.
        :param str output: Output from the tool.
        :param int return_code: Return code of the tool.
        :param bool timeouted: Has the tool timeouted?
        """
        self._name = name
        self._dir = dir
        self._args = args
        self._cmd_runner = cmd_runner
        self._output = output
        self._return_code = return_code
        self._timeouted = timeouted

    @property
    def name(self):
        """Name of the tool (`str`)."""
        return self._name

    @property
    def safe_name(self):
        """Safe name of the tool (`str`).

        The returned name is non-empty, starts with a letter or underscore, and
        contains just characters from range ``[a-zA-Z0-9_]``. Other characters
        are replaced with underscores. Examples:

        .. code-block:: python

            Tool(name='Tool', ...).safe_name == 'Tool'
            Tool(name='test me.py', ...).safe_name == 'test_me_py'
            Tool(name='9tool', ...).safe_name == '_9tool'
            Tool(name='', ...).safe_name == '_'
        """
        safe_name = re.sub('[^a-zA-Z0-9_]', '_', self._name)
        if not re.match(r'^[a-zA-Z_]', safe_name):
            safe_name = '_' + safe_name
        return safe_name

    @property
    def dir(self):
        """Base directory for the outputs of the tool
        (:class:`.Directory`).
        """
        return self._dir

    @property
    def args(self):
        """Arguments of the tool
        (:class:`.ToolArguments`).
        """
        return self._args

    @property
    def return_code(self):
        """Return code of the tool (`int`)."""
        return self._return_code

    @property
    def succeeded(self):
        """Has the tool succeeded?"""
        return self.return_code == 0

    @property
    def failed(self):
        """Has the tool failed?"""
        return not self.succeeded

    @property
    @memoize
    def output(self):
        """Output from the tool (:class:`.Text`)."""
        return Text(self._output)

    def end_of_output(self, lines=10):
        """Returns the last `lines` from the output."""
        return self._end_of(self.output, lines)

    @property
    def timeouted(self):
        """Has the tool timeouted?"""
        return self._timeouted

    @property
    def input_files(self):
        """A tuple of input files (:class:`.File`).

        If there was only a single file, it returns a singleton tuple. If the
        tool had no input files, it returns the empty tuple.
        """
        return self.args.input_files

    @property
    def log_file_name(self):
        """Name of the log file."""
        # We can name the log file after the input file, provided that there is
        # only a single input file. Otherwise, we use just the tool name.
        if len(self.args.input_files) == 1:
            base = self.args.input_files[0].name
        else:
            base = self.name
        return '{}.log'.format(base)

    @property
    def log_file(self):
        """Log file."""
        return self._get_file(self.log_file_name)

    @property
    @memoize
    def log(self):
        """Contents of the log file."""
        return self.log_file.text

    def end_of_log(self, lines=10):
        """Returns the last `lines` from the log."""
        return self._end_of(self.log, lines)

    def _run_cmd(self, *args, **kwargs):
        """Runs the given command with the given arguments by passing it to the
        command runner.
        """
        return self._cmd_runner.run_cmd(*args, **kwargs)

    def _get_file(self, name):
        """Returns the file with the given name."""
        return self.dir.get_file(name)

    def _file_exists(self, name):
        """Does a file with the given name exist?"""
        return self.dir.file_exists(name)

    def _end_of(self, output, lines):
        """Returns the last `lines` from `output`."""
        return '\n'.join(output.split('\n')[-lines:])
