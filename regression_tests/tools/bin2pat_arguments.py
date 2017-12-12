"""
    A representation of bin2pat arguments.
"""

from regression_tests.filesystem.file import StandaloneFile
from regression_tests.tools.tool_arguments import ToolArguments
from regression_tests.utils import overrides


class Bin2PatArguments(ToolArguments):
    """A representation of bin2pat arguments."""

    def __init__(self, *, output_file=None, **kwargs):
        """
        :param File output_file: Output file.

        All arguments are passed to :class:`.ToolArguments`.
        """
        super().__init__(**kwargs)
        self.output_file = output_file

    @property
    def input_file(self):
        """The input file (:class:`.File`)."""
        return self.input_files[0]

    @property
    @overrides(ToolArguments)
    def as_list(self):
        arg_list = []

        # Input file.
        if self.input_files:
            arg_list.append(self.input_file.path)

        # Output file.
        if self.output_file is not None:
            arg_list.extend(['-o', self.output_file.path])

        # Additional arguments.
        arg_list.extend(self.args_as_list)

        return arg_list

    @property
    @overrides(ToolArguments)
    def without_paths_and_output_files(self):
        args = self.clone()
        args._remove_paths_from_files_attr('input_files')
        args.output_file = None
        return args

    @overrides(ToolArguments)
    def with_rebased_files(self, inputs_dir, outputs_dir):
        args = self.clone()
        args._rebase_files_attr('input_files', inputs_dir)
        args._rebase_file_attr('output_file', outputs_dir)
        return args

    @classmethod
    @overrides(ToolArguments)
    def from_test_settings(cls, test_settings):
        args = Bin2PatArguments()

        # Input file.
        cls._verify_attr_is_set(test_settings, 'input')
        cls._verify_attr_is_not_list(test_settings, 'input')
        args._set_files_attr_if_not_none(test_settings, 'input')

        # Output file.
        args.output_file = StandaloneFile(
            args._get_output_file_name_from_input_file_name())

        # Additional arguments.
        cls._verify_attr_is_not_list(test_settings, 'args')
        args._set_attr_if_not_none(test_settings, 'args')

        return args

    def _get_output_file_name_from_input_file_name(self):
        """Returns the name of the output file from the input file."""
        return self.input_file.name + '.yara'
