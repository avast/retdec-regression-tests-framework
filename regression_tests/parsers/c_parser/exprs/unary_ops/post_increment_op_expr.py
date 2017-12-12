"""
    A post increment operator (``i++``).
"""

from regression_tests.parsers.c_parser.exprs.unary_ops.unary_op_expr import UnaryOpExpr


class PostIncrementOpExpr(UnaryOpExpr):
    """A post increment operator (``i++``)."""

    def is_post_increment_op(self):
        """Returns ``True``."""
        return True

    def __str__(self):
        return '{}++'.format(self.op)
