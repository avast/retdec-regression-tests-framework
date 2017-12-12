"""
    A base class for all floating-point types (``float``, ``double``, etc.).
"""

from regression_tests.parsers.c_parser.types.numeric_type import NumericType


class FloatingPointType(NumericType):
    """A base class for all floating-point types (``float``, ``double``, etc.).
    """

    def is_floating_point(self, size=None):
        """Returns ``True`` if `size` matches.

        See
        :func:`~regression_tests.parsers.c_parser.type.Type.is_floating_point()`
        for more details.
        """
        return self._is_of_size_if_not_none(size)
