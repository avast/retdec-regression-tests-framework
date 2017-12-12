"""
    An or operator (``||``).
"""

from regression_tests.parsers.c_parser.exprs.binary_ops.binary_op_expr import BinaryOpExpr


class OrOpExpr(BinaryOpExpr):
    """An or operator (``||``)."""

    def is_or_op(self):
        """Returns ``True``."""
        return True

    def __str__(self):
        return '{} || {}'.format(self.lhs, self.rhs)
