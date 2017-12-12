"""
    A representation of an array type.
"""

from regression_tests.parsers.c_parser.types.type import Type
from regression_tests.parsers.c_parser.utils import is_array_kind


class ArrayType(Type):
    """A representation of an array type."""

    def is_array(self):
        """Returns ``True``."""
        return True

    @property
    def element_type(self):
        """Type of elements in the array.

        For example, for ``int [10]``, it returns an instance of
        :class:`.IntType`.
        """
        type = self._type.element_type

        while is_array_kind(type):
            type = type.element_type

        return Type._from_clang_type(type)

    @property
    def element_count(self):
        """Number of elements in the array.

        If the array is multidimensional, a tuple consisting of element counts
        for each dimension is returned. For example, for ``int [10]``, it
        returns ``10``, and for ``int [10][20][30]``, it returns ``(10, 20,
        30)``.

        If the array is incomplete (e.g. ``int []``), it returns ``1`` because
        Clang behaves this way and there is no way of distinguishing e.g. ``int
        []`` from ``int [1]``.

        Returns ``None`` if the number of elements cannot be obtained.
        """
        type = self._type
        count_list = []

        while is_array_kind(type):
            try:
                # Type.element_count raises Exception when the element count
                # cannot be obtained.
                count_list.append(type.element_count)
            except Exception:
                count_list.append(None)
            type = type.element_type

        if len(count_list) == 1:
            return count_list[0]
        else:
            return tuple(count_list)

    @property
    def dimension(self):
        """Dimension of the array.

        For example, for ``int [10][10][10]``, it returns 3.
        """
        dimension = 1
        type = self._type.element_type

        while is_array_kind(type):
            type = type.element_type
            dimension += 1

        return dimension

    def __eq__(self, other):
        return (
            isinstance(other, ArrayType) and
            self.element_type == other.element_type and
            self.element_count == other.element_count
        )

    def __hash__(self):
        return hash('array') + hash(self.element_type) + hash(self.element_count)

    def __repr__(self):
        return '<{} element_type={} element_count={} dimension={}>'.format(
            self.__class__.__name__,
            self.element_type,
            self.element_count,
            self.dimension
        )

    def __str__(self):
        return '{} []'.format(self.element_type)
