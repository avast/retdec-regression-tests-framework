"""
    A bit-xor operator (``^``).
"""

from regression_tests.parsers.c_parser.exprs.binary_ops.binary_op_expr import BinaryOpExpr


class BitXorOpExpr(BinaryOpExpr):
    """A bit-xor operator (``^``)."""

    def is_bit_xor_op(self):
        """Returns ``True``."""
        return True

    def __str__(self):
        return '{} ^ {}'.format(self.lhs, self.rhs)
