"""
    A comma operator (``,``).
"""

from regression_tests.parsers.c_parser.exprs.binary_ops.binary_op_expr import BinaryOpExpr


class CommaOpExpr(BinaryOpExpr):
    """A comma operator (``,``)."""

    def is_comma_op(self):
        """Returns ``True``."""
        return True

    def __str__(self):
        return '{} , {}'.format(self.lhs, self.rhs)
