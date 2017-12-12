"""
    A multiplication operator (``*``).
"""

from regression_tests.parsers.c_parser.exprs.binary_ops.binary_op_expr import BinaryOpExpr


class MulOpExpr(BinaryOpExpr):
    """A multiplication operator (``*``)."""

    def is_mul_op(self):
        """Returns ``True``."""
        return True

    def __str__(self):
        return '{} * {}'.format(self.lhs, self.rhs)
