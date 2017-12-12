"""
    A base class for structure operators.
"""

from regression_tests.parsers.c_parser.exprs.binary_ops.binary_op_expr import BinaryOpExpr


class StructOpExpr(BinaryOpExpr):
    """A base class for structure operators."""

    @property
    def lhs(self):
        return next(self._node.get_tokens()).spelling

    @property
    def rhs(self):
        return list(self._node.get_tokens())[2].spelling

    @property
    def _operator(self):
        return list(self._node.get_tokens())[1].spelling

    def __str__(self):
        return '{}{}{}'.format(self.lhs, self._operator, self.rhs)
