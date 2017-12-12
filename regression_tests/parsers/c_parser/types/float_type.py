"""
    A ``float`` type.
"""

from regression_tests.parsers.c_parser.types.floating_point_type import FloatingPointType


class FloatType(FloatingPointType):
    """A ``float`` type."""

    def is_float(self, size=None):
        """Returns ``True`` if `size` matches.

        See :func:`~regression_tests.parsers.c_parser.type.Type.is_float()`
        for more details.
        """
        return self._is_of_size_if_not_none(size)

    def __eq__(self, other):
        return isinstance(other, FloatType)

    def __hash__(self):
        return hash('float')

    def __repr__(self):
        return '<{}>'.format(self.__class__.__name__)

    def __str__(self):
        return 'float'
