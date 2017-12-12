"""
    A base class for all integral types (``int``, ``long int``, etc.).
"""

from regression_tests.parsers.c_parser.types.numeric_type import NumericType


class IntegralType(NumericType):
    """A base class for all integral types (``int``, ``long int``, etc.)."""

    def is_integral(self, size=None):
        """Returns ``True`` if `size` matches.

        See :func:`~regression_tests.parsers.c_parser.type.Type.is_integral()`
        for more details.
        """
        return self._is_of_size_if_not_none(size)
