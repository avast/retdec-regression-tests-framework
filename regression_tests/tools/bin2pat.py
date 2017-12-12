"""
    A representation of a bin2pat that has run.
"""

from regression_tests.tools.tool import Tool
from regression_tests.utils import memoize


class Bin2Pat(Tool):
    """A representation of a bin2pat that has run."""

    @property
    def input_file(self):
        """The input file (:class:`.File`)."""
        return self.args.input_files[0]

    @property
    def out_yara_file(self):
        """Output YARA file."""
        return self._get_file(self._out_yara_file_name)

    @property
    @memoize
    def out_yara(self):
        """Contents of the output YARA file."""
        return self.out_yara_file.text

    @property
    def _out_yara_file_name(self):
        """Name of the output YARA file."""
        return self.args.output_file.name
