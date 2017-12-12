"""
    Generic tool arguments.
"""

import copy
import re

from regression_tests.filesystem.file import StandaloneFile
from regression_tests.test_settings import InvalidTestSettingsError


class ToolArguments:
    """Generic tool arguments."""

    def __init__(self, *, input_files=(), args=None):
        """
        :param tuple input_files: A tuple of input files.
        :param str args: Whitespace-separated arguments passed directly to the tool.
        """
        assert isinstance(input_files, tuple), 'Input files has to be in a tuple'

        self.input_files = input_files
        self.args = args if args else None

    @property
    def as_list(self):
        """A list of arguments to be passed to the tool."""
        arg_list = []

        # Input files.
        for input_file in self.input_files:
            arg_list.append(input_file.path)

        # Additional arguments.
        arg_list.extend(self.args_as_list)

        return arg_list

    @property
    def as_str(self):
        """A space-separated string of arguments."""
        return ' '.join(self.as_list)

    @property
    def args_as_list(self):
        """:func:`args` as a list instead of a string.

        If there are no arguments, the returned list is empty.
        """
        if self.args is None:
            return []
        return re.split(r'\s+', self.args.strip())

    @property
    def without_paths_and_output_files(self):
        """A clone of the tool arguments without paths and output files (if
        any).
        """
        args = self.clone()
        args._remove_paths_from_files_attr('input_files')
        return args

    def with_rebased_files(self, inputs_dir, outputs_dir):
        """A clone of the tool arguments with rebased input and output files.

        :param Directory inputs_dir: Directory containing input files.
        :param Directory outputs_dir: Directory in which the output files
                                      should be placed.
        """
        args = self.clone()
        args._rebase_files_attr('input_files', inputs_dir)
        return args

    @classmethod
    def from_test_settings(cls, test_settings):
        """Creates tool arguments for a tool from the given test settings.

        :param ~regression_tests.settings.TestSettings test_settings: Test
            settings.

        :raises InvalidTestSettingsError: If `test_settings` are invalid.

        `test_settings` are supposed to contain only single settings, i.e. none of
        its attributes can be a list.
        """
        args = ToolArguments()

        # Input files.
        cls._verify_attr_is_not_list(test_settings, 'input')
        args._set_files_attr_if_not_none(test_settings, 'input')

        # Additional arguments.
        cls._verify_attr_is_not_list(test_settings, 'args')
        args._set_attr_if_not_none(test_settings, 'args')

        return args

    def clone(self):
        """Clones the arguments.

        :returns: :class:`.ToolArguments` (or its subclass) that are equal to
                  `self` but not identical.
        """
        return copy.deepcopy(self)

    def clone_but(self, **kwargs):
        """Clones the arguments but sets different values for the specified
        attributes.

        :returns: :class:`ToolArguments` (or its subclass) that are equal to
                  `self` up to the specified attributes.

        See the constructor for a list of available attributes.
        """
        clone = self.clone()
        for attr, value in kwargs.items():
            setattr(clone, attr, value)
        return clone

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        attrs = ''
        for attr_name in self.__dict__:
            attr = getattr(self, attr_name)
            if attr is not None:
                if attrs:
                    attrs += ', '
                attrs += '{}={!r}'.format(attr_name, attr)
        return '{}({})'.format(self.__class__.__name__, attrs)

    @staticmethod
    def _verify_attr_is_set(test_settings, attr_name):
        """Verifies that `test_settings.attr_name` is not ``None``."""
        attr = getattr(test_settings, attr_name)
        if attr is None:
            raise InvalidTestSettingsError(
                "'{}' is missing (you forgot to specify it)".format(attr_name)
            )

    @staticmethod
    def _verify_attr_is_tuple(test_settings, attr_name, size=None):
        """Verifies that `test_settings.attr_name` is a tuple with `size`
        elements.
        """
        attr = getattr(test_settings, attr_name)
        if not isinstance(attr, tuple):
            raise InvalidTestSettingsError(
                "'{}' has to be a tuple (you used {!r})".format(attr_name, attr)
            )
        if size is not None and len(attr) != size:
            raise InvalidTestSettingsError(
                "'{}' must have {} elements (it has {} elements)".format(
                    attr_name,
                    size,
                    len(attr)
                )
            )

    @staticmethod
    def _verify_attr_is_not_list(test_settings, attr_name):
        """Verifies that `test_settings.attr_name` is not a list."""
        attr = getattr(test_settings, attr_name)
        if isinstance(attr, list):
            raise InvalidTestSettingsError(
                "'{}' cannot be a list (you used {!r})".format(attr_name, attr)
            )

    @staticmethod
    def _verify_attr_is_not_tuple(test_settings, attr_name):
        """Verifies that `test_settings.attr_name` is not a tuple."""
        attr = getattr(test_settings, attr_name)
        if isinstance(attr, tuple):
            raise InvalidTestSettingsError(
                "'{}' cannot be a tuple (you used {!r})".format(attr_name, attr)
            )

    def _set_attr_if_not_none(self, test_settings, attr_name):
        """Sets `self.attr_name` to `test_settings.attr_name` provided that
        `test_settings.attr_name` is not ``None``.
        """
        attr = getattr(test_settings, attr_name)
        if attr is not None:
            setattr(self, attr_name, attr)

    def _set_file_attr_if_not_none(self, test_settings, attr_name):
        """Sets ``self.(attr_name + _file)`` to ``StandaloneFile(attr)``
        provided that `test_settings.attr_name` is not ``None``.
        """
        attr = getattr(test_settings, attr_name)
        if attr is not None:
            setattr(self, attr_name + '_file', StandaloneFile(attr))

    def _set_files_attr_if_not_none(self, test_settings, attr_name):
        """Sets ``self.(attr_name + _files)`` to a tuple of
        ``StandaloneFile(file)`` provided that `test_settings.attr_name` is not
        ``None``.
        """
        attr = getattr(test_settings, attr_name)
        if attr is not None:
            if not isinstance(attr, tuple):
                attr = (attr,)
            new_attr = tuple(StandaloneFile(file) for file in attr)
            setattr(self, attr_name + '_files', new_attr)

    def _remove_path_from_file_attr(self, attr_name):
        """Removes path from the given file attribute (`str`)."""
        file = getattr(self, attr_name)
        if file is not None:
            setattr(self, attr_name, StandaloneFile(file.name))

    def _remove_paths_from_files_attr(self, attr_name):
        """Removes path from the given files attribute (`str`)."""
        files = getattr(self, attr_name)
        if files is not None:
            new_attr = files.__class__(
                StandaloneFile(file.name) for file in files
            )
            setattr(self, attr_name, new_attr)

    def _rebase_file_attr(self, attr_name, dir):
        """Rebases the path of the given file attribute (`str`) to the given
        directory (`Directory).
        """
        file = getattr(self, attr_name)
        if file is not None:
            setattr(self, attr_name, dir.get_file(file.path))

    def _rebase_files_attr(self, attr_name, dir):
        """Rebases paths of files in the given attribute (`str`) to the given
        directory (`Directory).
        """
        files = getattr(self, attr_name)
        if files is not None:
            new_attr = files.__class__(
                dir.get_file(file.path) for file in files
            )
            setattr(self, attr_name, new_attr)
