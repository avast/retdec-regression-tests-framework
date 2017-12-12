"""
    A pre decrement operator (``--i``).
"""

from regression_tests.parsers.c_parser.exprs.unary_ops.unary_op_expr import UnaryOpExpr


class PreDecrementOpExpr(UnaryOpExpr):
    """A pre decrement operator (``--i``)."""

    def is_pre_decrement_op(self):
        """Returns ``True``."""
        return True

    def __str__(self):
        return '--{}'.format(self.op)
