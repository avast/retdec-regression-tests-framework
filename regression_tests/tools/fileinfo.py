"""
    A representation of a fileinfo that has run.
"""

from regression_tests.parsers.fileinfo_output_parser import FileinfoOutput
from regression_tests.tools.tool import Tool
from regression_tests.utils import memoize


class Fileinfo(Tool):
    """A representation of a fileinfo that has run."""

    @property
    def input_file(self):
        """The input file (:class:`.File`)."""
        return self.args.input_files[0]

    @property
    @memoize
    def output(self):
        """Parsed output (:class:`.FileinfoOutput`)."""
        return FileinfoOutput(self._output)
