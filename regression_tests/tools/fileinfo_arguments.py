"""
    A representation of fileinfo arguments.
"""

from regression_tests.filesystem.file import StandaloneFile
from regression_tests.tools.tool_arguments import ToolArguments
from regression_tests.utils import overrides


class FileinfoArguments(ToolArguments):
    """A representation of fileinfo arguments."""

    def __init__(self, *, config_file=None, **kwargs):
        """
        :param File config_file: Output configuration file.

        All arguments are passed to :class:`.ToolArguments`.
        """
        super().__init__(**kwargs)
        self.config_file = config_file

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

        # Configuration file.
        if self.config_file is not None:
            arg_list.extend(['-c', self.config_file.path])

        # Additional arguments.
        arg_list.extend(self.args_as_list)

        return arg_list

    @property
    @overrides(ToolArguments)
    def without_paths_and_output_files(self):
        args = self.clone()
        args._remove_paths_from_files_attr('input_files')
        # The configuration file is an output file.
        args.config_file = None
        return args

    @overrides(ToolArguments)
    def with_rebased_files(self, inputs_dir, outputs_dir):
        args = self.clone()
        args._rebase_files_attr('input_files', inputs_dir)
        args._rebase_file_attr('config_file', outputs_dir)
        return args

    @classmethod
    @overrides(ToolArguments)
    def from_test_settings(cls, test_settings):
        args = FileinfoArguments()

        # Input file.
        cls._verify_attr_is_set(test_settings, 'input')
        cls._verify_attr_is_not_list(test_settings, 'input')
        args._set_files_attr_if_not_none(test_settings, 'input')

        # Output configuration file.
        args.config_file = StandaloneFile(
            args._get_config_file_name_from_input_file_name())

        # Additional arguments.
        cls._verify_attr_is_not_list(test_settings, 'args')
        args._set_attr_if_not_none(test_settings, 'args')

        return args

    def _get_config_file_name_from_input_file_name(self):
        """Returns the name of the output configuration file from the input
        file.
        """
        return self.input_file.name + '.config.json'
