"""
    A ternary operator (?:).
"""

from regression_tests.parsers.c_parser.exprs.expression import Expression
from regression_tests.parsers.c_parser.utils import nth_item
from regression_tests.parsers.c_parser.utils import remove_whitespace
from regression_tests.parsers.c_parser.utils import string_from_tokens


class TernaryOpExpr(Expression):
    """A ternary operator (?:)."""

    def is_ternary_op(self):
        """Returns ``True``."""
        return True

    @property
    def cond(self):
        """Condition of the ternary operator (:class:`.Expression`)."""
        return Expression._from_clang_node(next(self._node.get_children()))

    @property
    def true_value(self):
        """True value of the ternary operator (:class:`.Expression`)."""
        return Expression._from_clang_node(
            nth_item(1, self._node.get_children()))

    @property
    def false_value(self):
        """False value of the ternary operator (:class:`.Expression`)."""
        return Expression._from_clang_node(
            nth_item(2, self._node.get_children()))

    def __eq__(self, other):
        if isinstance(other, str):
            return string_from_tokens(self._node) == remove_whitespace(other)
        else:
            return (
                type(self) is type(other) and
                self.cond == other.cond and
                self.true_value == other.true_value and
                self.false_value == other.false_value
            )

    def __hash__(self):
        return hash(self.cond) + hash(self.true_value) + hash(self.false_value)

    def __repr__(self):
        return '<{} cond={} true_value={} false_value={}>'.format(
            self.__class__.__name__,
            self.cond,
            self.true_value,
            self.false_value
        )

    def __str__(self):
        return '{} ? {} : {}'.format(
            self.cond,
            self.true_value,
            self.false_value
        )
