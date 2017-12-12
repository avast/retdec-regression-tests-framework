"""
    A ``double`` type.
"""

from regression_tests.parsers.c_parser.types.floating_point_type import FloatingPointType


class DoubleType(FloatingPointType):
    """A ``double`` type."""

    def is_double(self, size=None):
        """Returns ``True`` if `size` matches.

        See :func:`~regression_tests.parsers.c_parser.type.Type.is_double()`
        for more details.
        """
        return self._is_of_size_if_not_none(size)

    def __eq__(self, other):
        return isinstance(other, DoubleType)

    def __hash__(self):
        return hash('double')

    def __repr__(self):
        return '<{}>'.format(self.__class__.__name__)

    def __str__(self):
        return 'double'
