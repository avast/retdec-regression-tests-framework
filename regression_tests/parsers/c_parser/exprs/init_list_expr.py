"""
    Initializer expression.
"""

from regression_tests.parsers.c_parser.exprs.expression import Expression


class InitListExpr(Expression):
    """Initializer expression.

    Contains a list of initializer values. Each value can be accessed by its
    position using the ``[]`` operator.

    .. code-block:: python

        init_list = InitListExpr(some_node)
        init_list[0]  # Returns the first value of the initializer.

    :raises IndexError: When the initializer is empty.
    """

    @property
    def values(self):
        """A list of values in the initializer expression."""
        return list(map(self._from_clang_node, self._node.get_children()))

    def __getitem__(self, item):
        return self.values[item]

    def __len__(self):
        return len(self.values)

    def __eq__(self, other):
        if isinstance(other, InitListExpr):
            other = other.values
        return self.values == other

    def __hash__(self):
        return hash(str(self.values))

    def __repr__(self):
        return '<%s {%s}>' % (
            self.__class__.__name__, ', '.join(map(str, self.values)),
        )

    def __str__(self):
        return '{%s}' % (', '.join(map(str, self.values)))
