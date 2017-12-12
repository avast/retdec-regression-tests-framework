"""
    Tests for the :mod:`regression_tests.tools.idaplugin` module.
"""

from unittest import mock

from regression_tests.filesystem.directory import Directory
from regression_tests.filesystem.file import File
from regression_tests.tools.idaplugin import IDAPlugin
from regression_tests.tools.idaplugin_arguments import IDAPluginArguments
from tests.tools.tool_tests import ToolTestsBase


class IDAPluginTests(ToolTestsBase):
    """Tests for `IDAPlugin`."""

    def setUp(self):
        super().setUp()
        self.name = 'idaplugin'
        self.args = IDAPluginArguments(
            input_files=(File('prog.exe', Directory('/test')),),
            output_file=File('prog.c', Directory('/test/outputs'))
        )
        self.idaplugin = self.create_idaplugin()

    def create_idaplugin(self, **kwargs):
        """Creates an IDA plugin with the given arguments."""
        return self.create_tool(cls=IDAPlugin, **kwargs)

    def test_input_file_returns_file_with_correct_name(self):
        self.assertEqual(self.idaplugin.input_file.name, 'prog.exe')

    def test_out_c_file_returns_correct_file(self):
        self.dir.get_file.return_value = self.args.output_file
        self.assertEqual(self.idaplugin.out_c_file, self.args.output_file)

    def test_out_c_returns_contents_of_out_c_file(self):
        OUT_C = 'int main() { return 0; }'
        file = mock.Mock(spec_set=File)
        type(file).text = mock.PropertyMock(return_value=OUT_C)
        self.dir.get_file.return_value = file
        self.assertEqual(self.idaplugin.out_c, OUT_C)

    def test_succeeded_returns_false_if_return_code_is_nonzero(self):
        self.idaplugin = self.create_idaplugin(
            return_code=1
        )
        self.assertFalse(self.idaplugin.succeeded)

    def test_succeeded_checks_existence_of_output_file_if_return_code_is_zero(self):
        self.dir.file_exists.return_value = True
        self.idaplugin = self.create_idaplugin(
            return_code=0
        )

        self.idaplugin.succeeded

        self.dir.file_exists.assert_called_once_with('prog.c')

    def test_succeeded_returns_true_if_return_code_is_zero_and_output_file_was_created(self):
        self.dir.file_exists.return_value = True
        self.idaplugin = self.create_idaplugin(
            return_code=0
        )
        self.assertTrue(self.idaplugin.succeeded)

    def test_succeeded_returns_false_if_return_code_is_zero_but_output_file_was_not_created(self):
        self.dir.file_exists.return_value = False
        self.idaplugin = self.create_idaplugin(
            return_code=0
        )
        self.assertFalse(self.idaplugin.succeeded)
