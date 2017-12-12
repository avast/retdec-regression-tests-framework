"""
    Build of RetDec.
"""

from datetime import datetime

from regression_tests.utils.os import chdir


class BuildInfo:
    """Information about a RetDec build."""

    def __init__(self, start_date, end_date, succeeded, log):
        """
        :param datetime start_date: Date and time the build started.
        :param datetime end_date: Date and time the build ended.
        :param bool succeeded: Has the build succeeded?
        :param str log: Log from the build.
        """
        self.start_date = start_date
        self.end_date = end_date
        self.succeeded = succeeded
        self.log = log

    @property
    def runtime(self):
        """Runtime of the build in seconds.

        Returns ``None`` if the build has not ended yet.
        """
        if not self.has_ended():
            return None
        return (self.end_date - self.start_date).total_seconds()

    def has_started(self):
        """Has the build started?"""
        return self.start_date is not None

    def has_ended(self):
        """Has the build ended?"""
        return self.end_date is not None


class NoBuildInfo(BuildInfo):
    """No build info.

    Implements the Null object design pattern.
    """

    def __init__(self):
        super().__init__(
            start_date=None,
            end_date=None,
            succeeded=True,
            log=''
        )


def build_retdec(build_dir, cmd_runner, procs=0):
    """Builds RetDec.

    :param Directory build_dir: The build directory
    :param CmdRunner cmd_runner: Runner of external commands to be used.
    :param int procs: Number of processors to be used (0 means auto detection).

    :returns: Information about the build (:class:`.BuildInfo`).
    """
    with chdir(build_dir.path):
        start_date = datetime.now()

        # First, we have to build RetDec, and then install it (we cannot do
        # both in one command).
        make_cmd = _get_make_cmd(procs)
        # Build.
        build_cmd = _get_build_cmd(make_cmd)
        output, return_code, _ = cmd_runner.run_cmd(build_cmd)
        if return_code == 0:
            # Installation.
            install_cmd = _get_install_cmd(make_cmd)
            install_output, return_code, _ = cmd_runner.run_cmd(install_cmd)
            output += install_output

        return BuildInfo(
            start_date=start_date,
            end_date=datetime.now(),
            succeeded=return_code == 0,
            log=output
        )


def _get_make_cmd(procs):
    """Returns a ``make`` command for the given number of processors (0 means
    auto detection).
    """
    make_cmd = ['./make.sh']
    if procs != 0:
        make_cmd += ['-j', procs]
    return make_cmd


def _get_build_cmd(make_cmd):
    """Returns a build command from the given ``make`` command."""
    # The build command is the same as the make command.
    return make_cmd


def _get_install_cmd(make_cmd):
    """Returns an installation command from the given ``make`` command."""
    return make_cmd + ['install']
