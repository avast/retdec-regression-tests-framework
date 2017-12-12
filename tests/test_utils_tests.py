"""
    Tests for the :mod:`regression_tests.test_utils` module.
"""

import os
import unittest
from unittest import mock

from regression_tests.test_utils import files_in_dir
from tests import WithPatching


class FilesInDirTests(unittest.TestCase, WithPatching):
    """Tests for `files_in_dir()`."""

    def setUp(self):
        # inspect
        self.inspect_mock = mock.MagicMock()
        self.inspect_mock.stack.return_value = [
            ...,
            [..., os.path.join('test_dir', 'test.py')]
        ]
        self.patch('regression_tests.test_utils.inspect', self.inspect_mock)

        # os.listdir()
        self.os_listdir_mock = mock.MagicMock()
        self.patch('regression_tests.test_utils.os.listdir', self.os_listdir_mock)

    def test_os_listdir_is_called_for_correct_directory(self):
        TEST_DIR = os.path.join('d1', 'd2')
        self.inspect_mock.stack.return_value = [
            ...,
            [..., os.path.join(TEST_DIR, 'test.py')]
        ]

        files_in_dir('dir')

        self.os_listdir_mock.assert_called_once_with(
            os.path.join(TEST_DIR, 'dir')
        )

    def test_returns_files_ordered_by_their_name(self):
        self.os_listdir_mock.return_value = ['b', 'c', 'a']

        files = files_in_dir('dir')

        self.assertEqual(
            files,
            [os.path.join('dir', 'a'), os.path.join('dir', 'b'), os.path.join('dir', 'c')]
        )

    def test_only_files_matching_give_regular_expression_are_returned(self):
        self.os_listdir_mock.return_value = [
            'test.py',
            'file.exe',
            'file.exe.bak'
        ]

        files = files_in_dir('dir', matching=r'.*\.exe')

        self.assertEqual(
            files,
            [os.path.join('dir', 'file.exe')]
        )

    def test_files_from_excluding_are_not_included(self):
        self.os_listdir_mock.return_value = [
            'test.py',
            'file.exe',
            'file.exe.bak'
        ]

        files = files_in_dir('dir', excluding=['test.py', 'file.exe.bak'])

        self.assertEqual(
            files,
            [os.path.join('dir', 'file.exe')]
        )

    def test_files_matching_excluding_are_not_included(self):
        self.os_listdir_mock.return_value = [
            'test.py',
            'file.exe',
            'other_test.py'
        ]

        files = files_in_dir('dir', excluding=r'.*\.py')

        self.assertEqual(
            files,
            [os.path.join('dir', 'file.exe')]
        )


class BaseRunAndSkipTests(unittest.TestCase):
    """A base class that provides assertions to check whether a test method is
    run or skipped.
    """

    def assert_method_is_run(self, test_cls):
        test = test_cls()
        # unittest.skipTest() raises unittest.SkipTest, so we check that this
        # exception is not raised upon calling the method.
        try:
            test.method()
        except unittest.SkipTest:
            self.fail('should have run')

    def assert_method_is_skipped(self, test_cls, due_to):
        test = test_cls()
        # unittest.skipTest() raises unittest.SkipTest, so we check that this
        # exception is raised upon calling the method.
        with self.assertRaisesRegex(
                unittest.SkipTest,
                r'.*{}.*'.format(due_to),
                msg='should have skipped'):
            test.method()
