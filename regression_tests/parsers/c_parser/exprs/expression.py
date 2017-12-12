"""
    A base class of all expressions.
"""

from abc import ABCMeta
from abc import abstractmethod

from clang import cindex

from regression_tests.parsers.c_parser.utils import first_child_node
from regression_tests.parsers.c_parser.utils import has_token
from regression_tests.parsers.c_parser.utils import has_token_in_position


class Expression(metaclass=ABCMeta):
    """A base class of all expressions."""

    def __init__(self, node):
        """
        :param node: Internal node representing the expression.
        """
        self._node = node

    def is_eq_op(self):
        """Is the expression an equals operator?"""
        return False

    def is_neq_op(self):
        """Is the expression a not equals operator?"""
        return False

    def is_gt_op(self):
        """Is the expression a greater than operator?"""
        return False

    def is_gt_eq_op(self):
        """Is the expression a greater than or equal operator?"""
        return False

    def is_lt_op(self):
        """Is the expression a less than operator?"""
        return False

    def is_lt_eq_op(self):
        """Is the expression a less than or equal operator?"""
        return False

    def is_add_op(self):
        """Is the expression an add operator?"""
        return False

    def is_sub_op(self):
        """Is the expression a subtraction operator?"""
        return False

    def is_mul_op(self):
        """Is the expression a multiplication operator?"""
        return False

    def is_mod_op(self):
        """Is the expression a modulo operator?"""
        return False

    def is_div_op(self):
        """Is the expression a division operator?"""
        return False

    def is_and_op(self):
        """Is the expression an and operator?"""
        return False

    def is_or_op(self):
        """Is the expression an or operator?"""
        return False

    def is_bit_and_op(self):
        """Is the expression a bit-and operator?"""
        return False

    def is_bit_or_op(self):
        """Is the expression a bit-or operator?"""
        return False

    def is_bit_xor_op(self):
        """Is the expression a bit-xor operator?"""
        return False

    def is_bit_shl_op(self):
        """Is the expression a bit left shift operator?"""
        return False

    def is_bit_shr_op(self):
        """Is the expression a bit right shift operator?"""
        return False

    def is_not_op(self):
        """Is the expression a not operator?"""
        return False

    def is_neg_op(self):
        """Is the expression a negation operator?"""
        return False

    def is_assign_op(self):
        """Is the expression an assignment operator?"""
        return False

    def is_address_op(self):
        """Is the expression an address operator?"""
        return False

    def is_deref_op(self):
        """Is the expression a dereference operator?"""
        return False

    def is_array_index_op(self):
        """Is the expression an array subscript operator?"""
        return False

    def is_comma_op(self):
        """Is the expression a comma operator?"""
        return False

    def is_ternary_op(self):
        """Is the expression a ternary operator?"""
        return False

    def is_call(self):
        """Is the expression a call expression?"""
        return False

    def is_cast(self):
        """Is the expression a cast expression?"""
        return False

    def is_pre_increment_op(self):
        """Is the expression a pre increment operator?"""
        return False

    def is_post_increment_op(self):
        """Is the expression a post increment operator?"""
        return False

    def is_pre_decrement_op(self):
        """Is the expression a pre decrement operator?"""
        return False

    def is_post_decrement_op(self):
        """Is the expression a post decrement operator?"""
        return False

    def is_compound_assign_op(self):
        """Is the expression a compound assignment operator?"""
        return False

    def is_struct_ref_op(self):
        """Is the expression a struct reference operator?"""
        return False

    def is_struct_deref_op(self):
        """Is the expression a struct dereference operator?"""
        return False

    @staticmethod
    def _from_clang_node(node):
        """Creates a new expression from the given clang node.

        :param node: Internal node representing the expression.

        :raises AssertionError: If the expression is not supported.
        """
        # Nodes of kind UNEXPOSED_EXPR are useless because we cannot convert
        # them, so skip them.
        node = Expression._skip_unexposed_expressions(node)

        # Literals.
        if node.kind == cindex.CursorKind.INTEGER_LITERAL:
            return IntegralLiteral(node)
        elif node.kind == cindex.CursorKind.FLOATING_LITERAL:
            return FloatingPointLiteral(node)
        elif node.kind == cindex.CursorKind.CHARACTER_LITERAL:
            return CharacterLiteral(node)
        elif node.kind == cindex.CursorKind.STRING_LITERAL:
            return StringLiteral(node)

        # Array initializer.
        elif node.kind == cindex.CursorKind.INIT_LIST_EXPR:
            return InitListExpr(node)

        # Identifier.
        elif node.kind == cindex.CursorKind.DECL_REF_EXPR:
            from regression_tests.parsers.c_parser.exprs.variable import Variable
            return Variable(node)

        # Ternary operator.
        elif node.kind == cindex.CursorKind.CONDITIONAL_OPERATOR:
            return TernaryOpExpr(node)

        # Call expression.
        elif node.kind == cindex.CursorKind.CALL_EXPR:
            return CallExpr(node)

        # Cast expression.
        elif node.kind == cindex.CursorKind.CSTYLE_CAST_EXPR:
            return CastExpr(node)

        # Binary operators.
        elif node.kind == cindex.CursorKind.COMPOUND_ASSIGNMENT_OPERATOR:
            return CompoundAssignOpExpr(node)
        elif node.kind == cindex.CursorKind.BINARY_OPERATOR:
            if has_token(node, '='):
                return AssignOpExpr(node)
            elif has_token(node, '=='):
                return EqOpExpr(node)
            elif has_token(node, '!='):
                return NeqOpExpr(node)
            elif has_token(node, '>'):
                return GtOpExpr(node)
            elif has_token(node, '>='):
                return GtEqOpExpr(node)
            elif has_token(node, '<'):
                return LtOpExpr(node)
            elif has_token(node, '<='):
                return LtEqOpExpr(node)
            elif has_token(node, '+'):
                return AddOpExpr(node)
            elif has_token(node, '-'):
                return SubOpExpr(node)
            elif has_token(node, '*'):
                return MulOpExpr(node)
            elif has_token(node, '%'):
                return ModOpExpr(node)
            elif has_token(node, '/'):
                return DivOpExpr(node)
            elif has_token(node, '&&'):
                return AndOpExpr(node)
            elif has_token(node, '||'):
                return OrOpExpr(node)
            elif has_token(node, '&'):
                return BitAndOpExpr(node)
            elif has_token(node, '|'):
                return BitOrOpExpr(node)
            elif has_token(node, '^'):
                return BitXorOpExpr(node)
            elif has_token(node, '<<'):
                return BitShlOpExpr(node)
            elif has_token(node, '>>'):
                return BitShrOpExpr(node)
            elif has_token(node, ','):
                return CommaOpExpr(node)
        elif node.kind == cindex.CursorKind.ARRAY_SUBSCRIPT_EXPR:
            return ArrayIndexOpExpr(node)
        elif node.kind == cindex.CursorKind.MEMBER_REF_EXPR:
            if has_token(node, '.'):
                return StructRefOpExpr(node)
            elif has_token(node, '->'):
                return StructDerefOpExpr(node)

        # Unary operators.
        elif node.kind == cindex.CursorKind.UNARY_OPERATOR:
            if has_token(node, '!'):
                return NotOpExpr(node)
            elif has_token(node, '-'):
                return NegOpExpr(node)
            elif has_token(node, '&'):
                return AddressOpExpr(node)
            elif has_token(node, '*'):
                return DerefOpExpr(node)
            elif has_token_in_position(node, '++', 0):
                return PreIncrementOpExpr(node)
            elif has_token_in_position(node, '++', 1):
                return PostIncrementOpExpr(node)
            elif has_token_in_position(node, '--', 0):
                return PreDecrementOpExpr(node)
            elif has_token_in_position(node, '--', 1):
                return PostDecrementOpExpr(node)

        raise AssertionError('unsupported expression `{}` of kind {}'.format(
            node.spelling, node.kind))

    @property
    def type(self):
        """Type of the expression (:class:`.Type`)."""
        return Type._from_clang_type(self._node.type)

    @abstractmethod
    def __eq__(self, other):
        raise NotImplementedError

    def __ne__(self, other):
        return not self == other

    @abstractmethod
    def __hash__(self):
        raise NotImplementedError

    @staticmethod
    def _skip_unexposed_expressions(node):
        """Skips nodes of kind `UNEXPOSED_EXPR` and returns the first node that
        is not of that kind.
        """
        while node.kind == cindex.CursorKind.UNEXPOSED_EXPR:
            node = first_child_node(node)
        return node


from regression_tests.parsers.c_parser.exprs.init_list_expr import InitListExpr
from regression_tests.parsers.c_parser.exprs.binary_ops.add_op_expr import AddOpExpr
from regression_tests.parsers.c_parser.exprs.binary_ops.and_op_expr import AndOpExpr
from regression_tests.parsers.c_parser.exprs.binary_ops.array_index_op_expr import ArrayIndexOpExpr
from regression_tests.parsers.c_parser.exprs.binary_ops.assign_op_expr import AssignOpExpr
from regression_tests.parsers.c_parser.exprs.binary_ops.bit_and_op_expr import BitAndOpExpr
from regression_tests.parsers.c_parser.exprs.binary_ops.bit_or_op_expr import BitOrOpExpr
from regression_tests.parsers.c_parser.exprs.binary_ops.bit_shl_op_expr import BitShlOpExpr
from regression_tests.parsers.c_parser.exprs.binary_ops.bit_shr_op_expr import BitShrOpExpr
from regression_tests.parsers.c_parser.exprs.binary_ops.bit_xor_op_expr import BitXorOpExpr
from regression_tests.parsers.c_parser.exprs.binary_ops.comma_op_expr import CommaOpExpr
from regression_tests.parsers.c_parser.exprs.binary_ops.compound_assign_op_expr import CompoundAssignOpExpr
from regression_tests.parsers.c_parser.exprs.binary_ops.div_op_expr import DivOpExpr
from regression_tests.parsers.c_parser.exprs.binary_ops.eq_op_expr import EqOpExpr
from regression_tests.parsers.c_parser.exprs.binary_ops.gt_op_expr import GtOpExpr
from regression_tests.parsers.c_parser.exprs.binary_ops.gt_eq_op_expr import GtEqOpExpr
from regression_tests.parsers.c_parser.exprs.binary_ops.lt_op_expr import LtOpExpr
from regression_tests.parsers.c_parser.exprs.binary_ops.lt_eq_op_expr import LtEqOpExpr
from regression_tests.parsers.c_parser.exprs.binary_ops.mod_op_expr import ModOpExpr
from regression_tests.parsers.c_parser.exprs.binary_ops.mul_op_expr import MulOpExpr
from regression_tests.parsers.c_parser.exprs.binary_ops.neq_op_expr import NeqOpExpr
from regression_tests.parsers.c_parser.exprs.binary_ops.or_op_expr import OrOpExpr
from regression_tests.parsers.c_parser.exprs.binary_ops.struct_deref_op_expr import StructDerefOpExpr
from regression_tests.parsers.c_parser.exprs.binary_ops.struct_ref_op_expr import StructRefOpExpr
from regression_tests.parsers.c_parser.exprs.binary_ops.sub_op_expr import SubOpExpr
from regression_tests.parsers.c_parser.exprs.call_expr import CallExpr
from regression_tests.parsers.c_parser.exprs.cast_expr import CastExpr
from regression_tests.parsers.c_parser.exprs.literals.character_literal import CharacterLiteral
from regression_tests.parsers.c_parser.exprs.literals.floating_point_literal import FloatingPointLiteral
from regression_tests.parsers.c_parser.exprs.literals.integral_literal import IntegralLiteral
from regression_tests.parsers.c_parser.exprs.literals.string_literal import StringLiteral
from regression_tests.parsers.c_parser.exprs.ternary_op_expr import TernaryOpExpr
from regression_tests.parsers.c_parser.exprs.unary_ops.address_op_expr import AddressOpExpr
from regression_tests.parsers.c_parser.exprs.unary_ops.deref_op_expr import DerefOpExpr
from regression_tests.parsers.c_parser.exprs.unary_ops.neg_op_expr import NegOpExpr
from regression_tests.parsers.c_parser.exprs.unary_ops.not_op_expr import NotOpExpr
from regression_tests.parsers.c_parser.exprs.unary_ops.post_decrement_op_expr import PostDecrementOpExpr
from regression_tests.parsers.c_parser.exprs.unary_ops.post_increment_op_expr import PostIncrementOpExpr
from regression_tests.parsers.c_parser.exprs.unary_ops.pre_decrement_op_expr import PreDecrementOpExpr
from regression_tests.parsers.c_parser.exprs.unary_ops.pre_increment_op_expr import PreIncrementOpExpr
from regression_tests.parsers.c_parser.types.type import Type
