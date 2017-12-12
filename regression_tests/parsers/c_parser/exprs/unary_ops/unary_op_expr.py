"""
    A base class for all unary operators.
"""

from regression_tests.parsers.c_parser.exprs.expression import Expression
from regression_tests.parsers.c_parser.utils import first_child_node
from regression_tests.parsers.c_parser.utils import remove_whitespace
from regression_tests.parsers.c_parser.utils import string_from_tokens


class UnaryOpExpr(Expression):
    """A base class for all unary operators."""

    @property
    def op(self):
        """Operand (:class:`.Expression`)."""
        return Expression._from_clang_node(first_child_node(self._node))

    def __eq__(self, other):
        if isinstance(other, str):
            return string_from_tokens(self._node) == remove_whitespace(other)
        else:
            return (
                type(self) is type(other) and
                self.op == other.op
            )

    def __hash__(self):
        return hash(self.op)

    def __repr__(self):
        return '<{} op={}>'.format(
            self.__class__.__name__,
            self.op
        )
