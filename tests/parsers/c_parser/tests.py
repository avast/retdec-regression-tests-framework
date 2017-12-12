"""
    Tests for the :mod:`regression_tests.parsers.c_parser` package.
"""

import unittest
from unittest import mock

from regression_tests.parsers.c_parser import parse
from regression_tests.parsers.c_parser import parse_file


class ParseTests(unittest.TestCase):
    """Tests for `parse()`."""

    def test_parsed_object_represents_original_source_code(self):
        CODE = 'int main() {}'
        parsed_c_code = parse(CODE)
        self.assertEqual(parsed_c_code, CODE)

    def test_parsed_objects_code_returns_original_source_code(self):
        CODE = 'int main() {}'
        parsed_c_code = parse(CODE)
        self.assertEqual(parsed_c_code.code, CODE)


class ParseFileTests(unittest.TestCase):
    """Tests for `parse_file()`."""

    def test_reads_data_from_file_and_correctly_parses_them(self):
        open_mock = mock.mock_open(read_data='int g;')
        with mock.patch('builtins.open', open_mock, create=True):
            module = parse_file('/path/to/file.c', encoding='latin2')
            open_mock.assert_called_once_with(
                '/path/to/file.c', 'r', encoding='latin2'
            )
            self.assertTrue(module.has_global_var('g'))
