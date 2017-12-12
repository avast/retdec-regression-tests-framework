"""
    A variable.
"""

from clang import cindex

from regression_tests.parsers.c_parser.exprs.expression import Expression
from regression_tests.parsers.c_parser.utils import is_array_kind
from regression_tests.parsers.c_parser.utils import remove_whitespace


class Variable(Expression):
    """A variable."""

    @property
    def name(self):
        """Name of the variable (`str`)."""
        return self._node.spelling

    @property
    def initializer(self):
        """Initializer of the variable (:class:`.Expression`).

        If the variable has no initializer, it returns ``None``. Example:

        .. code-block:: c

            int i = 1;  // The initializer is 1.
            int j;      // No initializer.
        """
        children = list(self._node.get_children())
        if self._no_children_or_only_one_that_is_not_initializer(children):
            return None
        return Expression._from_clang_node(children[-1])

    def str_with_type(self):
        """Returns string representation containing type.

        Example: ``int a = 2``.
        """
        if self.type.is_composite_type():
            type = self.type.whole_name
        else:
            type = self.type

        str = '{} {}'.format(type, self.name)
        if self.initializer:
            str += ' = {}'.format(self.initializer)
        return str

    def _is_type_ref(self, node):
        """Is the node a type reference?"""
        return node.kind == cindex.CursorKind.TYPE_REF

    def _is_composite_or_enum(self, node):
        """Is the node a composite type or enum declaration?"""
        return node.kind in [
            cindex.CursorKind.STRUCT_DECL,
            cindex.CursorKind.UNION_DECL,
            cindex.CursorKind.ENUM_DECL,
        ]

    def _is_uninitialized_array_with_set_size(self, node):
        """Is the variable declared to be an array with size and not initialized?"""
        return (
            is_array_kind(self._node.type) and
            node.kind == cindex.CursorKind.INTEGER_LITERAL
        )

    def _no_children_or_only_one_that_is_not_initializer(self, children):
        """Do children not exist or is there only one that is not initializer?"""
        return (
            not children or
            (
                len(children) == 1 and
                (
                    self._is_composite_or_enum(children[0]) or
                    self._is_type_ref(children[0]) or
                    self._is_uninitialized_array_with_set_size(children[0])
                )
            )
        )

    def __eq__(self, other):
        if isinstance(other, str):
            return self.name == remove_whitespace(other)
        return (
            self.name == other.name and
            self.type == other.type and
            self.initializer == other.initializer
        )

    def __hash__(self):
        return hash(self.name) + hash(self.type) + hash(self.initializer)

    def __repr__(self):
        return '<{} type={} name={} initializer={}>'.format(
            self.__class__.__name__,
            self.type,
            self.name,
            self.initializer
        )

    def __str__(self):
        str = self.name
        if self.initializer:
            str += ' = {}'.format(self.initializer)
        return str
