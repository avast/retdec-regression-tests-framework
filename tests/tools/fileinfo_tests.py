"""
    Tests for the :mod:`regression_tests.tools.fileinfo` module.
"""

from regression_tests.filesystem.directory import Directory
from regression_tests.filesystem.file import File
from regression_tests.tools.fileinfo import Fileinfo
from regression_tests.tools.fileinfo_arguments import FileinfoArguments
from tests.tools.tool_tests import ToolTestsBase


class FileinfoTests(ToolTestsBase):
    """Tests for `Fileinfo`."""

    def setUp(self):
        super().setUp()
        self.name = 'fileinfo'
        self.args = FileinfoArguments(
            input_files=(File('prog.exe', Directory('/test')),)
        )
        self.fileinfo = self.create_fileinfo()

    def create_fileinfo(self, **kwargs):
        """Creates a fileinfo with the given arguments."""
        return self.create_tool(cls=Fileinfo, **kwargs)

    def test_input_file_returns_file_with_correct_name(self):
        self.assertEqual(self.fileinfo.input_file.name, 'prog.exe')

    def test_output_returns_parsed_output(self):
        self.fileinfo = self.create_fileinfo(
            output='Architecture: x86'
        )
        self.assertEqual(self.fileinfo.output['Architecture'], 'x86')
