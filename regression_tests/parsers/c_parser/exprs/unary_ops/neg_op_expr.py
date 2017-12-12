"""
    A negation operator (``-``).
"""

from regression_tests.parsers.c_parser.exprs.unary_ops.unary_op_expr import UnaryOpExpr


class NegOpExpr(UnaryOpExpr):
    """A negation operator (``-``)."""

    def is_neg_op(self):
        """Returns ``True``."""
        return True

    def __str__(self):
        return '-{}'.format(self.op)
