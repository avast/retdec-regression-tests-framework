"""
    A not operator (``!``).
"""

from regression_tests.parsers.c_parser.exprs.unary_ops.unary_op_expr import UnaryOpExpr


class NotOpExpr(UnaryOpExpr):
    """A not operator (``!``)."""

    def is_not_op(self):
        """Returns ``True``."""
        return True

    def __str__(self):
        return '!{}'.format(self.op)
