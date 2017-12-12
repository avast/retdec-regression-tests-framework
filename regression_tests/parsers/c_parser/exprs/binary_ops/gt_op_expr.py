"""
    A greater than operator (``>``).
"""

from regression_tests.parsers.c_parser.exprs.binary_ops.binary_op_expr import BinaryOpExpr


class GtOpExpr(BinaryOpExpr):
    """A greater than operator (``>``)."""

    def is_gt_op(self):
        """Returns ``True``."""
        return True

    def __str__(self):
        return '{} > {}'.format(self.lhs, self.rhs)
