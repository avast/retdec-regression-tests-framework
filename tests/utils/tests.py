"""
    Tests for the :mod:`regression_tests.utils` package.
"""

import unittest
from unittest import mock

from regression_tests.utils import copy_class
from regression_tests.utils import overrides
from regression_tests.utils import memoize


class MemoizeTests(unittest.TestCase):
    """Tests for `memoize()`."""

    def test_memoizes_results(self):
        func = mock.Mock(return_value=1)
        memoized_func = memoize(func)

        self.assertEqual(memoized_func(1), 1)
        self.assertEqual(memoized_func(1), 1)
        func.assert_called_once_with(1)


class OverridesTests(unittest.TestCase):
    """Tests for `overrides()`."""

    def test_passes_when_method_exists_in_interface_class(self):
        class BaseClass:
            def foo(self):
                pass

        class Subclass(BaseClass):
            @overrides(BaseClass)
            def foo(self):
                pass

    def test_raises_assertion_error_when_method_does_not_exist_in_interface_class(self):
        with self.assertRaises(AssertionError):
            class BaseClass:
                pass

            class Subclass(BaseClass):
                @overrides(BaseClass)
                def foo(self):
                    pass

    def test_adds_custom_docstring_when_no_previous_doc_in_method(self):
        class BaseClass:
            def foo(self):
                pass

        class Subclass(BaseClass):
            @overrides(BaseClass)
            def foo(self):
                pass

        self.assertEqual(Subclass.foo.__doc__, 'Overrides :func:`BaseClass.foo()`.')

    def test_adds_modified_docstring_from_method_in_interface_class_if_there_is_one(self):
        class BaseClass:
            def foo(self):
                """Original description."""
                pass

        class Subclass(BaseClass):
            @overrides(BaseClass)
            def foo(self):
                pass

        self.assertEqual(
            Subclass.foo.__doc__,
            'Original description.\n' +
            '\n' +
            'Overrides :func:`BaseClass.foo()`.'
        )

    def test_original_docstring_with_indentation_is_cleaned_before_it_is_used(self):
        class BaseClass:
            def foo(self):
                """Original description
                that spans
                over multiple lines.
                """
                pass

        class Subclass(BaseClass):
            @overrides(BaseClass)
            def foo(self):
                pass

        self.assertEqual(
            Subclass.foo.__doc__,
            'Original description\nthat spans\nover multiple lines.\n' +
            '\n' +
            'Overrides :func:`BaseClass.foo()`.'
        )

    def test_does_not_add_docstring_when_method_has_docstring(self):
        class BaseClass:
            def foo(self):
                pass

        class Subclass(BaseClass):
            @overrides(BaseClass)
            def foo(self):
                """Custom description."""
                pass

        self.assertEqual(Subclass.foo.__doc__, 'Custom description.')


class CopyClassTests(unittest.TestCase):
    """Tests for `copy_class()`."""

    def test_returned_class_is_a_copy(self):
        class A:
            a = 1

        A_copy = copy_class(A)

        self.assertEqual(A.a, A_copy.a)

    def test_returned_class_has_different_id(self):
        class A:
            pass

        A_copy = copy_class(A)

        self.assertNotEqual(id(A), id(A_copy))
