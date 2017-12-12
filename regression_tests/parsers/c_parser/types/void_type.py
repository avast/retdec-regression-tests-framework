"""
    A ``void`` type.
"""

from regression_tests.parsers.c_parser.types.type import Type


class VoidType(Type):
    """A ``void`` type."""

    def is_void(self):
        """Returns ``True``."""
        return True

    def __eq__(self, other):
        return isinstance(other, VoidType)

    def __hash__(self):
        return hash('void')

    def __repr__(self):
        return '<{}>'.format(self.__class__.__name__)

    def __str__(self):
        return 'void'
