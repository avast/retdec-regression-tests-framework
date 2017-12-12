"""
    An address operator (``&``).
"""

from regression_tests.parsers.c_parser.exprs.unary_ops.unary_op_expr import UnaryOpExpr


class AddressOpExpr(UnaryOpExpr):
    """An address operator (``&``)."""

    def is_address_op(self):
        """Returns ``True``."""
        return True

    def __str__(self):
        return '&{}'.format(self.op)
