"""
    A less than or equal operator (``<=``).
"""

from regression_tests.parsers.c_parser.exprs.binary_ops.binary_op_expr import BinaryOpExpr


class LtEqOpExpr(BinaryOpExpr):
    """A less than or equal operator (``<=``)."""

    def is_lt_eq_op(self):
        """Returns ``True``."""
        return True

    def __str__(self):
        return '{} <= {}'.format(self.lhs, self.rhs)
