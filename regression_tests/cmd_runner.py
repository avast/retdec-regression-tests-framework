"""
    A runner of external commands.
"""

import os
import re
import signal
import subprocess

from regression_tests import io
from regression_tests.utils.os import on_windows


class CmdRunner:
    """A runner of external commands."""

    def run_cmd(self, cmd, input=b'', timeout=None, input_encoding='utf-8',
                output_encoding='utf-8', strip_shell_colors=True):
        """Runs the given command (synchronously).

        :param list cmd: Command to be run as a list of arguments (strings).
        :param bytes input: Input to be used when running the command.
        :param int timeout: Number of seconds after which the command should be
                            terminated.
        :param str input_encoding: Encode the command's output in this encoding.
        :param str output_encoding: Decode the command's output in this encoding.
        :param bool strip_shell_colors: Should shell colors be stripped from
                                        the output?

        :returns: A triple (`output`, `return_code`, `timeouted`).

        The meaning of the items in the return value are:

        * `output` contains the combined output from the standard outputs and
          standard error,
        * `return_code` is the return code of the command,
        * `timeouted` is either `True` or `False`, depending on whether the
          command has timeouted.

        If `input` is a string (`str`), not `bytes`, it is decoded into `bytes`
        by using `input_encoding`.

        If `output_encoding` is not ``None``, the returned data are decoded in
        that encoding. Also, all line endings are converted to ``'\\n'``, and
        if ``strip_shell_colors`` is ``True``, shell colors are stripped.
        Otherwise, if `output_encoding` is ``None``, the data are directly
        returned as raw bytes without any conversions.

        To disable the timeout, pass ``None`` as `timeout` (the default).

        If the timeout expires before the command finishes, the value of `output`
        is the command's output generated up to the timeout.
        """
        def decode(output):
            if output_encoding is not None:
                output = output.decode(output_encoding, errors='replace')
                output = re.sub(r'\r\n?', '\n', output)
                if strip_shell_colors:
                    return io.strip_shell_colors(output)
            return output

        # The communicate() call below expects the input to be in bytes, so
        # convert it unless it is already in bytes.
        if not isinstance(input, bytes):
            input = input.encode(input_encoding)

        try:
            p = self.start(cmd)
            output, _ = p.communicate(input, timeout)
            return decode(output), p.returncode, False
        except subprocess.TimeoutExpired:
            # Kill the process, along with all its child processes.
            p.kill()
            # Finish the communication to obtain the output.
            output, _ = p.communicate()
            return decode(output), p.returncode, True

    def start(self, cmd, discard_output=False):
        """Starts the given command and returns a handler to it.

        :param list cmd: Command to be run as a list of arguments (strings).
        :param bool discard_output: Should the output be discarded instead of
                                    being buffered so it can be obtained later?

        :returns: A handler to the started command (``subprocess.Popen``).

        If the output is irrelevant for you, you should set `discard_output` to
        ``True``.
        """
        # The implementation is platform-specific because we want to be able to
        # kill the children alongside with the process.
        kwargs = dict(
            args=cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL if discard_output else subprocess.PIPE,
            stderr=subprocess.DEVNULL if discard_output else subprocess.STDOUT
        )
        if on_windows():
            return _WindowsProcess(**kwargs)
        else:
            return _LinuxProcess(**kwargs)


class _LinuxProcess(subprocess.Popen):
    """An internal wrapper around ``subprocess.Popen`` for Linux."""

    def __init__(self, **kwargs):
        # To ensure that all the process' children terminate when the process
        # is killed, we use a process group so as to enable sending a signal to
        # all the processes in the group. For that, we attach a session ID to
        # the parent process of the spawned child processes. This will make it
        # the group leader of the processes. When a signal is sent to the
        # process group leader, it's transmitted to all of the child processes
        # of this group.
        #
        # os.setsid is passed in the argument preexec_fn so it's run after
        # fork() and before exec().
        #
        # This solution is based on http://stackoverflow.com/a/4791612.
        kwargs['preexec_fn'] = os.setsid
        super().__init__(**kwargs)

    def kill(self):
        """Kills the process, including its children."""
        os.killpg(self.pid, signal.SIGTERM)


class _WindowsProcess(subprocess.Popen):
    """An internal wrapper around ``subprocess.Popen`` for Windows."""

    def __init__(self, **kwargs):
        # TODO: change for Python, either this is not needed anymore, or python3
        # should be used instead of sh. 
        #
        # Shell scripts need to be run with 'sh' on Windows. Simply running the
        # script by its path doesn't work. That is, for example, instead of
        #
        #     /path/to/retdec-decompiler.sh
        #
        # we need to run
        #
        #     sh /path/to/retdec-decompiler.sh
        #
        if 'args' in kwargs and kwargs['args'] and kwargs['args'][0].endswith('.sh'):
            kwargs['args'].insert(0, 'sh')
        super().__init__(**kwargs)

    def kill(self):
        """Kills the process, including its children."""
        # Since os.setsid() and os.killpg() are not available on Windows, we
        # have to do this differently. More specifically, we do this by calling
        # taskkill, which also kills the process' children.
        #
        # This solution is based on
        # http://mackeblog.blogspot.cz/2012/05/killing-subprocesses-on-windows-in.html
        cmd = ['taskkill', '/F', '/T', '/PID', str(self.pid)]
        subprocess.call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
