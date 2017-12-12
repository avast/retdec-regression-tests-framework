"""
    A compound assignment operator (``+=, -=, *=, /=, %=, &=, |=, ^=, <<=,
    >>=``).
"""

from regression_tests.parsers.c_parser.exprs.binary_ops.binary_op_expr import BinaryOpExpr
from regression_tests.parsers.c_parser.utils import remove_whitespace
from regression_tests.utils import memoize


class CompoundAssignOpExpr(BinaryOpExpr):
    """A compound assignment operator (``+=, -=, *=, /=, %=, &=, |=, ^=, <<=,
    >>=``).
    """

    def is_compound_assign_op(self):
        """Returns ``True``."""
        return True

    @property
    def identification(self):
        """Returns string identifying the expression."""
        return remove_whitespace(str(self))

    @property
    @memoize
    def _operator(self):
        return list(self._node.get_tokens())[1].spelling

    def __str__(self):
        return '{} {} {}'.format(self.lhs, self._operator, self.rhs)
