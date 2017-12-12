"""
    A representation of an unpacker that has run.
"""

from regression_tests.tools.tool import Tool
from regression_tests.utils import overrides


class Unpacker(Tool):
    """A representation of an unpacker that has run."""

    def __init__(self, *args, fileinfo=None, **kwargs):
        """
        :param Fileinfo fileinfo: Fileinfo run (if it has run).

        Other parameters are passed directory to
        :class:`~regression_tests.tools.tool.Tool`'s constructor.
        """
        self._fileinfo = fileinfo
        super().__init__(*args, **kwargs)

    @property
    def input_file(self):
        """The input file (:class:`.File`)."""
        return self.args.input_files[0]

    @property
    @overrides(Tool)
    def succeeded(self):
        if not super().succeeded:
            return False
        return self._output_file_exists()

    @property
    def fileinfo(self):
        """Access to the fileinfo run after unpacking.

        :raises AssertionError: If fileinfo did not run.

        To run fileinfo after unpacker, pass ``run_fileinfo=True`` in test
        settings, e.g.

        .. code-block:: python

            settings = TestSettings(
                tool='unpacker',
                input='file.exe',
                run_fileinfo=True  # By default, this is False.
            )

        As the comment suggests, by default, fileinfo does not run. See the
        description of :class:~regression_tests.tools.unpacker_test_settings`
        for more fileinfo-related parameters.
        """
        if self._fileinfo is None:
            raise AssertionError('fileinfo did not run')

        return self._fileinfo

    @property
    def _output_file_name(self):
        """Name of the output file."""
        return self.args.output_file.name

    def _output_file_exists(self):
        """Does the output file exists?"""
        return self._file_exists(self._output_file_name)
