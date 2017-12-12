"""
    Settings for unpacker.
"""

from regression_tests.tools.unpacker_arguments import UnpackerArguments
from regression_tests.tools.unpacker_runner import UnpackerRunner
from regression_tests.tools.unpacker_test import UnpackerTest
from regression_tests.tools.tool_test_settings import ToolTestSettings
from regression_tests.utils import overrides


class UnpackerTestSettings(ToolTestSettings):
    """Settings for unpacker tests.

    See the description of :class:`.ToolTestSettings` for additional
    attributes.
    """

    #: Name of the tool.
    TOOL = 'unpacker'

    def __init__(self, *, run_fileinfo=False, fileinfo_args='--verbose --json',
                 fileinfo_timeout=60, **kwargs):
        """
        :param bool run_fileinfo: Should fileinfo be run after unpacking?
        :param str fileinfo_args: Arguments to be passed to fileinfo when
                                  `run_fileinfo` is ``True``.
        :param int fileinfo_timeout: Maximal running time of fileinfo.

        See the description of :class:`.ToolTestSettings` for additional
        parameters.
        """
        kwargs['tool'] = self.TOOL
        ToolTestSettings.__init__(self, **kwargs)

        # run_fileinfo
        self._verify_has_type(run_fileinfo, 'run_fileinfo', bool)
        self.run_fileinfo = run_fileinfo

        # fileinfo_args
        self._verify_has_type(fileinfo_args, 'fileinfo_args', str)
        self.fileinfo_args = fileinfo_args

        # fileinfo_timeout
        self._verify_has_type(fileinfo_timeout, 'fileinfo_timeout', int)
        self.fileinfo_timeout = fileinfo_timeout

    @property
    @overrides(ToolTestSettings)
    def tool_arguments_class(self):
        return UnpackerArguments

    @property
    @overrides(ToolTestSettings)
    def tool_runner_class(self):
        return UnpackerRunner

    @property
    @overrides(ToolTestSettings)
    def tool_test_class(self):
        return UnpackerTest

    @classmethod
    @overrides(ToolTestSettings)
    def should_be_created_from(cls, **kwargs):
        return kwargs.get('tool') == cls.TOOL
