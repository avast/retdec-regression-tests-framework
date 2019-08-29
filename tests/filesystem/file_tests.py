"""
    Tests for the :mod:`regression_tests.filesystem.file` module.
"""

import os
import unittest
from unittest import mock


from regression_tests.filesystem.directory import Directory
from regression_tests.filesystem.file import CFile
from regression_tests.filesystem.file import ConfigFile
from regression_tests.filesystem.file import File
from regression_tests.filesystem.file import StandaloneFile
from regression_tests.filesystem.file import TextFile
from regression_tests.filesystem.file import YaraFile
from tests.filesystem.directory_tests import ROOT_DIR


#: Path to a temporary directory to be used in tests.
TMP_DIR_PATH = os.path.join(ROOT_DIR, 'tmp')


def new_dir(path):
    """Returns a new mock for Directory with the given path."""
    dir = mock.Mock(spec_set=Directory)
    type(dir).path = mock.PropertyMock(return_value=TMP_DIR_PATH)
    return dir


class FileTests(unittest.TestCase):
    """Tests for `File`."""

    def test_name_returns_correct_value(self):
        file = File('file.txt', Directory(TMP_DIR_PATH))
        self.assertEqual(file.name, 'file.txt')

    def test_dir_returns_correct_value(self):
        file = File('file.txt', Directory(TMP_DIR_PATH))
        self.assertEqual(file.dir, Directory(TMP_DIR_PATH))

    def test_path_returns_correct_value(self):
        file = File('file.txt', Directory(TMP_DIR_PATH))
        self.assertEqual(file.path, os.path.join(ROOT_DIR, 'tmp', 'file.txt'))

    def test_name_cannot_be_modified_after_creation(self):
        file = File('file.txt', Directory(TMP_DIR_PATH))
        with self.assertRaises(AttributeError):
            file.name = 'other_file.txt'

    def test_dir_cannot_be_modified_after_creation(self):
        file = File('file.txt', Directory(TMP_DIR_PATH))
        with self.assertRaises(AttributeError):
            file.dir = Directory(os.path.join(ROOT_DIR, 'other', 'dir'))

    def test_data_calls_read_binary_file_on_its_directory_and_returns_result(self):
        dir = new_dir(TMP_DIR_PATH)
        FILE_DATA = 'contents of the file'
        dir.read_binary_file.return_value = FILE_DATA
        file = File('file.txt', dir)
        self.assertEqual(file.data, FILE_DATA)
        dir.read_binary_file.assert_called_once_with('file.txt')

    def test_data_is_memoized(self):
        dir = new_dir(TMP_DIR_PATH)
        file = File('file.txt', dir)
        # We call data() two times and check that the data were read only once.
        file.data
        file.data
        dir.read_binary_file.assert_called_once_with('file.txt')

    def test_exists_calls_file_exists_on_its_directory_and_returns_result(self):
        dir = new_dir(TMP_DIR_PATH)
        dir.file_exists.return_value = True
        file = File('file.txt', dir)
        self.assertEqual(file.exists(), dir.file_exists.return_value)
        dir.file_exists.assert_called_once_with('file.txt')

    def test_renamed_returns_file_with_new_name_and_same_dir(self):
        dir = new_dir(TMP_DIR_PATH)
        file = File('file.txt', dir)
        NEW_NAME = 'new.txt'
        renamed_file = file.renamed(NEW_NAME)
        self.assertEqual(renamed_file.name, NEW_NAME)
        self.assertEqual(renamed_file.dir, dir)

    def test_two_files_with_same_name_and_dir_are_equal(self):
        file1 = File('file.txt', Directory(TMP_DIR_PATH))
        file2 = File('file.txt', Directory(TMP_DIR_PATH))
        self.assertEqual(file1, file2)

    def test_two_files_with_different_name_are_not_equal(self):
        file1 = File('file1.txt', Directory(TMP_DIR_PATH))
        file2 = File('file2.txt', Directory(TMP_DIR_PATH))
        self.assertNotEqual(file1, file2)

    def test_two_files_with_different_dir_are_not_equal(self):
        file1 = File('file.txt', Directory(os.path.join(ROOT_DIR, 'tmp', 'dir1')))
        file2 = File('file.txt', Directory(os.path.join(ROOT_DIR, 'tmp', 'dir2')))
        self.assertNotEqual(file1, file2)

    def test_repr_returns_executable_repr_that_creates_original_file(self):
        file = File('file.txt', Directory(TMP_DIR_PATH))
        self.assertEqual(file, eval(repr(file)))

    def test_same_file_hashes_to_same_value(self):
        file1 = File('file.txt', Directory(TMP_DIR_PATH))
        file2 = File('file.txt', Directory(TMP_DIR_PATH))
        self.assertEqual(hash(file1), hash(file2))

    def test_files_with_different_names_hash_to_different_values(self):
        file1 = File('file1.txt', Directory(TMP_DIR_PATH))
        file2 = File('file2.txt', Directory(TMP_DIR_PATH))
        self.assertNotEqual(hash(file1), hash(file2))

    def test_files_with_different_directories_hash_to_different_values(self):
        file1 = File('file.txt', Directory(os.path.join(ROOT_DIR, 'tmp1')))
        file2 = File('file.txt', Directory(os.path.join(ROOT_DIR, 'tmp2')))
        self.assertNotEqual(hash(file1), hash(file2))


class TextFileTests(unittest.TestCase):
    """Tests for `TextFile`."""

    def test_text_calls_read_text_file_on_its_directory_and_returns_result(self):
        dir = new_dir(TMP_DIR_PATH)
        FILE_TEXT = 'text of the file'
        dir.read_text_file.return_value = FILE_TEXT
        file = TextFile('file.txt', dir)
        self.assertEqual(file.text, FILE_TEXT)
        dir.read_text_file.assert_called_once_with('file.txt')

    def test_text_is_memoized(self):
        dir = new_dir(TMP_DIR_PATH)
        file = TextFile('file.txt', dir)
        # We call text() two times and check that the text was read only once.
        file.text
        file.text
        dir.read_text_file.assert_called_once_with('file.txt')

    def test_renamed_returns_file_with_new_class(self):
        dir = new_dir(TMP_DIR_PATH)
        file = TextFile('file.txt', dir)
        renamed_file = file.renamed('new.txt')
        self.assertEqual(renamed_file.__class__, TextFile)


class CFileTests(unittest.TestCase):
    """Tests for `CFile`."""

    @mock.patch('regression_tests.filesystem.file.parse_c')
    def test_text_calls_parse_c_and_returns_its_result(self, parse_c_mock):
        dir = new_dir(TMP_DIR_PATH)
        FILE_CODE = 'int main() {}'
        dir.read_text_file.return_value = FILE_CODE
        file = CFile('file.c', dir)
        self.assertEqual(file.text, parse_c_mock.return_value)
        parse_c_mock.assert_called_once_with(FILE_CODE, 'file.c')

    def test_text_is_memoized(self):
        dir = new_dir(TMP_DIR_PATH)
        dir.read_text_file.return_value = 'int main() {}'
        file = CFile('file.c', dir)
        # We call text() two times and check that the text was read only once.
        file.text
        file.text
        dir.read_text_file.assert_called_once_with('file.c')


class ConfigFileTests(unittest.TestCase):
    """Tests for `ConfigFile`."""

    @mock.patch('regression_tests.filesystem.file.parse_config')
    def test_text_calls_parse_config_and_returns_its_result(self, parse_config_mock):
        dir = new_dir(TMP_DIR_PATH)
        CONFIG_TEXT = '{}'
        dir.read_text_file.return_value = CONFIG_TEXT
        file = ConfigFile('config.config.json', dir)
        self.assertEqual(file.text, parse_config_mock.return_value)
        parse_config_mock.assert_called_once_with(CONFIG_TEXT)

    def test_text_is_memoized(self):
        dir = new_dir(TMP_DIR_PATH)
        dir.read_text_file.return_value = '{}'
        file = ConfigFile('config.config.json', dir)
        # We call text() two times and check that the text was read only once.
        file.text
        file.text
        dir.read_text_file.assert_called_once_with('config.config.json')


class YaraFileTests(unittest.TestCase):
    """Tests for `YaraFile`."""

    @mock.patch('regression_tests.filesystem.file.parse_yara')
    def test_text_calls_parse_yara_and_returns_its_result(self, parse_yara_mock):
        dir = new_dir(TMP_DIR_PATH)
        YARA_TEXT = 'rule X { meta: name = "func" }'
        dir.read_text_file.return_value = YARA_TEXT
        file = YaraFile('file.yara', dir)
        self.assertEqual(file.text, parse_yara_mock.return_value)
        parse_yara_mock.assert_called_once_with(YARA_TEXT)

    def test_text_is_memoized(self):
        dir = new_dir(TMP_DIR_PATH)
        dir.read_text_file.return_value = 'rule X { meta: name = "func" }'
        file = YaraFile('file.yara', dir)
        # We call text() two times and check that the text was read only once.
        file.text
        file.text
        dir.read_text_file.assert_called_once_with('file.yara')


class StandaloneFileTests(unittest.TestCase):
    """Tests for `StandaloneFile`."""

    def test_name_returns_correct_value_when_there_is_no_directory(self):
        NAME = 'file.txt'
        file = StandaloneFile(NAME)
        self.assertEqual(file.name, NAME)

    def test_name_returns_correct_value_when_there_is_directory(self):
        file = StandaloneFile('dir/file.txt')
        self.assertEqual(file.name, 'file.txt')

    def test_path_returns_correct_value_when_there_is_no_directory(self):
        file = StandaloneFile('file.txt')
        self.assertEqual(file.path, file.name)

    def test_path_returns_correct_value_when_there_is_directory(self):
        PATH = os.path.join('dir', 'file.txt')
        file = StandaloneFile(PATH)
        self.assertEqual(file.path, PATH)

    def test_separator_in_path_is_normalized_to_match_separator_used_by_os(self):
        for file in [StandaloneFile('dir/file.txt'), StandaloneFile('dir\\file.txt')]:
            self.assertEqual(file.path, os.path.join('dir', 'file.txt'))

    def test_name_cannot_be_modified_after_creation(self):
        file = StandaloneFile('file.txt')
        with self.assertRaises(AttributeError):
            file.name = 'other_file.txt'

    def test_two_files_with_same_paths_are_equal(self):
        file1 = StandaloneFile('file.txt')
        file2 = StandaloneFile('file.txt')
        self.assertEqual(file1, file2)

    def test_two_files_with_different_paths_are_not_equal(self):
        file1 = StandaloneFile('file1.txt')
        file2 = StandaloneFile('file2.txt')
        self.assertNotEqual(file1, file2)

    def test_repr_returns_executable_repr_that_creates_original_file(self):
        file = StandaloneFile('file.txt')
        self.assertEqual(file, eval(repr(file)))
