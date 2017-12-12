"""
    A ``char`` type.
"""

from regression_tests.parsers.c_parser.types.integral_type import IntegralType


class CharType(IntegralType):
    """A ``char`` type."""

    def __init__(self, type, size=8):
        """
        :param clang.cindex.Type type: Internal type.
        :param int size: Size in bits.
        """
        super().__init__(type, size)

    def is_char(self, size=None):
        """Returns ``True``."""
        return True

    def __eq__(self, other):
        return isinstance(other, CharType)

    def __hash__(self):
        return hash('char')

    def __repr__(self):
        return '<{}>'.format(self.__class__.__name__)

    def __str__(self):
        return 'char'
