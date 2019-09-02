"""
    A representation of r2 plugin arguments.
"""

from regression_tests.filesystem.file import StandaloneFile
from regression_tests.tools.tool_arguments import ToolArguments
from regression_tests.utils import overrides


class R2PluginArguments(ToolArguments):
    """A representation of r2 plugin arguments."""

    def __init__(self, *, project_file=None, output_file=None, commands=None, **kwargs):
        """
        :param File project_file: Input R2 project file.
        :param File output_file: Output file.

        All arguments are passed to :class:`.ToolArguments`.
        """
        super().__init__(**kwargs)
        self.project_file = project_file
        self.output_file = output_file
        self.commands = commands

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

        # R2 project file.
        if self.project_file is not None:
            arg_list.extend(['--project', self.project_file.path])

        # Output file.
        if self.output_file is not None:
            arg_list.extend(['-o', self.output_file.path])

        if self.commands:
            if type(self.commands) is tuple:
                arg_list.extend(['-c', ';'.join(self.commands)])

            else:
                arg_list.extend(['-c', self.commands])

        # Additional arguments.
        arg_list.extend(self.args_as_list)

        return arg_list

    @property
    @overrides(ToolArguments)
    def without_paths_and_output_files(self):
        args = self.clone()
        args._remove_paths_from_files_attr('input_files')
        args._remove_path_from_file_attr('project_file')
        args.output_file = None
        return args

    @overrides(ToolArguments)
    def with_rebased_files(self, inputs_dir, outputs_dir):
        args = self.clone()
        args._rebase_files_attr('input_files', inputs_dir)
        args._rebase_file_attr('project_file', inputs_dir)
        args._rebase_file_attr('output_file', outputs_dir)
        return args

    @classmethod
    @overrides(ToolArguments)
    def from_test_settings(cls, test_settings):
        args = R2PluginArguments()

        # Input file.
        cls._verify_attr_is_set(test_settings, 'input')
        cls._verify_attr_is_not_list(test_settings, 'input')
        args._set_files_attr_if_not_none(test_settings, 'input')

        # R2 project file.
        cls._verify_attr_is_not_list(test_settings, 'project')
        args._set_file_attr_if_not_none(test_settings, 'project')

        # R2 init commands.
        args._set_attr_if_not_none(test_settings, 'commands')

        # Output file.
        args.output_file = StandaloneFile(
            args._get_output_file_name_from_input_file_name())

        # Additional arguments.
        cls._verify_attr_is_not_list(test_settings, 'args')
        args._set_attr_if_not_none(test_settings, 'args')

        return args

    def _get_output_file_name_from_input_file_name(self):
        """Returns the name of the output file from the input file."""
        input_file_name = self.input_file.name
        if input_file_name.endswith('.exe'):
            return input_file_name[:-4] + '.c'
        return input_file_name + '.c'
