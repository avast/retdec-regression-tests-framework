"""
    A pointer type.
"""

from regression_tests.parsers.c_parser.types.type import Type


class PointerType(Type):
    """A pointer type."""

    def is_pointer(self):
        """Returns ``True``."""
        return True

    @property
    def pointed_type(self):
        """The type this pointer type points to (:class:`.Type`)."""
        return Type._from_clang_type(self._type.get_pointee())

    def __eq__(self, other):
        return (isinstance(other, PointerType) and
                self.pointed_type == other.pointed_type)

    def __hash__(self):
        return hash('pointer') + hash(self.pointed_type)

    def __repr__(self):
        return '<{} pointed_type={}>'.format(
            self.__class__.__name__,
            self.pointed_type
        )

    def __str__(self):
        s = str(self.pointed_type)
        s += '*' if self.pointed_type.is_pointer() else ' *'
        return s
