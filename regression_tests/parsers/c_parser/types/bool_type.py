"""
    A ``bool`` type.
"""

from regression_tests.parsers.c_parser.types.integral_type import IntegralType


class BoolType(IntegralType):
    """A ``bool`` type."""

    def is_bool(self):
        """Returns ``True``."""
        return True

    def __eq__(self, other):
        return isinstance(other, BoolType)

    def __hash__(self):
        return hash('bool')

    def __repr__(self):
        return '<{}>'.format(self.__class__.__name__)

    def __str__(self):
        return 'bool'
