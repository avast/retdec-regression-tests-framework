"""
    A structure dereference operator (``->``).
"""

from regression_tests.parsers.c_parser.exprs.binary_ops.struct_op_expr import StructOpExpr


class StructDerefOpExpr(StructOpExpr):
    """A structure dereference operator (``->``)."""

    def is_struct_deref_op(self):
        """Returns ``True``."""
        return True
