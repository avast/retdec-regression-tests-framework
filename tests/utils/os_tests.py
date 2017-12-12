"""
    Tests for the :module`regression_tests.utils.os` module.
"""

import os
import unittest
from unittest import mock

from regression_tests.utils.os import chdir
from regression_tests.utils.os import make_dir_name_valid
from regression_tests.utils.os import make_file_name_valid
from tests.filesystem.directory_tests import ROOT_DIR


@mock.patch('os.chdir')
class ChdirTests(unittest.TestCase):
    """Tests for `chdir()`."""
    # From http://petrzemek.net/blog/2014/06/21/unit-testing-with-unittest-mock-patch/.

    def setUp(self):
        self.orig_cwd = os.getcwd()
        self.dst_dir = 'test'

    def test_os_chdir_is_called_with_dst_dir_in_entry(self, mock_chdir):
        with chdir(self.dst_dir):
            mock_chdir.assert_called_once_with(self.dst_dir)

    def test_os_chdir_is_called_with_orig_cwd_in_exit(self, mock_chdir):
        with chdir(self.dst_dir):
            mock_chdir.reset_mock()
        mock_chdir.assert_called_once_with(self.orig_cwd)

    def test_os_chdir_is_called_with_orig_cwd_in_exit_even_if_exception_occurs(
            self, mock_chdir):
        try:
            with chdir(self.dst_dir):
                mock_chdir.reset_mock()
                raise RuntimeError
        except RuntimeError:
            mock_chdir.assert_called_once_with(self.orig_cwd)


class MakeFileNameValidTests(unittest.TestCase):
    """Tests for `make_file_name_valid()`."""

    def scenario_returns_correct_file_name(self, name, ref_name):
        self.assertEqual(make_file_name_valid(name), ref_name)

    def test_returns_underscore_for_empty_file_name(self):
        self.scenario_returns_correct_file_name('', '_')

    def test_returns_unchanged_name_if_all_characters_are_valid(self):
        self.scenario_returns_correct_file_name('xxx', 'xxx')

    def test_returns_valid_name_if_some_characters_are_invalid(self):
        self.scenario_returns_correct_file_name('x/x', 'xx')
        self.scenario_returns_correct_file_name('x\x00x', 'xx')
        self.scenario_returns_correct_file_name('x\x01x', 'xx')
        self.scenario_returns_correct_file_name('x\x0ex', 'xx')
        self.scenario_returns_correct_file_name('x\x0fx', 'xx')

    def test_correctly_shortens_file_name_if_it_is_too_long(self):
        self.scenario_returns_correct_file_name(
            256 * 'a',
            # 242 + len(' - ...') = 255
            242 * 'a' + ' - 2960995929'
        )

    def test_does_not_shorten_file_name_when_max_length_is_none(self):
        name = 1000 * 'a'
        self.assertEqual(make_file_name_valid(name, max_length=None), name)

    def test_uses_minimal_usable_length_when_max_length_is_too_low(self):
        self.assertEqual(
            make_file_name_valid(1000 * 'a', max_length=0),
            # The value below is the CRC32 hash of the name.
            '2587417091'
        )


class MakeDirNameValidTests(unittest.TestCase):
    """Tests for `make_dir_name_valid()`."""

    @mock.patch('regression_tests.utils.os.on_windows', return_value=False)
    def test_returns_same_result_as_make_file_name_valid_on_linux(self, *args):
        NAME = 'x/x\x00x'
        self.assertEqual(
            make_dir_name_valid(NAME),
            make_file_name_valid(NAME)
        )

    @mock.patch('regression_tests.utils.os.on_windows', return_value=True)
    def test_returns_same_result_as_make_file_name_valid_with_custom_limit_on_windows(
            self, *args):
        NAME = 1000 * 'a'
        PATH_TO_DIR = os.path.join(ROOT_DIR, 'some_dir')
        self.assertEqual(
            make_dir_name_valid(
                NAME,
                path_to_dir=PATH_TO_DIR,
                max_nested_file_length=100
            ),
            make_file_name_valid(
                NAME,
                # See the implementation of make_dir_name_valid() for the
                # explanation of the following computation:
                max_length=(260 - len(PATH_TO_DIR) - len(os.path.sep) - 100)
            )
        )
