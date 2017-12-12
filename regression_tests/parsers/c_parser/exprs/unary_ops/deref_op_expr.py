"""
    A dereference operator (``*``).
"""

from regression_tests.parsers.c_parser.exprs.unary_ops.unary_op_expr import UnaryOpExpr


class DerefOpExpr(UnaryOpExpr):
    """A dereference operator (``*``)."""

    def is_deref_op(self):
        """Returns ``True``."""
        return True

    def __str__(self):
        return '*{}'.format(self.op)
