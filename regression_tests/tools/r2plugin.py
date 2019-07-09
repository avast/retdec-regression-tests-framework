"""
    A representation of an r2 plugin that has run.
"""

from regression_tests.tools.tool import Tool
from regression_tests.utils import memoize
from regression_tests.utils import overrides


class R2Plugin(Tool):
    """A representation of an r2 plugin that has run."""

    @property
    def input_file(self):
        """The input file (:class:`.File`)."""
        return self.args.input_files[0]

    @property
    def out_c_file(self):
        """Output C file."""
        return self._get_file(self._out_c_file_name)

    @property
    @memoize
    def out_c(self):
        """Contents of the output C file."""
        return self.out_c_file.text

    @property
    @overrides(Tool)
    def succeeded(self):
        if not super().succeeded:
            return False
        return self.out_c_file_exists()

    @property
    def _out_c_file_name(self):
        """Name of the output C file."""
        return self.args.output_file.name

    def out_c_file_exists(self):
        """Does the output C file exists?"""
        return self._file_exists(self._out_c_file_name)
