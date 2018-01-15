"""
    A representation of decompilation arguments.
"""

from regression_tests.filesystem.file import StandaloneFile
from regression_tests.tools.tool_arguments import ToolArguments
from regression_tests.utils import overrides


class DecompilerArguments(ToolArguments):
    """A representation of decompilation arguments."""

    def __init__(self, *, pdb_file=None, config_file=None, static_code_archive=None,
                 static_code_sigfile=None, arch=None, format=None, mode=None,
                 hll=None, ar_index=None, ar_name=None, output_file=None,
                 **kwargs):
        """
        :param File pdb_file: PDB file.
        :param File config_file: Configuration file.
        :param File static_code_archive: Archive(s) whose functions should be
                                         considered as statically linked code.
        :param File static_code_sigfile: File(s) with signatures that match
                                         functions to be considered as
                                         statically linked code.
        :param str arch: Architecture.
        :param str format: File format.
        :param str mode: Mode.
        :param str hll: High-level language.
        :param int/str ar_index: Index of the file in the input archive to be
                                 decompiled.
        :param str ar_name: Name of the file in the input archive to be
                            decompiled.
        :param File output_file: Output file.

        All the other arguments are passed to :class:`.ToolArguments`.
        """
        super().__init__(**kwargs)
        self.pdb_file = pdb_file
        self.config_file = config_file
        self.static_code_archive = static_code_archive
        self.static_code_sigfile = static_code_sigfile
        self.arch = arch
        self.format = format
        self.mode = mode
        self.hll = hll
        self.ar_index = ar_index
        self.ar_name = ar_name
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

        # PDB file.
        if self.pdb_file is not None:
            arg_list.extend(['--pdb', self.pdb_file.path])

        # Configuration file.
        if self.config_file is not None:
            arg_list.extend(['--config', self.config_file.path])

        # Archive whose functions should be considered as statically linked code.
        if self.static_code_archive is not None:
            arg_list.extend(
                ['--static-code-archive', self.static_code_archive.path]
            )

        # File with signatures that match functions to be considered as
        # statically linked code.
        if self.static_code_sigfile is not None:
            arg_list.extend(
                ['--static-code-sigfile', self.static_code_sigfile.path]
            )

        # Mode.
        if self.mode is not None:
            arg_list.extend(['-m', self.mode])

        # High-level language.
        if self.hll is not None:
            arg_list.extend(['-l', self.hll])

        # Architecture.
        if self.arch is not None:
            arg_list.extend(['-a', self.arch])

        # File format.
        if self.format is not None:
            arg_list.extend(['-f', self.format])

        # Index of a file in the input archive.
        if self.ar_index is not None:
            arg_list.extend(['--ar-index', str(self.ar_index)])

        # Name of a file in the input archive.
        if self.ar_name is not None:
            arg_list.extend(['--ar-name', self.ar_name])

        # Additional arguments.
        arg_list.extend(self.args_as_list)

        # Output file.
        if self.output_file is not None:
            arg_list.extend(['-o', self.output_file.path])

        return arg_list

    @property
    @overrides(ToolArguments)
    def without_paths_and_output_files(self):
        args = self.clone()
        args._remove_paths_from_files_attr('input_files')
        args._remove_path_from_file_attr('pdb_file')
        args._remove_path_from_file_attr('config_file')
        args._remove_path_from_file_attr('static_code_archive')
        args._remove_path_from_file_attr('static_code_sigfile')
        args.output_file = None
        return args

    @overrides(ToolArguments)
    def with_rebased_files(self, inputs_dir, outputs_dir):
        args = self.clone()
        args._rebase_files_attr('input_files', inputs_dir)
        args._rebase_file_attr('pdb_file', inputs_dir)
        args._rebase_file_attr('config_file', inputs_dir)
        args._rebase_file_attr('static_code_archive', inputs_dir)
        args._rebase_file_attr('static_code_sigfile', inputs_dir)
        args._rebase_file_attr('output_file', outputs_dir)
        return args

    @classmethod
    @overrides(ToolArguments)
    def from_test_settings(cls, test_settings):
        args = DecompilerArguments()

        # Input file.
        cls._verify_attr_is_set(test_settings, 'input')
        cls._verify_attr_is_not_list(test_settings, 'input')
        args._set_files_attr_if_not_none(test_settings, 'input')

        # PDB file.
        cls._verify_attr_is_not_list(test_settings, 'pdb')
        args._set_file_attr_if_not_none(test_settings, 'pdb')

        # Configuration file.
        cls._verify_attr_is_not_list(test_settings, 'config')
        args._set_file_attr_if_not_none(test_settings, 'config')

        # Archive whose functions should be considered as statically linked code.
        # We cannot use args._set_file_attr_if_not_none() because we want to
        # omit the '_file' suffix of the created attribute.
        cls._verify_attr_is_not_list(test_settings, 'static_code_archive')
        if test_settings.static_code_archive is not None:
            args.static_code_archive = StandaloneFile(
                test_settings.static_code_archive
            )

        # File with signatures that match functions to be considered as
        # statically linked code.
        # We cannot use args._set_file_attr_if_not_none() because we want to
        # omit the '_file' suffix of the created attribute.
        cls._verify_attr_is_not_list(test_settings, 'static_code_sigfile')
        if test_settings.static_code_sigfile is not None:
            args.static_code_sigfile = StandaloneFile(
                test_settings.static_code_sigfile
            )

        # Architecture.
        cls._verify_attr_is_not_list(test_settings, 'arch')
        args._set_attr_if_not_none(test_settings, 'arch')

        # File format.
        cls._verify_attr_is_not_list(test_settings, 'format')
        args._set_attr_if_not_none(test_settings, 'format')

        # Mode.
        cls._verify_attr_is_not_list(test_settings, 'mode')
        args._set_attr_if_not_none(test_settings, 'mode')

        # High-level language.
        cls._verify_attr_is_not_list(test_settings, 'hll')
        args._set_attr_if_not_none(test_settings, 'hll')

        # Index of a file in the input archive.
        cls._verify_attr_is_not_list(test_settings, 'ar_index')
        args._set_attr_if_not_none(test_settings, 'ar_index')

        # Name of a file in the input archive.
        cls._verify_attr_is_not_list(test_settings, 'ar_name')
        args._set_attr_if_not_none(test_settings, 'ar_name')

        # Additional arguments.
        cls._verify_attr_is_not_list(test_settings, 'args')
        args._set_attr_if_not_none(test_settings, 'args')

        # Output file.
        args.output_file = StandaloneFile(
            args._get_output_file_name_from_input_file_name())

        return args

    def _get_output_file_name_from_input_file_name(self):
        """Returns the name of the output file from the input file.
        """
        input_file_name = self.input_file.name
        if input_file_name.endswith('.exe'):
            return input_file_name[:-4] + '.c'
        elif input_file_name.endswith('.ll'):
            return input_file_name[:-3] + '.c'
        else:
            return input_file_name + '.c'
