"""
    Tests for the :mod:`regression_tests.tools.unpacker` module.
"""

from unittest import mock

from regression_tests.filesystem.directory import Directory
from regression_tests.filesystem.file import File
from regression_tests.tools.unpacker import Unpacker
from regression_tests.tools.unpacker_arguments import UnpackerArguments
from tests.tools.tool_tests import ToolTestsBase


class UnpackerTests(ToolTestsBase):
    """Tests for `Unpacker`."""

    def setUp(self):
        super().setUp()
        self.name = 'unpacker'
        self.args = UnpackerArguments(
            input_files=(File('prog.exe', Directory('/test')),),
            output_file=File('prog.exe-unpacked', Directory('/test/outputs'))
        )
        self.unpacker = self.create_unpacker()

    def create_unpacker(self, **kwargs):
        """Creates an unpacker with the given arguments."""
        return self.create_tool(cls=Unpacker, **kwargs)

    def test_input_file_returns_file_with_correct_name(self):
        self.assertEqual(self.unpacker.input_file.name, 'prog.exe')

    def test_succeeded_returns_false_if_return_code_is_nonzero(self):
        self.unpacker = self.create_unpacker(
            return_code=1
        )
        self.assertFalse(self.unpacker.succeeded)

    def test_succeeded_checks_existence_of_output_file_if_return_code_is_zero(self):
        self.dir.file_exists.return_value = True
        self.unpacker = self.create_unpacker(
            return_code=0
        )

        self.unpacker.succeeded

        self.dir.file_exists.assert_called_once_with('prog.exe-unpacked')

    def test_succeeded_returns_true_if_return_code_is_zero_and_output_file_was_created(self):
        self.dir.file_exists.return_value = True
        self.unpacker = self.create_unpacker(
            return_code=0
        )
        self.assertTrue(self.unpacker.succeeded)

    def test_succeeded_returns_false_if_return_code_is_zero_but_output_file_was_not_created(self):
        self.dir.file_exists.return_value = False
        self.unpacker = self.create_unpacker(
            return_code=0
        )
        self.assertFalse(self.unpacker.succeeded)

    def test_fileinfo_raises_exception_when_it_did_not_run(self):
        self.unpacker = self.create_unpacker(fileinfo=None)
        with self.assertRaisesRegex(AssertionError, r'.*fileinfo did not run.*'):
            self.unpacker.fileinfo

    def test_fileinfo_returns_fileinfo_when_it_ran(self):
        fileinfo = mock.Mock()
        self.unpacker = self.create_unpacker(fileinfo=fileinfo)
        self.assertEqual(self.unpacker.fileinfo, fileinfo)
