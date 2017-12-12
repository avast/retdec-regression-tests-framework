"""
    A representation of a structure.
"""

from regression_tests.parsers.c_parser.types.composite_type import CompositeType


class StructType(CompositeType):
    """A representation of a structure."""

    @property
    def _type_name(self):
        return 'struct'

    def is_struct(self):
        """Returns ``True``."""
        return True
