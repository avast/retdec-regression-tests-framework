"""
    A representation of a union.
"""

from regression_tests.parsers.c_parser.types.composite_type import CompositeType


class UnionType(CompositeType):
    """A representation of a union."""

    @property
    def _type_name(self):
        return 'union'

    def is_union(self):
        """Returns ``True``."""
        return True
