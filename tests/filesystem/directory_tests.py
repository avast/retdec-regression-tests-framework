"""
    Tests for the :mod:`regression_tests.filesystem.directory` module.
"""

import os
import unittest
from unittest import mock

from regression_tests.filesystem.directory import Directory
from regression_tests.filesystem.file import CFile
from regression_tests.filesystem.file import ConfigFile
from regression_tests.filesystem.file import TextFile
from regression_tests.filesystem.file import YaraFile
from regression_tests.utils.os import on_windows


def root_directory():
    """Returns the root directory to be used in absolute paths in tests."""
    if on_windows():
        # Use e.g. 'C:\', depending on the current working directory.
        return os.path.splitdrive(os.path.abspath(os.getcwd()))[0] + '\\'

    # Linux.
    return '/'


#: Root directory to be used in absolute paths in tests.
ROOT_DIR = root_directory()


class DirectoryCreateTests(unittest.TestCase):
    """Tests for the creation of `Directory` instances."""

    def test_path_returns_same_path_when_path_is_absolute(self):
        PATH = os.path.join(ROOT_DIR, 'some', 'path')
        directory = Directory(PATH)
        self.assertEqual(directory.path, PATH)

    def test_path_returns_absolute_path_when_path_is_relative(self):
        PATH = 'dir'
        directory = Directory(PATH)
        self.assertEqual(directory.path, os.path.join(os.getcwd(), PATH))

    def test_path_cannot_be_modified_after_creation(self):
        directory = Directory(os.path.join('some', 'path'))
        with self.assertRaises(AttributeError):
            directory.path = os.path.join(ROOT_DIR, 'some', 'other', 'path')

    def test_name_returns_correct_name(self):
        directory = Directory(os.path.join('some', 'dir'))
        self.assertEqual(directory.name, 'dir')


class CreatedDirectoryTests(unittest.TestCase):
    """A base class for `Directory` tests with a created directory."""

    def setUp(self):
        self.PATH = os.path.join(ROOT_DIR, 'some', 'path')
        self.directory = Directory(self.PATH)


class DirectoryExistsTests(CreatedDirectoryTests):
    """Tests for `Directory.exists()`."""

    @mock.patch('os.path.isdir')
    def test_dir_exists_calls_isdir_with_correct_path(self, isdir_mock):
        self.directory.exists()
        isdir_mock.assert_called_once_with(self.directory.path)

    @mock.patch('os.path.isdir')
    def test_exists_returns_true_when_dir_exists(self, isdir_mock):
        isdir_mock.return_value = True
        self.assertTrue(self.directory.exists())

    @mock.patch('os.path.isdir')
    def test_exists_returns_false_when_dir_does_not_exist(self, isdir_mock):
        isdir_mock.return_value = False
        self.assertFalse(self.directory.exists())


class DirectoryGetDirTests(CreatedDirectoryTests):
    """Tests for `Directory.get_dir()`."""

    def test_returns_correct_directory_for_relative_path(self):
        DIR = os.path.join('dir', 'subdir')
        dir_directory = self.directory.get_dir(DIR)
        self.assertEqual(dir_directory.path, os.path.join(self.PATH, DIR))

    def test_returns_correct_directory_for_absolute_path(self):
        DIR = os.path.join(ROOT_DIR, 'dir', 'subdir')
        dir_directory = self.directory.get_dir(DIR)
        self.assertEqual(dir_directory.path, DIR)


class DirectoryDirExistsTests(CreatedDirectoryTests):
    """Tests for `Directory.dir_exists()`."""

    @mock.patch('os.path.isdir')
    def test_dir_exists_calls_isdir_with_correct_path_for_relative_path_to_dir(
            self, isdir_mock):
        DIR = os.path.join('dir', 'subdir')
        self.directory.dir_exists(DIR)
        isdir_mock.assert_called_once_with(os.path.join(self.PATH, DIR))

    @mock.patch('os.path.isdir')
    def test_dir_exists_calls_isdir_with_correct_path_for_absolute_path_to_dir(
            self, isdir_mock):
        DIR = os.path.join(ROOT_DIR, 'dir', 'subdir')
        self.directory.dir_exists(DIR)
        isdir_mock.assert_called_once_with(DIR)

    @mock.patch('os.path.isdir')
    def test_dir_exists_returns_true_when_dir_exists(self, isdir_mock):
        isdir_mock.return_value = True
        self.assertTrue(self.directory.dir_exists(os.path.join('dir', 'subdir')))

    @mock.patch('os.path.isdir')
    def test_dir_exists_returns_false_when_dir_does_not_exist(self, isdir_mock):
        isdir_mock.return_value = False
        self.assertFalse(self.directory.dir_exists(os.path.join('dir', 'subdir')))


class DirectoryRemoveTests(CreatedDirectoryTests):
    """Tests for `Directory.remove()`."""

    @mock.patch('shutil.rmtree')
    def test_calls_shutil_rmtree_with_correct_arguments(self, rmtree_mock):
        self.directory.remove()
        rmtree_mock.assert_called_once_with(self.directory.path, ignore_errors=True)


class DirectoryCopyFileTests(CreatedDirectoryTests):
    """Tests for `Directory.copy_file()`."""

    @mock.patch('shutil.copyfile')
    def test_calls_shutil_copyfile_with_correct_arguments_and_returns_correct_file(
            self, copyfile_mock):
        input_file = TextFile('test.txt', self.directory)

        copied_file = self.directory.copy_file(input_file)

        copyfile_mock.assert_called_once_with(
            input_file.path,
            os.path.join(self.directory.path, input_file.name)
        )
        self.assertEqual(copied_file.dir, self.directory)
        self.assertEqual(copied_file.name, input_file.name)


class DirectoryGetFileTests(CreatedDirectoryTests):
    """Tests for `Directory.get_file()`."""

    def test_returns_file_with_correct_path_when_only_file_name_is_given(self):
        self.assertEqual(
            self.directory.get_file('file.exe').path,
            os.path.join(self.PATH, 'file.exe')
        )

    def test_returns_file_with_correct_path_when_file_with_path_is_given(self):
        self.assertEqual(
            self.directory.get_file(os.path.join('dir1', 'dir2', 'file.exe')).path,
            os.path.join(self.PATH, 'dir1', 'dir2', 'file.exe')
        )

    def test_path(self):
        self.assertEqual(
            self.directory.get_file(os.path.join('dir1', 'dir2', 'file.exe')).path,
            os.path.join(self.PATH, 'dir1', 'dir2', 'file.exe')
        )

    def test_returns_CFile_for_file_ending_with_dot_c(self):
        self.assertIsInstance(self.directory.get_file('file.c'), CFile)

    def test_returns_ConfigFile_for_file_ending_with_dot_json(self):
        self.assertIsInstance(self.directory.get_file('file.config.json'), ConfigFile)

    def test_returns_YaraFile_for_file_ending_with_dot_yara(self):
        self.assertIsInstance(self.directory.get_file('file.yara'), YaraFile)

    def test_returns_TextFile_for_other_files(self):
        self.assertIsInstance(self.directory.get_file('file.txt'), TextFile)


class DirectoryReprTests(CreatedDirectoryTests):
    """Tests for `Directory.__repr__()`."""

    def test_repr_returns_executable_repr_that_creates_original_directory(self):
        dir = Directory(os.path.join(ROOT_DIR, 'tmp'))
        self.assertEqual(dir, eval(repr(dir)))
