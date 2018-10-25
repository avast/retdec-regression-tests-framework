"""
    Tests for the :module`regression_tests.parsers.c_parser.expression` module.
"""

from unittest import mock

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
from regression_tests.parsers.c_parser.exprs.expression import Expression
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
from tests.parsers.c_parser import WithModuleTests


class ExpressionTests(WithModuleTests):
    """Tests for `Expression`."""

    def test_from_clang_node_returns_integral_literal_for_int_literal(self):
        expr = self.get_expr('1', 'int')
        self.assertIsInstance(expr, IntegralLiteral)

    def scenario_is_integral_literal(self, value, type):
        self.assertIsInstance(self.get_expr_from_global_var(value, type), IntegralLiteral)

    def test_from_clang_node_returns_integral_literal_for_typedefed_int_literals(self):
        self.scenario_is_integral_literal('1', 'int8_t')
        self.scenario_is_integral_literal('1', 'int16_t')
        self.scenario_is_integral_literal('1', 'int32_t')
        self.scenario_is_integral_literal('1', 'int64_t')
        self.scenario_is_integral_literal('1', 'uint8_t')
        self.scenario_is_integral_literal('1', 'uint16_t')
        self.scenario_is_integral_literal('1', 'uint32_t')
        self.scenario_is_integral_literal('1', 'uint64_t')

    def test_from_clang_node_returns_fp_literal_for_double_literal(self):
        expr = self.get_expr('1.0', 'double')
        self.assertIsInstance(expr, FloatingPointLiteral)

    def test_from_clang_node_returns_fp_literal_for_float_literal_with_f_suffix(self):
        expr = self.get_expr('1.0f', 'float')
        self.assertIsInstance(expr, FloatingPointLiteral)

    def test_from_clang_node_returns_fp_literal_for_float_literal_with_F_suffix(self):
        expr = self.get_expr('1.0F', 'float')
        self.assertIsInstance(expr, FloatingPointLiteral)

    def test_from_clang_node_returns_fp_literal_for_long_double_literal_with_l_suffix(self):
        expr = self.get_expr('1.0l', 'long double')
        self.assertIsInstance(expr, FloatingPointLiteral)

    def test_from_clang_node_returns_fp_literal_for_long_double_literal_with_L_suffix(self):
        expr = self.get_expr_from_global_var('1.0L', 'long double')
        self.assertIsInstance(expr, FloatingPointLiteral)

    def test_from_clang_node_returns_character_literal_for_char_literal(self):
        expr = self.get_expr("'a'", 'int')
        self.assertIsInstance(expr, CharacterLiteral)

    def test_from_clang_node_returns_string_literal_for_string_literal(self):
        expr = self.get_expr('"hello"', 'const char *')
        self.assertIsInstance(expr, StringLiteral)

    def test_from_clang_node_returns_eq_op_expr_for_eq_op(self):
        expr = self.get_expr('1 == 2', 'int')
        self.assertIsInstance(expr, EqOpExpr)

    def test_from_clang_node_returns_neq_op_expr_for_neq_op(self):
        expr = self.get_expr('1 != 2', 'int')
        self.assertIsInstance(expr, NeqOpExpr)

    def test_from_clang_node_returns_gt_op_expr_for_gt_op(self):
        expr = self.get_expr('1 > 2', 'int')
        self.assertIsInstance(expr, GtOpExpr)

    def test_from_clang_node_returns_gt_eq_op_expr_for_gt_eq_op(self):
        expr = self.get_expr('1 >= 2', 'int')
        self.assertIsInstance(expr, GtEqOpExpr)

    def test_from_clang_node_returns_lt_op_expr_for_lt_op(self):
        expr = self.get_expr('1 < 2', 'int')
        self.assertIsInstance(expr, LtOpExpr)

    def test_from_clang_node_returns_lt_eq_op_expr_for_lt_eq_op(self):
        expr = self.get_expr('1 <= 2', 'int')
        self.assertIsInstance(expr, LtEqOpExpr)

    def test_from_clang_node_returns_add_op_expr_for_add_op(self):
        expr = self.get_expr('1 + 2', 'int')
        self.assertIsInstance(expr, AddOpExpr)

    def test_from_clang_node_returns_sub_op_expr_for_sub_op(self):
        expr = self.get_expr('1 - 2', 'int')
        self.assertIsInstance(expr, SubOpExpr)

    def test_from_clang_node_returns_mul_op_expr_for_mul_op(self):
        expr = self.get_expr('1 * 2', 'int')
        self.assertIsInstance(expr, MulOpExpr)

    def test_from_clang_node_returns_mod_op_expr_for_mod_op(self):
        expr = self.get_expr('1 % 2', 'int')
        self.assertIsInstance(expr, ModOpExpr)

    def test_from_clang_node_returns_div_op_expr_for_div_op(self):
        expr = self.get_expr('1 / 2', 'int')
        self.assertIsInstance(expr, DivOpExpr)

    def test_from_clang_node_returns_and_op_expr_for_and_op(self):
        expr = self.get_expr('1 && 2', 'int')
        self.assertIsInstance(expr, AndOpExpr)

    def test_from_clang_node_returns_or_op_expr_for_or_op(self):
        expr = self.get_expr('1 || 2', 'int')
        self.assertIsInstance(expr, OrOpExpr)

    def test_from_clang_node_returns_bit_and_op_expr_for_bit_and_op(self):
        expr = self.get_expr('1 & 2', 'int')
        self.assertIsInstance(expr, BitAndOpExpr)

    def test_from_clang_node_returns_bit_or_op_expr_for_bit_or_op(self):
        expr = self.get_expr('1 | 2', 'int')
        self.assertIsInstance(expr, BitOrOpExpr)

    def test_from_clang_node_returns_bit_xor_op_expr_for_bit_xor_op(self):
        expr = self.get_expr('1 ^ 2', 'int')
        self.assertIsInstance(expr, BitXorOpExpr)

    def test_from_clang_node_returns_bit_shl_op_expr_for_bit_shl_op(self):
        expr = self.get_expr('1 << 2', 'int')
        self.assertIsInstance(expr, BitShlOpExpr)

    def test_from_clang_node_returns_bit_shr_op_expr_for_bit_shr_op(self):
        expr = self.get_expr('1 >> 2', 'int')
        self.assertIsInstance(expr, BitShrOpExpr)

    def test_from_clang_node_returns_not_op_expr_for_not_op(self):
        expr = self.get_expr('! 1', 'int')
        self.assertIsInstance(expr, NotOpExpr)

    def test_from_clang_node_returns_neg_op_expr_for_neg_op(self):
        expr = self.get_expr('- 1', 'int')
        self.assertIsInstance(expr, NegOpExpr)

    def test_from_clang_node_returns_assign_op_expr_for_assign_op(self):
        expr = self.get_expr('a = 2', 'int')
        self.assertIsInstance(expr, AssignOpExpr)

    def test_from_clang_node_returns_address_op_expr_for_address_op(self):
        expr = self.get_expr('&a', 'int')
        self.assertIsInstance(expr, AddressOpExpr)

    def test_from_clang_node_returns_deref_op_expr_for_deref_op(self):
        expr = self.get_expr('*a', 'int *')
        self.assertIsInstance(expr, DerefOpExpr)

    def test_from_clang_node_returns_array_index_op_expr_for_array_index_op(self):
        expr = self.get_array_index_op_expr('array', 0, 'int')
        self.assertIsInstance(expr, ArrayIndexOpExpr)

    def test_from_clang_node_returns_comma_op_expr_for_comma_op(self):
        expr = self.get_comma_op_expr('1', '2')
        self.assertIsInstance(expr, CommaOpExpr)

    def test_from_clang_node_returns_ternary_op_expr_for_ternary_op(self):
        expr = self.get_expr('1 ? 2 : 3', 'int')
        self.assertIsInstance(expr, TernaryOpExpr)

    def test_from_clang_node_returns_call_expr_for_call(self):
        expr = self.get_expr('foo()', 'int')
        self.assertIsInstance(expr, CallExpr)

    def test_from_clang_node_returns_cast_expr_for_cast(self):
        expr = self.get_expr('(int) 1.5', 'int')
        self.assertIsInstance(expr, CastExpr)

    def test_from_clang_node_returns_pre_increment_op_expr_for_pre_increment_op(self):
        expr = self.get_expr('++a', 'int')
        self.assertIsInstance(expr, PreIncrementOpExpr)

    def test_from_clang_node_returns_post_increment_op_expr_for_post_increment_op(self):
        expr = self.get_expr('a++', 'int')
        self.assertIsInstance(expr, PostIncrementOpExpr)

    def test_from_clang_node_returns_pre_decrement_op_expr_for_pre_decrement_op(self):
        expr = self.get_expr('--a', 'int')
        self.assertIsInstance(expr, PreDecrementOpExpr)

    def test_from_clang_node_returns_post_decrement_op_expr_for_post_decrement_op(self):
        expr = self.get_expr('a--', 'int')
        self.assertIsInstance(expr, PostDecrementOpExpr)

    def test_from_clang_node_returns_compound_assign_op_expr_for_compound_assign_ops(self):
        expr = self.get_expr('a += 2', 'int')
        self.assertIsInstance(expr, CompoundAssignOpExpr)
        expr = self.get_expr('a -= 2', 'int')
        self.assertIsInstance(expr, CompoundAssignOpExpr)
        expr = self.get_expr('a *= 2', 'int')
        self.assertIsInstance(expr, CompoundAssignOpExpr)
        expr = self.get_expr('a /= 2', 'int')
        self.assertIsInstance(expr, CompoundAssignOpExpr)
        expr = self.get_expr('a %= 2', 'int')
        self.assertIsInstance(expr, CompoundAssignOpExpr)
        expr = self.get_expr('a &= 2', 'int')
        self.assertIsInstance(expr, CompoundAssignOpExpr)
        expr = self.get_expr('a |= 2', 'int')
        self.assertIsInstance(expr, CompoundAssignOpExpr)
        expr = self.get_expr('a ^= 2', 'int')
        self.assertIsInstance(expr, CompoundAssignOpExpr)
        expr = self.get_expr('a <<= 2', 'int')
        self.assertIsInstance(expr, CompoundAssignOpExpr)
        expr = self.get_expr('a >>= 2', 'int')
        self.assertIsInstance(expr, CompoundAssignOpExpr)

    def test_from_clang_node_returns_struct_ref_op_expr_for_struct_ref_op(self):
        expr = self.get_struct_ref_op_expr('s', 'x')
        self.assertIsInstance(expr, StructRefOpExpr)

    def test_from_clang_node_returns_struct_deref_op_expr_for_struct_deref_op(self):
        expr = self.get_struct_deref_op_expr('s', 'x')
        self.assertIsInstance(expr, StructDerefOpExpr)

    def test_from_clang_node_skips_parenthesized_expressions(self):
        # The include and NULL have to be there. Otherwise, the expression is
        # not of kind cindex.CursorKind.PAREN_EXPR (the point of this test).
        module = self.parse("""
            #include <stdlib.h>

            void (*x)() = NULL;
        """)
        x = module.global_vars[0]
        self.assertEqual(x.name, 'x')
        self.assertIsInstance(x.initializer, CastExpr)  # Cast from NULL to void*.

    def test_from_clang_node_raises_assertion_error_upon_unsupported_expression(self):
        unsupported_expr = mock.Mock()
        with self.assertRaisesRegex(AssertionError, r'.*unsupported.*'):
            Expression._from_clang_node(unsupported_expr)
