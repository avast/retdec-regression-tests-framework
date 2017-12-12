"""
    A base class for all binary operators.
"""

from regression_tests.parsers.c_parser.exprs.expression import Expression
from regression_tests.parsers.c_parser.utils import nth_item
from regression_tests.parsers.c_parser.utils import remove_whitespace
from regression_tests.parsers.c_parser.utils import string_from_tokens


class BinaryOpExpr(Expression):
    """A base class for all binary operators."""

    @property
    def lhs(self):
        """Expression on the left side of operator (:class:`.Expression`)."""
        return Expression._from_clang_node(next(self._node.get_children()))

    @property
    def rhs(self):
        """Expression on the right side of operator (:class:`.Expression`)."""
        return Expression._from_clang_node(
            nth_item(1, self._node.get_children()))

    def __eq__(self, other):
        if isinstance(other, str):
            return string_from_tokens(self._node) == remove_whitespace(other)
        else:
            return (
                type(self) is type(other) and
                self.lhs == other.lhs and
                self.rhs == other.rhs
            )

    def __hash__(self):
        return hash(self.lhs) + hash(self.rhs)

    def __repr__(self):
        return '<{} lhs={} rhs={}>'.format(
            self.__class__.__name__,
            self.lhs,
            self.rhs
        )
