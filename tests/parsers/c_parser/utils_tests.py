"""
    Tests for the :module`regression_tests.parsers.c_parser.utils` module.
"""

import unittest

from regression_tests.parsers.c_parser.utils import IdentifiedObjectList
from regression_tests.parsers.c_parser.utils import first_token
from regression_tests.parsers.c_parser.utils import get_name
from regression_tests.parsers.c_parser.utils import has_token
from regression_tests.parsers.c_parser.utils import has_token_in_position
from regression_tests.parsers.c_parser.utils import has_tokens
from regression_tests.parsers.c_parser.utils import nth_item
from regression_tests.parsers.c_parser.utils import remove_whitespace
from regression_tests.parsers.c_parser.utils import string_from_tokens
from regression_tests.parsers.c_parser.utils import underline
from tests.parsers.c_parser import WithModuleTests


class IdentifiedObjectListTests(unittest.TestCase):
    """Tests for `IdentifiedObjectList`."""

    def setUp(self):
        self.items = IdentifiedObjectList([])

    def test_property_name_is_set_correctly(self):
        self.assertEqual(self.items.property_name, 'identification')

    def test_modify_key_works_as_expected(self):
        self.assertEqual(IdentifiedObjectList.modify_key(self, 'a b   c'), 'abc')


class HasTokensTests(WithModuleTests):
    """Tests for `has_tokens()`."""

    def test_returns_false_when_no_tokens(self):
        class FakeNode:
            def get_tokens(self):
                return []
        fake_node = FakeNode()
        self.assertFalse(has_tokens(fake_node))

    def test_returns_true_when_node_has_tokens(self):
        expr_node = self.get_expr('1 + 2', 'int')._node
        self.assertTrue(has_tokens(expr_node))


class HasTokenTests(WithModuleTests):
    """Tests for `has_token()`."""

    def test_returns_false_when_token_not_present(self):
        expr_node = self.get_expr('1 + 2', 'int')._node
        self.assertFalse(has_token(expr_node, '*'))

    def test_returns_true_when_token_present(self):
        expr_node = self.get_expr('1 + 2', 'int')._node
        self.assertTrue(has_token(expr_node, '+'))


class HasTokenInPositionTests(WithModuleTests):
    """Tests for `has_token_in_position()`."""

    def test_returns_false_when_token_token_not_in_position(self):
        expr_node = self.get_expr('1 + 2', 'int')._node
        self.assertFalse(has_token_in_position(expr_node, '+', 0))

    def test_returns_true_when_token_in_position(self):
        expr_node = self.get_expr('1 + 2', 'int')._node
        self.assertTrue(has_token_in_position(expr_node, '+', 1))


class StringFromTokensTests(WithModuleTests):
    """Tests for `string_from_tokens()`."""

    def test_returns_correct_value(self):
        expr_node = self.get_expr('1 + 2', 'int')._node
        self.assertEqual(string_from_tokens(expr_node), '1+2')


class RemoveWhitespaceTests(unittest.TestCase):
    """Tests for `remove_whitespace()`."""

    def test_removes_whitespace(self):
        self.assertEqual(remove_whitespace(' a\t\nbc'), 'abc')

    def test_lefts_whitespace_in_string_literals(self):
        self.assertEqual(remove_whitespace('if ("ab c d" )'), 'if("ab c d")')

    def test_deals_with_multiple_string_literals(self):
        self.assertEqual(
            remove_whitespace('"ab c d", "x\ty\nz "  \n '),
            '"ab c d","x\ty\nz "'
        )


class FirstTokenTests(WithModuleTests):
    """Tests for `first_token()`."""

    def test_returns_first_token(self):
        expr_node = self.get_expr('1 + 2', 'int')._node
        self.assertEqual(first_token(expr_node).spelling, '1')


class GetNameTests(unittest.TestCase):
    """Tests for `get_name()`."""

    def test_returns_correct_name_when_called_with_string(self):
        self.assertEqual(get_name('abc'), 'abc')

    def test_returns_correct_name_when_called_with_object_with_property_name(self):
        class FakeObject:
            @property
            def name(self):
                return 'fake name'
        fake_obj = FakeObject()
        self.assertEqual(get_name(fake_obj), 'fake name')


class UnderlineTests(unittest.TestCase):
    """Tests for `underline()`."""

    def test_underlines(self):
        self.assertEqual(underline('abc'), 'abc\n---')


class NthItemTests(unittest.TestCase):
    """Tests for `nth_item()`."""

    def test_returns_nth_item(self):
        def test_generator():
            i = 0
            while True:
                yield i
                i += 1
        generator = test_generator()
        self.assertEqual(nth_item(3, generator), 3)
