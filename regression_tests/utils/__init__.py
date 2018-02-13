"""
    Utilities for regression tests.
"""

import functools
import inspect


def memoize(func):
    """A decorator to memoize the given function.

    It stores the results of function calls and returns the stored result when
    the same inputs occur again. The decorator also works on methods or
    properties.
    """
    return functools.lru_cache(maxsize=None)(func)


def overrides(interface_class):
    """A decorator to document and validate an overridden method in a subclass.

    Usage:

    .. code-block:: python

        class BaseClass:
            def foo(self):
                ...

        class Subclass(BaseClass):
            @overrides(BaseClass)
            def foo(self):
                ...

    When there is no such method in `interface_class`, it raises an assertion
    error.
    """
    # Based on http://stackoverflow.com/a/8313042.
    def overrider(method):
        assert method.__name__ in dir(interface_class)

        # When there is no docstring, use a custom one.
        if not method.__doc__:
            # If the method in the interface class has a docstring, use it as a
            # base of the custom docstring.
            original_doc = getattr(interface_class, method.__name__).__doc__
            if original_doc:
                # We need to clean the docstring (indentation between """ and """)
                # because it confuses Sphinx.
                original_doc = inspect.cleandoc(original_doc)
            base_doc = original_doc + '\n\n' if original_doc else ''
            method.__doc__ = base_doc + 'Overrides :func:`{}.{}()`.'.format(
                interface_class.__name__,
                method.__name__
            )

        return method
    return overrider


def copy_class(cls):
    """Returns a copy of the given test class."""
    # We cannot use the standard copy module because it does not copy modules
    # or classes. Therefore, we use the approach from
    # http://stackoverflow.com/a/13379957.
    return type(
        cls.__name__,
        cls.__bases__,
        dict(cls.__dict__)
    )
