"""
    Settings for decompilations.
"""

from regression_tests.tools.decompilation_arguments import DecompilationArguments
from regression_tests.tools.decompilation_runner import DecompilationRunner
from regression_tests.tools.decompilation_test import DecompilationTest
from regression_tests.tools.tool_test_settings import ToolTestSettings
from regression_tests.utils import overrides
from regression_tests.utils.list import as_list


class DecompilationTestSettings(ToolTestSettings):
    """Settings for decompilation tests."""

    #: Name of the tool.
    TOOL = 'decompiler'

    def __init__(self, *, pdb=None, config=None, static_code_archive=None,
                 static_code_sigfile=None, arch=None, format=None, mode=None,
                 hll=None, ar_index=None, ar_name=None, **kwargs):
        """
        Each parameter can be either a single item or a list of items.

        :param str/list pdb: PDB file(s).
        :param str/list config: Configuration file(s).
        :param str/list static_code_archive: Archive(s) whose functions should
                                             be considered as statically linked
                                             code.
        :param str/list static_code_sigfile: File(s) with signatures that match
                                             functions to be considered as
                                             statically linked code.
        :param str/list arch: Architecture(s).
        :param str/list format: File format(s).
        :param str/list mode: Mode(s).
        :param str/list hll: High-level language(s).
        :param int/str/list ar_index: Index(es) of the file(s) in the input
                                      archive to be decompiled.
        :param str/list ar_name: Name(s) of the file(s) in the input archive to
                                 be decompiled.

        See the description of :class:`.ToolTestSettings` for additional
        parameters.

        If any of the lists contains duplicates, they are merged.

        See the description of :class:`.ToolTestSettings` for additional
        attributes.
        """
        kwargs['tool'] = self.TOOL
        ToolTestSettings.__init__(self, **kwargs)

        self.pdb = self._merge_duplicates(pdb)
        self.static_code_archive = self._merge_duplicates(static_code_archive)
        self.static_code_sigfile = self._merge_duplicates(static_code_sigfile)
        self.config = self._merge_duplicates(config)
        self.arch = self._merge_duplicates(arch)
        self.format = self._merge_duplicates(format)
        self.mode = self._merge_duplicates(mode)
        self.hll = self._merge_duplicates(hll)
        self.ar_index = self._merge_duplicates(ar_index)
        self.ar_name = self._merge_duplicates(ar_name)

    @property
    def pdb_as_list(self):
        """PDB file(s) as a list.

        When the PDB file is not set, the empty list is returned. When there is
        only a single PDB file, a singleton list is returned. When there are
        multiple files, the list is returned directly.
        """
        return as_list(self.pdb)

    def has_multiple_pdbs(self):
        """Checks if the settings contains multiple PDB files.

        :returns: ``True`` if the settings contains multiple PDB files,
                  ``False`` otherwise.
        """
        return self._has_multiple_values_for_attr('pdb')

    @property
    def static_code_archive_as_list(self):
        """Archive file(s) as a list.

        When the archive file is not set, the empty list is returned. When
        there is only a single archive file, a singleton list is returned. When
        there are multiple files, the list is returned directly.
        """
        return as_list(self.static_code_archive)

    def has_multiple_static_code_archives(self):
        """Checks if the settings contains multiple archive files.

        :returns: ``True`` if the settings contains multiple archive files,
                  ``False`` otherwise.
        """
        return self._has_multiple_values_for_attr('static_code_archive')

    @property
    def static_code_sigfile_as_list(self):
        """Signature file(s) as a list.

        When the signature file is not set, the empty list is returned. When
        there is only a single signature file, a singleton list is returned.
        When there are multiple files, the list is returned directly.
        """
        return as_list(self.static_code_sigfile)

    def has_multiple_static_code_sigfiles(self):
        """Checks if the settings contains multiple signature files.

        :returns: ``True`` if the settings contains multiple signature files,
                  ``False`` otherwise.
        """
        return self._has_multiple_values_for_attr('static_code_sigfile')

    @property
    def config_as_list(self):
        """Configuration file(s) as a list.

        When the configuration file is not set, the empty list is returned.
        When there is only a single configuration file, a singleton list is
        returned. When there are multiple files, the list is returned directly.
        """
        return as_list(self.config)

    def has_multiple_configs(self):
        """Checks if the settings contains multiple configuration files.

        :returns: ``True`` if the settings contains multiple configuration
                  files, ``False`` otherwise.
        """
        return self._has_multiple_values_for_attr('config')

    @property
    def arch_as_list(self):
        """Architecture(s) as a list.

        When the architecture is not set, the empty list is returned. When
        there is only a single architecture, a singleton list is returned. When
        the architecture is a list, it is returned directly.
        """
        return as_list(self.arch)

    def has_multiple_archs(self):
        """Checks if the settings contains multiple architectures.

        :returns: ``True`` if the settings contains multiple architectures,
                  ``False`` otherwise.
        """
        return self._has_multiple_values_for_attr('arch')

    @property
    def format_as_list(self):
        """File format(s) as a list.

        When the file format is not set, the empty list is returned. When there
        is only a single file format, a singleton list is returned. When the
        format is a list, it is returned directly.
        """
        return as_list(self.format)

    def has_multiple_formats(self):
        """Checks if the settings contains multiple formats.

        :returns: ``True`` if the settings contains multiple formats, ``False``
                  otherwise.
        """
        return self._has_multiple_values_for_attr('format')

    @property
    def mode_or_default(self):
        """Mode(s) if set, the default mode otherwise."""
        return self.mode if self.mode else 'bin'

    @property
    def mode_as_list(self):
        """Mode(s) as a list.

        When the mode is not set, the empty list is returned. When there is
        only a single mode, a singleton list is returned. When the mode is a
        list, it is returned directly.
        """
        return as_list(self.mode)

    def has_multiple_modes(self):
        """Checks if the settings contains multiple modes.

        :returns: ``True`` if the settings contains multiple modes, ``False``
                  otherwise.
        """
        return self._has_multiple_values_for_attr('mode')

    @property
    def hll_as_list(self):
        """High-level language(s) as a list.

        When the high-level language (HLL) is not set, the empty list is
        returned. When there is only a single HLL, a singleton list is
        returned. When the HLL is a list, it is returned directly.
        """
        return as_list(self.hll)

    def has_multiple_hlls(self):
        """Checks if the settings contains multiple high-level languages.

        :returns: ``True`` if the settings contains multiple high-level
                  languages, ``False`` otherwise.
        """
        return self._has_multiple_values_for_attr('hll')

    @property
    def ar_index_as_list(self):
        """Index(es) of file(s) in the input archive as a list.

        When the index is not set, the empty list is returned. When there is
        only a single index, a singleton list is returned. When the index is a
        list, it is returned directly.
        """
        return as_list(self.ar_index)

    def has_multiple_ar_indexes(self):
        """Checks if the settings contains multiple indexes of files in the
        input archive.

        :returns: ``True`` if the settings contains multiple indexes, ``False``
                  otherwise.
        """
        return self._has_multiple_values_for_attr('ar_index')

    @property
    def ar_name_as_list(self):
        """Name(s) of file(s) in the input archive as a list.

        When the name is not set, the empty list is returned. When there is
        only a single name, a singleton list is returned. When the name is a
        list, it is returned directly.
        """
        return as_list(self.ar_name)

    def has_multiple_ar_names(self):
        """Checks if the settings contains multiple names of files in the input
        archive.

        :returns: ``True`` if the settings contains multiple names, ``False``
                  otherwise.
        """
        return self._has_multiple_values_for_attr('ar_name')

    @property
    @overrides(ToolTestSettings)
    def tool_arguments_class(self):
        return DecompilationArguments

    @property
    @overrides(ToolTestSettings)
    def tool_runner_class(self):
        return DecompilationRunner

    @property
    @overrides(ToolTestSettings)
    def tool_test_class(self):
        return DecompilationTest

    @classmethod
    @overrides(ToolTestSettings)
    def should_be_created_from(cls, **kwargs):
        # We want to use these settings by default, i.e. when no explicit tool
        # settings are requested.
        if 'tool' not in kwargs:
            return True

        return kwargs['tool'] == cls.TOOL
