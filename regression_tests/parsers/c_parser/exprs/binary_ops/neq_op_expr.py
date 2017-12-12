"""
    A not equals operator (``!=``).
"""

from regression_tests.parsers.c_parser.exprs.binary_ops.binary_op_expr import BinaryOpExpr


class NeqOpExpr(BinaryOpExpr):
    """A not equals operator (``!=``)."""

    def is_neq_op(self):
        """Returns ``True``."""
        return True

    def __str__(self):
        return '{} != {}'.format(self.lhs, self.rhs)
