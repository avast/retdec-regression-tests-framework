"""
    A bit left shift operator (``<<``).
"""

from regression_tests.parsers.c_parser.exprs.binary_ops.binary_op_expr import BinaryOpExpr


class BitShlOpExpr(BinaryOpExpr):
    """A bit left shift operator (``<<``)."""

    def is_bit_shl_op(self):
        """Returns ``True``."""
        return True

    def __str__(self):
        return '{} << {}'.format(self.lhs, self.rhs)
