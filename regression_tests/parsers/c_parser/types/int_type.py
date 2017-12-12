"""
    An ``int`` type.
"""

from regression_tests.parsers.c_parser.types.integral_type import IntegralType


class IntType(IntegralType):
    """An ``int`` type."""

    def is_int(self, size=None):
        """Returns ``True`` if `size` matches.

        See :func:`~regression_tests.parsers.c_parser.type.Type.is_int()`
        for more details.
        """
        return self._is_of_size_if_not_none(size)

    def __eq__(self, other):
        return isinstance(other, IntType)

    def __hash__(self):
        return hash('int')

    def __repr__(self):
        return '<{}>'.format(self.__class__.__name__)

    def __str__(self):
        return 'int'
