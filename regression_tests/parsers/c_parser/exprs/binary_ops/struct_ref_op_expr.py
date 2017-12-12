"""
    A structure reference operator (``.``).
"""

from regression_tests.parsers.c_parser.exprs.binary_ops.struct_op_expr import StructOpExpr


class StructRefOpExpr(StructOpExpr):
    """A structure reference operator (``.``)."""

    def is_struct_ref_op(self):
        """Returns ``True``."""
        return True
