"""
    Tests for the
    :module`regression_tests.parsers.c_parser.exprs.cast_expr`
    module.
"""

from tests.parsers.c_parser import WithModuleTests


class CastExprTests(WithModuleTests):
    """Tests for `CastExpr`."""

    def test_cast_expr_is_cast(self):
        cast_expr = self.get_expr('(int) 1.5', 'int')
        self.assertTrue(cast_expr.is_cast())

    def test_cast_expr_is_no_other_expr(self):
        cast_expr = self.get_expr('(int) 1.5', 'int')
        self.assertFalse(cast_expr.is_eq_op())
        self.assertFalse(cast_expr.is_neq_op())
        self.assertFalse(cast_expr.is_gt_op())
        self.assertFalse(cast_expr.is_gt_eq_op())
        self.assertFalse(cast_expr.is_lt_op())
        self.assertFalse(cast_expr.is_lt_eq_op())
        self.assertFalse(cast_expr.is_add_op())
        self.assertFalse(cast_expr.is_sub_op())
        self.assertFalse(cast_expr.is_mul_op())
        self.assertFalse(cast_expr.is_mod_op())
        self.assertFalse(cast_expr.is_div_op())
        self.assertFalse(cast_expr.is_and_op())
        self.assertFalse(cast_expr.is_or_op())
        self.assertFalse(cast_expr.is_bit_and_op())
        self.assertFalse(cast_expr.is_bit_or_op())
        self.assertFalse(cast_expr.is_bit_xor_op())
        self.assertFalse(cast_expr.is_bit_shl_op())
        self.assertFalse(cast_expr.is_bit_shr_op())
        self.assertFalse(cast_expr.is_not_op())
        self.assertFalse(cast_expr.is_neg_op())
        self.assertFalse(cast_expr.is_assign_op())
        self.assertFalse(cast_expr.is_address_op())
        self.assertFalse(cast_expr.is_deref_op())
        self.assertFalse(cast_expr.is_array_index_op())
        self.assertFalse(cast_expr.is_comma_op())
        self.assertFalse(cast_expr.is_ternary_op())
        self.assertFalse(cast_expr.is_call())

    def test_dst_type_is_correctly_extracted(self):
        cast_expr = self.get_expr('(float) 1.5', 'int')
        self.assertTrue(cast_expr.dst_type.is_float())

    def test_op_is_correctly_extracted(self):
        cast_expr = self.get_expr('(int) 1.5', 'int')
        self.assertEqual(cast_expr.op, '1.5')

    def test_two_same_cast_exprs_are_equal(self):
        cast_expr1 = self.get_expr('(int) 1.5', 'int')
        cast_expr2 = self.get_expr('(int) 1.5', 'int')
        self.assertEqual(cast_expr1, cast_expr2)

    def test_cast_exprs_can_be_compared_to_strings(self):
        cast_expr = self.get_expr('(int) 1.5', 'int')
        self.assertEqual(cast_expr, '\t( int) 1.5\n')

    def test_two_cast_exprs_different_by_dst_type_are_not_equal(self):
        cast_expr1 = self.get_expr('(int) 1.5', 'int')
        cast_expr2 = self.get_expr('(float) 1.5', 'int')
        self.assertNotEqual(cast_expr1, cast_expr2)

    def test_two_cast_exprs_different_by_op_are_not_equal(self):
        cast_expr1 = self.get_expr('(int) 1.5', 'int')
        cast_expr2 = self.get_expr('(int) 2.5', 'int')
        self.assertNotEqual(cast_expr1, cast_expr2)

    def test_two_equal_cast_exprs_have_same_hash(self):
        cast_expr1 = self.get_expr('(int) 1.5', 'int')
        cast_expr2 = self.get_expr('(int) 1.5', 'int')
        self.assertEqual(cast_expr1, cast_expr2)
        self.assertEqual(hash(cast_expr1), hash(cast_expr2))

    def test_repr_returns_correct_repr(self):
        cast_expr = self.get_expr('(int) 1.5', 'int')
        self.assertEqual(repr(cast_expr), '<CastExpr dst_type=int op=1.5>')

    def test_str_returns_correct_str(self):
        cast_expr = self.get_expr('(int) 1.5', 'int')
        self.assertEqual(str(cast_expr), '(int) 1.5')
