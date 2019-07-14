"""
    Tests for the :mod:`regression_tests.tools.r2plugin` module.
"""

from unittest import mock

from regression_tests.filesystem.directory import Directory
from regression_tests.filesystem.file import File
from regression_tests.tools.r2plugin import R2Plugin
from regression_tests.tools.r2plugin_arguments import R2PluginArguments
from tests.tools.tool_tests import ToolTestsBase


class R2PluginTests(ToolTestsBase):
    """Tests for `R2Plugin`."""

    def setUp(self):
        super().setUp()
        self.name = 'r2plugin'
        self.args = R2PluginArguments(
            input_files=(File('prog.exe', Directory('/test')),),
            output_file=File('prog.c', Directory('/test/outputs'))
        )
        self.r2plugin = self.create_r2plugin()

    def create_r2plugin(self, **kwargs):
        """Creates an R2 plugin with the given arguments."""
        return self.create_tool(cls=R2Plugin, **kwargs)

    def test_input_file_returns_file_with_correct_name(self):
        self.assertEqual(self.r2plugin.input_file.name, 'prog.exe')

    def test_out_c_file_returns_correct_file(self):
        self.dir.get_file.return_value = self.args.output_file
        self.assertEqual(self.r2plugin.out_c_file, self.args.output_file)

    def test_out_c_returns_contents_of_out_c_file(self):
        OUT_C = 'int main() { return 0; }'
        file = mock.Mock(spec_set=File)
        type(file).text = mock.PropertyMock(return_value=OUT_C)
        self.dir.get_file.return_value = file
        self.assertEqual(self.r2plugin.out_c, OUT_C)

    def test_succeeded_returns_false_if_return_code_is_nonzero(self):
        self.r2plugin = self.create_r2plugin(
            return_code=1
        )
        self.assertFalse(self.r2plugin.succeeded)

    def test_succeeded_checks_existence_of_output_file_if_return_code_is_zero(self):
        self.dir.file_exists.return_value = True
        self.r2plugin = self.create_r2plugin(
            return_code=0
        )

        self.assertTrue(self.r2plugin.succeeded)

        self.dir.file_exists.assert_called_once_with('prog.c')

    def test_succeeded_returns_true_if_return_code_is_zero_and_output_file_was_created(self):
        self.dir.file_exists.return_value = True
        self.r2plugin = self.create_r2plugin(
            return_code=0
        )
        self.assertTrue(self.r2plugin.succeeded)

    def test_succeeded_returns_false_if_return_code_is_zero_but_output_file_was_not_created(self):
        self.dir.file_exists.return_value = False
        self.r2plugin = self.create_r2plugin(
            return_code=0
        )
        self.assertFalse(self.r2plugin.succeeded)
