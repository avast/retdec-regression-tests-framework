"""
    An assignment operator (``=``).
"""

from regression_tests.parsers.c_parser.exprs.binary_ops.binary_op_expr import BinaryOpExpr
from regression_tests.parsers.c_parser.utils import remove_whitespace


class AssignOpExpr(BinaryOpExpr):
    """An assignment operator (``=``)."""

    def is_assign_op(self):
        """Returns ``True``."""
        return True

    @property
    def identification(self):
        """Returns string identifying the expression."""
        return remove_whitespace(str(self))

    def __str__(self):
        return '{} = {}'.format(self.lhs, self.rhs)
