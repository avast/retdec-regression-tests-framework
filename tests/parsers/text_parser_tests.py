"""
    Tests for the :module`regression_tests.parsers.text_parser` module.
"""

import unittest

from regression_tests.parsers.text_parser import Text
from regression_tests.parsers.text_parser import parse


class ParseTests(unittest.TestCase):
    """Tests for `parse()`."""

    def test_returns_text_from_string(self):
        text = parse('text')
        self.assertIsInstance(text, Text)

    def test_returned_object_is_like_string(self):
        text = parse('text')
        self.assertIsInstance(text, str)


class TextTests(unittest.TestCase):
    """Tests for `Text`."""

    def test_contains_returns_true_if_regexp_is_found(self):
        text = Text("""
            // ...
            void func() {}
        """)
        self.assertTrue(text.contains(r'void .*() {}'))

    def test_contains_returns_false_if_regexp_is_not_found(self):
        text = Text('')
        self.assertFalse(text.contains(r'test'))
