"""
    Abstraction of files.
"""

import os

from regression_tests.parsers.c_parser import parse as parse_c
from regression_tests.parsers.config_parser import parse as parse_config
from regression_tests.parsers.text_parser import parse as parse_text
from regression_tests.parsers.yara_parser import parse as parse_yara
from regression_tests.utils import memoize


class File:
    """An abstraction of a file."""

    def __init__(self, name, dir):
        """
        :param str name: Name of the file.
        :param Directory dir: Directory in which the file is located.
        """
        self._name = name
        self._dir = dir

    @property
    def name(self):
        """Name of the file (`str`)."""
        return self._name

    @property
    def dir(self):
        """Directory in which the file is located (:class:`.Directory`)."""
        return self._dir

    @property
    def path(self):
        """Path to the file (`str`)."""
        return os.path.join(self.dir.path, self.name)

    @property
    @memoize
    def data(self):
        """Data of the file (`bytes`)."""
        return self.dir.read_binary_file(self.name)

    def exists(self):
        """Does the file exists?"""
        return self.dir.file_exists(self.name)

    def renamed(self, new_name):
        """Returns a new file in the same directory but with a different name.
        """
        return self.__class__(new_name, self.dir)

    def __repr__(self):
        return '{}({!r}, {!r})'.format(
            self.__class__.__name__,
            self.name,
            self.dir
        )

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        return hash(self.path)


class TextFile(File):
    """An abstraction of a text file."""

    @property
    @memoize
    def text(self):
        """Text of the file (:class:`.Text`, which is a `str`-like object)."""
        return parse_text(self.dir.read_text_file(self.name))


class CFile(TextFile):
    """An abstraction of a C file."""

    @property
    @memoize
    def text(self):
        """Parsed contents of the file (:class:`.Module`, which is a `str`-like
        object).
        """
        return parse_c(super().text, self.name)


class ConfigFile(TextFile):
    """An abstraction of a configuration file used by RetDec."""

    @property
    @memoize
    def text(self):
        """Parsed contents of the file (:class:`.Config`, which is a `str`-like
        object).
        """
        return parse_config(super().text)


class YaraFile(TextFile):
    """An abstraction of a YARA file."""

    @property
    @memoize
    def text(self):
        """Parsed contents of the file (:class:`.Yara`, which is a `str`-like
        object).
        """
        return parse_yara(super().text)


class StandaloneFile:
    """An abstraction of a file with a relative path.

    If you want to represent a file within a specific directory, use
    :class:`.File` instead. This class is meant to be used for files like
    ``test.c`` where the precise directory is indeterminate.
    """

    def __init__(self, path):
        """
        :param str path: Relative path to the file. Can be just a name.

        The path is normalized so that its path separator corresponds to the
        separator used on the target system.
        """
        self._path = path.replace('/', os.sep).replace('\\', os.sep)

    @property
    def name(self):
        """Name of the file (`str`)."""
        return os.path.basename(self._path)

    @property
    def path(self):
        """Path to the file (`str`)."""
        return self._path

    def __repr__(self):
        return '{}({!r})'.format(
            self.__class__.__name__,
            self.path
        )

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self == other
