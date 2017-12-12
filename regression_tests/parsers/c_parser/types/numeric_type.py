"""
    A base class for all types representing numbers (``int``, ``float``,
    etc.).
"""

from regression_tests.parsers.c_parser.types.type import Type


class NumericType(Type):
    """A base class for all types representing numbers (``int``, ``float``,
    etc.).
    """

    def __init__(self, type, size=None):
        """
        :param clang.cindex.Type type: Internal type.
        :param int size: Size in bits (optional).
        """
        super().__init__(type)
        self._size = size

    @property
    def size(self):
        """Size in bits (or ``None`` if not defined)."""
        return self._size

    def _is_of_size_if_not_none(self, size):
        """Checks if the type is of the given size (if not ``None``).
        """
        if size is None:
            return True
        return self.size == size
