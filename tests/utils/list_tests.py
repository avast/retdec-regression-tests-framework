"""
    Tests for the :module`regression_tests.utils.list` module.
"""

import unittest

from regression_tests.utils.list import NamedObjectList
from regression_tests.utils.list import StrPropertyList
from regression_tests.utils.list import as_list
from regression_tests.utils.list import merge_duplicates
from regression_tests.utils.list import move_to_end
from regression_tests.utils.list import names_of
from regression_tests.utils.list import names_to_set


# The tests for NamedObjectList are based on
# http://petrzemek.net/blog/2014/10/11/indexing-python-lists-with-integer-or-object-name/

class StrPropertyObject:
    """A dummy class used in :class:`StrPropertyList` tests."""

    def __init__(self, fake_property):
        self.fake_property = fake_property

    # Makes assertion messages more useful.
    def __repr__(self):
        return self.fake_property


class StrPropertyListChild(StrPropertyList):
    """A dummy class used in :class:`StrPropertyList` tests."""

    @property
    def property_name(self):
        return 'fake_property'


class StrPropertyListTests(unittest.TestCase):
    """Tests for `StrPropertyList`."""

    def setUp(self):
        self.fake_prop_a = StrPropertyObject('a')
        self.fake_prop_b = StrPropertyObject('b')
        self.fake_prop_c = StrPropertyObject('c')
        self.fake_props = StrPropertyListChild([
            self.fake_prop_a,
            self.fake_prop_b,
            self.fake_prop_c
        ])

    # __getitem__

    def test_getitem_by_int_returns_correct_object_when_object_exists(self):
        self.assertEqual(self.fake_props[0], self.fake_prop_a)
        self.assertEqual(self.fake_props[1], self.fake_prop_b)
        self.assertEqual(self.fake_props[2], self.fake_prop_c)

    def test_getitem_by_int_raises_index_error_when_no_such_object_exist(self):
        with self.assertRaises(IndexError):
            self.fake_props[3]

    def test_getitem_by_name_returns_correct_object_when_object_exists(self):
        self.assertEqual(self.fake_props['a'], self.fake_prop_a)
        self.assertEqual(self.fake_props['b'], self.fake_prop_b)
        self.assertEqual(self.fake_props['c'], self.fake_prop_c)

    def test_getitem_by_name_raises_index_error_when_no_such_object_exist(self):
        with self.assertRaises(IndexError):
            self.fake_props['X']

    # __setitem__

    def test_setitem_by_int_returns_correct_object_when_object_exists(self):
        self.fake_props[0] = self.fake_prop_b
        self.assertEqual(self.fake_props[0], self.fake_prop_b)

    def test_setitem_by_int_raises_index_error_when_no_such_object_exist(self):
        with self.assertRaises(IndexError):
            self.fake_props[3] = self.fake_prop_b

    def test_setitem_by_name_returns_correct_object_when_object_exists(self):
        self.fake_props['a'] = self.fake_prop_b
        self.assertEqual(self.fake_props[0], self.fake_prop_b)

    def test_setitem_by_name_raises_index_error_when_no_such_object_exist(self):
        with self.assertRaises(IndexError):
            self.fake_props['X'] = self.fake_prop_b

    # __delitem__

    def test_delitem_by_int_returns_correct_object_when_object_exists(self):
        del self.fake_props[0]
        self.assertEqual(self.fake_props[0], self.fake_prop_b)

    def test_delitem_by_int_raises_index_error_when_no_such_object_exist(self):
        with self.assertRaises(IndexError):
            del self.fake_props[3]

    def test_delitem_by_name_returns_correct_object_when_object_exists(self):
        del self.fake_props['a']
        self.assertEqual(self.fake_props[0], self.fake_prop_b)

    def test_delitem_by_name_raises_index_error_when_no_such_object_exist(self):
        with self.assertRaises(IndexError):
            del self.fake_props['X']


class Variable:
    """A dummy class to be used in :class:`NamedObjectList` tests."""

    def __init__(self, name):
        self.name = name

    # Makes assertion messages more useful.
    def __repr__(self):
        return self.name


class NamedObjectListTests(unittest.TestCase):
    """Tests for `NamedObjectList`."""

    def setUp(self):
        self.vars = NamedObjectList([])

    def test_property_name_is_set_correctly(self):
        self.assertEqual(self.vars.property_name, 'name')


class MergeDuplicatesTests(unittest.TestCase):
    """Tests for `merge_duplicates()`."""

    def test_returns_empty_list_for_empty_list(self):
        self.assertEqual(merge_duplicates([]), [])

    def test_returns_same_list_when_no_duplicates(self):
        self.assertEqual(merge_duplicates([1, 2, 3]), [1, 2, 3])

    def test_correctly_merges_duplicates_while_keeping_first_occurrences(self):
        self.assertEqual(merge_duplicates([1, 2, 1, 1, 3, 2, 3]), [1, 2, 3])


class MoveToEndTests(unittest.TestCase):
    """Tests for `move_to_end()`."""

    def test_moves_item_to_end_when_it_is_in_list(self):
        list = [1, 2, 3]

        move_to_end(2, list)

        self.assertEqual(list, [1, 3, 2])

    def test_does_nothing_when_item_is_not_in_list(self):
        list = [1, 2, 3]

        move_to_end(10, list)

        self.assertEqual(list, [1, 2, 3])


class AsListTests(unittest.TestCase):
    """Tests for `as_list()`."""

    def test_for_none_empty_list_is_returned(self):
        self.assertEqual(as_list(None), [])

    def test_for_string_singleton_list_is_returned(self):
        self.assertEqual(as_list('test'), ['test'])

    def test_for_tuple_singleton_list_is_returned(self):
        self.assertEqual(as_list((1, 2)), [(1, 2)])

    def test_for_int_singleton_list_is_returned(self):
        self.assertEqual(as_list(1), [1])

    def test_for_list_same_list_is_returned(self):
        self.assertEqual(as_list(['a', 'b']), ['a', 'b'])


class NamesOfTests(unittest.TestCase):
    """Tests for `names_of()`."""

    def test_returns_empty_list_when_there_are_no_objects(self):
        self.assertEqual(names_of([]), [])

    def test_returns_correct_names_when_there_are_objects(self):
        self.assertEqual(names_of([Variable('a'), Variable('b')]), ['a', 'b'])


class NamesToSetTests(unittest.TestCase):
    """Tests for `names_to_set()`."""

    def test_returns_empty_set_when_there_are_no_names(self):
        self.assertEqual(names_to_set([]), set())

    def test_turns_names_to_set_when_names_is_list_of_names(self):
        self.assertEqual(names_to_set(['a', 'b']), {'a', 'b'})

    def test_obtains_names_from_nested_list_when_names_contains_another_list(self):
        self.assertEqual(names_to_set([['a', 'b']]), {'a', 'b'})
