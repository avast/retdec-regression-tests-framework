"""
    A cast expression.
"""

from regression_tests.parsers.c_parser.exprs.expression import Expression
from regression_tests.parsers.c_parser.utils import last_child_node
from regression_tests.parsers.c_parser.utils import remove_whitespace
from regression_tests.parsers.c_parser.utils import string_from_tokens


class CastExpr(Expression):
    """A cast expression."""

    def is_cast(self):
        """Returns ``True``."""
        return True

    @property
    def dst_type(self):
        """Destination type (:class:`.Type`)."""
        return self.type

    @property
    def op(self):
        """Casted expression (:class:`.Expression`)."""
        return Expression._from_clang_node(last_child_node(self._node))

    def __eq__(self, other):
        if isinstance(other, str):
            return string_from_tokens(self._node) == remove_whitespace(other)
        else:
            return (
                type(self) is type(other) and
                self.dst_type == other.dst_type and
                self.op == other.op
            )

    def __hash__(self):
        return hash(self.dst_type) + hash(self.op)

    def __repr__(self):
        return '<{} dst_type={} op={}>'.format(
            self.__class__.__name__,
            self.dst_type,
            self.op
        )

    def __str__(self):
        return '({}) {}'.format(
            self.dst_type,
            self.op
        )
