"""
    Tests for the
    :module`regression_tests.parsers.c_parser.exprs.ternary_op_expr`
    module.
"""

from tests.parsers.c_parser import WithModuleTests


class TernaryOpExprTests(WithModuleTests):
    """Tests for `TernaryOpExpr`."""

    def test_ternary_op_expr_is_ternary_op(self):
        ternary_op_expr = self.get_expr('1 ? 2 : 3', 'int')
        self.assertTrue(ternary_op_expr.is_ternary_op())

    def test_ternary_op_expr_is_no_other_expr(self):
        ternary_op_expr = self.get_expr('1 ? 2 : 3', 'int')
        self.assertFalse(ternary_op_expr.is_eq_op())
        self.assertFalse(ternary_op_expr.is_neq_op())
        self.assertFalse(ternary_op_expr.is_gt_op())
        self.assertFalse(ternary_op_expr.is_gt_eq_op())
        self.assertFalse(ternary_op_expr.is_lt_op())
        self.assertFalse(ternary_op_expr.is_lt_eq_op())
        self.assertFalse(ternary_op_expr.is_add_op())
        self.assertFalse(ternary_op_expr.is_sub_op())
        self.assertFalse(ternary_op_expr.is_mul_op())
        self.assertFalse(ternary_op_expr.is_mod_op())
        self.assertFalse(ternary_op_expr.is_div_op())
        self.assertFalse(ternary_op_expr.is_and_op())
        self.assertFalse(ternary_op_expr.is_or_op())
        self.assertFalse(ternary_op_expr.is_bit_and_op())
        self.assertFalse(ternary_op_expr.is_bit_or_op())
        self.assertFalse(ternary_op_expr.is_bit_xor_op())
        self.assertFalse(ternary_op_expr.is_bit_shl_op())
        self.assertFalse(ternary_op_expr.is_bit_shr_op())
        self.assertFalse(ternary_op_expr.is_not_op())
        self.assertFalse(ternary_op_expr.is_neg_op())
        self.assertFalse(ternary_op_expr.is_assign_op())
        self.assertFalse(ternary_op_expr.is_address_op())
        self.assertFalse(ternary_op_expr.is_deref_op())
        self.assertFalse(ternary_op_expr.is_array_index_op())
        self.assertFalse(ternary_op_expr.is_comma_op())

    def test_cond_is_correctly_extracted(self):
        ternary_op_expr = self.get_expr('1 ? 2 : 3', 'int')
        self.assertEqual(ternary_op_expr.cond, '1')

    def test_true_value_is_correctly_extracted(self):
        ternary_op_expr = self.get_expr('1 ? 2 : 3', 'int')
        self.assertEqual(ternary_op_expr.true_value, '2')

    def test_false_value_is_correctly_extracted(self):
        ternary_op_expr = self.get_expr('1 ? 2 : 3', 'int')
        self.assertEqual(ternary_op_expr.false_value, '3')

    def test_two_same_ternary_op_exprs_are_equal(self):
        ternary_op_expr1 = self.get_expr('1 ? 2 : 3', 'int')
        ternary_op_expr2 = self.get_expr('1 ? 2 : 3', 'int')
        self.assertEqual(ternary_op_expr1, ternary_op_expr2)

    def test_ternary_op_exprs_can_be_compared_to_strings(self):
        ternary_op_expr = self.get_expr('1 ? 2 : 3', 'int')
        self.assertEqual(ternary_op_expr, '1 ? 2\t : 3\n ')

    def test_two_different_ternary_op_exprs_are_not_equal(self):
        ternary_op_expr1 = self.get_expr('1 ? 2 : 3', 'int')
        ternary_op_expr2 = self.get_expr('2 ? 3 : 1', 'int')
        self.assertNotEqual(ternary_op_expr1, ternary_op_expr2)

    def test_two_equal_ternary_op_exprs_have_same_hash(self):
        ternary_op_expr1 = self.get_expr('1 ? 2 : 3', 'int')
        ternary_op_expr2 = self.get_expr('1 ? 2 : 3', 'int')
        self.assertEqual(ternary_op_expr1, ternary_op_expr2)
        self.assertEqual(hash(ternary_op_expr1), hash(ternary_op_expr2))

    def test_repr_returns_correct_repr(self):
        ternary_op_expr = self.get_expr('1 ? 2 : 3', 'int')
        self.assertEqual(repr(ternary_op_expr), '<TernaryOpExpr cond=1 true_value=2 false_value=3>')

    def test_str_returns_correct_str(self):
        ternary_op_expr = self.get_expr('1 ? 2 : 3', 'int')
        self.assertEqual(str(ternary_op_expr), '1 ? 2 : 3')
