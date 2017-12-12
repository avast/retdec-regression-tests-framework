"""
    Tests for the :mod:`regression_tests.tools.bin2pat` module.
"""

from unittest import mock

from regression_tests.filesystem.directory import Directory
from regression_tests.filesystem.file import File
from regression_tests.tools.bin2pat import Bin2Pat
from regression_tests.tools.bin2pat_arguments import Bin2PatArguments
from tests.tools.tool_tests import ToolTestsBase


class Bin2PatTests(ToolTestsBase):
    """Tests for `Bin2Pat`."""

    def setUp(self):
        super().setUp()
        self.name = 'bin2pat'
        self.args = Bin2PatArguments(
            input_files=(File('mod.o', Directory('/test')),),
            output_file=File('out.yara', Directory('/test/outputs'))
        )
        self.bin2pat = self.create_bin2pat()

    def create_bin2pat(self, **kwargs):
        """Creates a bin2pat with the given arguments."""
        return self.create_tool(cls=Bin2Pat, **kwargs)

    def test_input_file_returns_file_with_correct_name(self):
        self.assertEqual(self.bin2pat.input_file.name, 'mod.o')

    def test_out_yara_file_returns_correct_file(self):
        self.dir.get_file.return_value = self.args.output_file
        self.assertEqual(self.bin2pat.out_yara_file, self.args.output_file)

    def test_out_yara_returns_contents_of_out_yara_file(self):
        out_yara = 'rule ruleName [..]'
        file = mock.Mock(spec_set=File)
        type(file).text = mock.PropertyMock(return_value=out_yara)
        self.dir.get_file.return_value = file
        self.assertEqual(self.bin2pat.out_yara, out_yara)
