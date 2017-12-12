"""
    Tests for the
    :module`regression_tests.parsers.c_parser.exprs.binary_ops.comma_op_expr`
    module.
"""

from tests.parsers.c_parser import WithModuleTests


class CommaOpExprTests(WithModuleTests):
    """Tests for `CommaOpExpr`."""

    def test_comma_op_expr_is_comma_op(self):
        comma_op_expr = self.get_comma_op_expr(1, 2)
        self.assertTrue(comma_op_expr.is_comma_op())

    def test_comma_op_expr_is_no_other_expr(self):
        comma_op_expr = self.get_comma_op_expr(1, 2)
        self.assertFalse(comma_op_expr.is_eq_op())
        self.assertFalse(comma_op_expr.is_neq_op())
        self.assertFalse(comma_op_expr.is_gt_op())
        self.assertFalse(comma_op_expr.is_gt_eq_op())
        self.assertFalse(comma_op_expr.is_lt_op())
        self.assertFalse(comma_op_expr.is_lt_eq_op())
        self.assertFalse(comma_op_expr.is_add_op())
        self.assertFalse(comma_op_expr.is_sub_op())
        self.assertFalse(comma_op_expr.is_mul_op())
        self.assertFalse(comma_op_expr.is_mod_op())
        self.assertFalse(comma_op_expr.is_div_op())
        self.assertFalse(comma_op_expr.is_and_op())
        self.assertFalse(comma_op_expr.is_or_op())
        self.assertFalse(comma_op_expr.is_bit_and_op())
        self.assertFalse(comma_op_expr.is_bit_or_op())
        self.assertFalse(comma_op_expr.is_bit_xor_op())
        self.assertFalse(comma_op_expr.is_bit_shl_op())
        self.assertFalse(comma_op_expr.is_bit_shr_op())
        self.assertFalse(comma_op_expr.is_not_op())
        self.assertFalse(comma_op_expr.is_neg_op())
        self.assertFalse(comma_op_expr.is_assign_op())
        self.assertFalse(comma_op_expr.is_address_op())
        self.assertFalse(comma_op_expr.is_deref_op())
        self.assertFalse(comma_op_expr.is_array_index_op())
        self.assertFalse(comma_op_expr.is_ternary_op())
        self.assertFalse(comma_op_expr.is_call())
        self.assertFalse(comma_op_expr.is_cast())
        self.assertFalse(comma_op_expr.is_pre_increment_op())
        self.assertFalse(comma_op_expr.is_post_increment_op())
        self.assertFalse(comma_op_expr.is_pre_decrement_op())
        self.assertFalse(comma_op_expr.is_post_decrement_op())
        self.assertFalse(comma_op_expr.is_compound_assign_op())
        self.assertFalse(comma_op_expr.is_struct_ref_op())
        self.assertFalse(comma_op_expr.is_struct_deref_op())

    def test_repr_returns_correct_repr(self):
        comma_op_expr = self.get_comma_op_expr(1, 2)
        self.assertEqual(repr(comma_op_expr), '<CommaOpExpr lhs=1 rhs=2>')

    def test_str_returns_correct_str(self):
        comma_op_expr = self.get_comma_op_expr(1, 2)
        self.assertEqual(str(comma_op_expr), '1 , 2')
