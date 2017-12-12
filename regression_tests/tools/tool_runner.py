"""
    A generic tool runner.
"""

import os

from regression_tests.tools.tool import Tool


class ToolRunner:
    """A generic tool runner."""

    def __init__(self, cmd_runner, tools_dir, test_settings):
        """
        :param CmdRunner cmd_runner: Runner of external commands to be used.
        :param Directory tools_dir: Directory where the tested tools are
                                    located.
        :param ToolTestSettings test_settings: Settings of the tested tool.
        """
        self._cmd_runner = cmd_runner
        self._tools_dir = tools_dir
        self._test_settings = test_settings

    def run_tool(self, tool_name, args, dir, timeout):
        """Runs the tool with the given arguments.

        :param str tool_name: Name of the tool to run.
        :param ToolArguments args: Arguments to be passed to the tool.
        :param Directory dir: Directory where the outputs from the tool will be
                              stored.
        :param int timeout: Timeout (in seconds).

        :returns: The run tool (:class:`.Tool`).
        """
        self._create_tool_dir(dir)
        args = self._initialize_tool_dir_and_args(dir, args)
        output, return_code, timeouted = self._run_tool(
            tool_name,
            args,
            timeout
        )
        tool = self._get_tool(
            tool_name,
            args,
            dir,
            output,
            return_code,
            timeout,
            timeouted
        )
        self._create_and_store_log(dir, tool, timeout)
        return tool

    def _create_tool_dir(self, dir):
        """Creates the directory for the tool."""
        dir.create(erase_if_exists=True)

    def _initialize_tool_dir_and_args(self, dir, args):
        """Initializes the tool directory and arguments.

        Returns new arguments to be used to run the tool.
        """
        # By default, there is nothing to do.
        return args

    def _run_tool(self, tool_name, args, timeout):
        """Runs the tool and returns the results."""
        executable_name = self._get_tool_executable_name(tool_name)
        return self._cmd_runner.run_cmd(
            [os.path.join(self._tools_dir.path, executable_name)] + args.as_list,
            strip_shell_colors=True,
            timeout=timeout
        )

    @property
    def _tool_class(self):
        """Returns a class to be used to create a tool instance."""
        return Tool

    def _get_tool_executable_name(self, tool_name):
        """Returns the name of an executable to run the given tool."""
        # By default, assume that the tool's name is also the name of the
        # executable.
        return tool_name

    def _get_tool(self, tool_name, args, dir, output, return_code, timeout,
                  timeouted):
        """Creates a tool from the given arguments."""
        return self._tool_class(
            tool_name,
            dir,
            args,
            self._cmd_runner,
            output,
            return_code,
            timeouted
        )

    def _create_and_store_log(self, dir, tool, timeout):
        """Creates a log and stores it."""
        log = self._create_log(tool, timeout)
        self._store_log(log, tool, dir)

    def _create_log(self, tool, timeout):
        """Creates a log for the given tool."""
        log_header = self._create_log_header(tool, timeout)
        log_body = self._create_log_body(tool)
        log_footer = self._create_log_footer(tool)
        log = '\n\n'.join([log_header, log_body, log_footer])
        return log.strip() + '\n'

    def _create_log_header(self, tool, timeout):
        """Creates the header for the tool log."""
        return '\n'.join([
            '# Command: {} {}'.format(
                self._get_tool_executable_name(tool.name),
                tool.args.without_paths_and_output_files.as_str
            ),
            '# Timeout: {} seconds'.format(timeout)
        ])

    def _create_log_body(self, tool):
        """Creates the body for the tool log."""
        return tool.output.strip()

    def _create_log_footer(self, tool):
        """Creates the footer for the tool log."""
        return '\n'.join([
            '# Return code: {}'.format(tool.return_code),
            '# Timeouted:   {}'.format('yes' if tool.timeouted else 'no'),
        ])

    def _combine_logs(self, log1, log2):
        """Combines the given two logs into a single log."""
        separator = '# ' + 78 * '-' + '\n'
        return '{}\n{}\n{}'.format(log1, separator, log2)

    def _store_log(self, log, tool, dir):
        """Stores the log from the given tool into the given directory."""
        dir.store_file(tool.log_file_name, log)
