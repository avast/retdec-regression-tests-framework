"""
    Abstraction of directories.
"""

import os
import shutil

from regression_tests.filesystem.file import CFile
from regression_tests.filesystem.file import ConfigFile
from regression_tests.filesystem.file import TextFile
from regression_tests.filesystem.file import YaraFile


class Directory:
    """An abstraction of a directory."""

    def __init__(self, path):
        """
        If `path` is not an absolute path, it is converted into an absolute
        path from the current working directory.
        """
        self._path = os.path.abspath(path)

    @property
    def path(self):
        """Path to the directory."""
        return self._path

    @property
    def name(self):
        """Name of the directory."""
        return os.path.basename(self.path)

    def exists(self):
        """Checks whether the directory exists.

        :returns: ``True`` if the directory exists, ``False`` otherwise.
        """
        return os.path.isdir(self.path)

    def get_dir(self, dir):
        """Returns the given directory.

        :param str dir: Path to a directory.

        If the path to the directory is relative, it is considered to be
        relative to the path of the current directory.
        """
        return self.__class__(self._path_to(dir))

    def dir_exists(self, dir):
        """Checks whether the given directory exists.

        :param str dir: Path to a directory.

        :returns: ``True`` if `dir` exists, ``False`` otherwise.

        If the path to the directory is relative, it is considered to be
        relative to the path of the current directory.
        """
        return os.path.isdir(self._path_to(dir))

    def create(self, erase_if_exists=False):
        """Creates the directory.

        :param bool erase_if_exists: Should the directory be erased prior to
                                     creating it if it exists?

        :returns: The created directory (:class:`.Directory`), which is always
                  equal to `self`.

        If `erase_if_exists` is ``False`` and the directory already exists, a
        directory for it is just returned.
        """
        if erase_if_exists:
            self.remove()
        os.makedirs(self.path, exist_ok=True)
        return self.get_dir(self.path)

    def remove(self):
        """Removes the directory.

        If the directory does not exist, this method does nothing.
        """
        shutil.rmtree(self.path, ignore_errors=True)

    def file_exists(self, name):
        """Checks if a file with the given name exists in the directory.

        :para str name: Name of the file.

        :returns: ``True`` if the file exists, ``False`` otherwise.
        """
        return os.path.isfile(self._path_to(name))

    def store_file(self, name, content, encoding='utf-8'):
        """Stores a file under the given name with the given content.

        :param str name: Name of the file.
        :param str content: Content of the file.
        :param str encoding: Encoding to be used.

        :returns: The created file of the given name (:class:`.File`).
        """
        with open(self._path_to(name), 'w', encoding=encoding) as f:
            f.write(content)
        return self._file_named(name)

    def copy_file(self, file):
        """Copies the given file to the directory.

        :param file: File to be copied.
        :type file: :class:`.File`

        :returns: The copy of the file (:class:`.File`).
        """
        copied_file = self._file_named(file.name)
        shutil.copyfile(file.path, copied_file.path)
        return copied_file

    def get_file(self, path):
        """Returns the given file.

        :param str path: Relative path of the file to the directory.

        :returns: File of the given name (:class:`.File`).

        The `path` is normalized before it is used, e.g. ``A/foo/../file.txt``
        becomes ``A/file.txt``.

        This function does not check whether the given file exists, it simply
        returns a :class:`.File` object for it.
        """
        assert not os.path.isabs(path), 'path has to be relative'
        assert not path.endswith(os.sep), 'path cannot end with a separator'

        path = os.path.normpath(path)
        *subdirs, name = path.split(os.sep)
        dir = self
        for subdir in subdirs:
            dir = dir.get_dir(subdir)
        return dir._file_named(name)

    def read_binary_file(self, name):
        """Returns the contents of the given binary file as raw bytes.

        :param str name: Name of the file.
        """
        with open(self._path_to(name), 'rb') as f:
            return f.read()

    def read_text_file(self, name, encoding='utf-8'):
        """Returns the contents of the given text file as a string.

        :param str name: Name of the file.
        :param str encoding: Encoding of the file.
        """
        # Replace malformed data by a replacement marker (such as '?') so that
        # the file can be read even if there are encoding errors.
        with open(self._path_to(name), 'r', encoding=encoding,
                  errors='replace') as f:
            return f.read()

    def walk(self):
        """Implementation of ``os.walk()``."""
        for dir_path, subdir_names, file_names in os.walk(self.path):
            dir = self.get_dir(dir_path)
            yield (
                dir,
                [dir.get_dir(subdir_name) for subdir_name in subdir_names],
                [dir.get_file(file_name) for file_name in file_names]
            )

    def __repr__(self):
        return '{}({!r})'.format(self.__class__.__name__, self.path)

    def __eq__(self, other):
        return self.path == other.path

    def __ne__(self, other):
        return not self == other

    def _path_to(self, path):
        """Returns an absolute path to the given file or directory."""
        return path if os.path.isabs(path) else os.path.join(self.path, path)

    def _file_named(self, name):
        """Returns a file with the given name."""
        if name.endswith('.c'):
            return CFile(name, self)
        elif name.endswith('.config.json'):
            return ConfigFile(name, self)
        elif name.endswith('.yara'):
            return YaraFile(name, self)

        # We assume that other files are text files by default.
        return TextFile(name, self)
