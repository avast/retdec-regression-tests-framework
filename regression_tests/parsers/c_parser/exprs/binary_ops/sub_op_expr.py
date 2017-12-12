"""
    A subtraction operator (``-``).
"""

from regression_tests.parsers.c_parser.exprs.binary_ops.binary_op_expr import BinaryOpExpr


class SubOpExpr(BinaryOpExpr):
    """A subtraction operator (``-``)."""

    def is_sub_op(self):
        """Returns ``True``."""
        return True

    def __str__(self):
        return '{} - {}'.format(self.lhs, self.rhs)
