"""
    A bit-and operator (``&``).
"""

from regression_tests.parsers.c_parser.exprs.binary_ops.binary_op_expr import BinaryOpExpr


class BitAndOpExpr(BinaryOpExpr):
    """A bit-and operator (``&``)."""

    def is_bit_and_op(self):
        """Returns ``True``."""
        return True

    def __str__(self):
        return '{} & {}'.format(self.lhs, self.rhs)
