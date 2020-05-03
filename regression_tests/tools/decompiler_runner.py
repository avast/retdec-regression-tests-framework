"""
    A runner of decompilations.
"""

from regression_tests.tools.decompiler import Decompiler
from regression_tests.tools.tool_runner import ToolRunner
from regression_tests.utils import overrides


class DecompilerRunner(ToolRunner):
    """A runner of decompilations."""

    @property
    @overrides(ToolRunner)
    def _tool_class(self):
        return Decompiler

    @overrides(ToolRunner)
    def _get_tool_executable_name(self, tool_name):
        return 'retdec-decompiler'

    @overrides(ToolRunner)
    def _initialize_tool_dir_and_args(self, dir, args):
        if args.config_file is not None:
            # We have to copy the input configuration file to the output
            # directory to prevent its rewriting (see #1349).
            return self._copy_config_file_to_tool_dir(dir, args)

        return args

    def _copy_config_file_to_tool_dir(self, dir, args):
        new_config_file = dir.copy_file(args.config_file)
        return args.clone_but(config_file=new_config_file)
