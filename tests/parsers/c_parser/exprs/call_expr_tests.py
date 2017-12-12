"""
    Tests for the
    :module`regression_tests.parsers.c_parser.exprs.call_expr`
    module.
"""

from tests.parsers.c_parser import WithModuleTests


class CallExprTests(WithModuleTests):
    """Tests for `CallExpr`."""

    def test_call_expr_is_call(self):
        call_expr = self.get_expr('foo()', 'int')
        self.assertTrue(call_expr.is_call())

    def test_call_expr_is_no_other_expr(self):
        call_expr = self.get_expr('foo()', 'int')
        self.assertFalse(call_expr.is_eq_op())
        self.assertFalse(call_expr.is_neq_op())
        self.assertFalse(call_expr.is_gt_op())
        self.assertFalse(call_expr.is_gt_eq_op())
        self.assertFalse(call_expr.is_lt_op())
        self.assertFalse(call_expr.is_lt_eq_op())
        self.assertFalse(call_expr.is_add_op())
        self.assertFalse(call_expr.is_sub_op())
        self.assertFalse(call_expr.is_mul_op())
        self.assertFalse(call_expr.is_mod_op())
        self.assertFalse(call_expr.is_div_op())
        self.assertFalse(call_expr.is_and_op())
        self.assertFalse(call_expr.is_or_op())
        self.assertFalse(call_expr.is_bit_and_op())
        self.assertFalse(call_expr.is_bit_or_op())
        self.assertFalse(call_expr.is_bit_xor_op())
        self.assertFalse(call_expr.is_bit_shl_op())
        self.assertFalse(call_expr.is_bit_shr_op())
        self.assertFalse(call_expr.is_not_op())
        self.assertFalse(call_expr.is_neg_op())
        self.assertFalse(call_expr.is_assign_op())
        self.assertFalse(call_expr.is_address_op())
        self.assertFalse(call_expr.is_deref_op())
        self.assertFalse(call_expr.is_array_index_op())
        self.assertFalse(call_expr.is_comma_op())
        self.assertFalse(call_expr.is_ternary_op())
        self.assertFalse(call_expr.is_cast())

    def test_name_is_correctly_extracted(self):
        call_expr = self.get_expr('foo()', 'int')
        self.assertEqual(call_expr.name, 'foo')

    def test_has_args_returns_false_for_call_without_arguments(self):
        call_expr = self.get_expr('foo()', 'int')
        self.assertFalse(call_expr.has_args())

    def test_has_args_returns_true_for_call_with_arguments(self):
        call_expr = self.get_expr('foo(1, 2)', 'int')
        self.assertTrue(call_expr.has_args())

    def test_args_are_correctly_extracted(self):
        call_expr = self.get_expr('foo(1, 2)', 'int')
        self.assertEqual(len(call_expr.args), 2)
        self.assertEqual(call_expr.args[0], '1')
        self.assertEqual(call_expr.args[1], '2')

    def test_two_same_call_exprs_are_equal(self):
        call_expr1 = self.get_expr('foo(1, 2)', 'int')
        call_expr2 = self.get_expr('foo(1, 2)', 'int')
        self.assertEqual(call_expr1, call_expr2)

    def test_call_exprs_can_be_compared_to_strings(self):
        call_expr = self.get_expr('foo(1, 2)', 'int')
        self.assertEqual(call_expr, '\nfoo(1, 2)\t')

    def test_two_call_exprs_different_by_name_are_not_equal(self):
        call_expr1 = self.get_expr('foo(1, 2)', 'int')
        call_expr2 = self.get_expr('bar(1, 2)', 'int')
        self.assertNotEqual(call_expr1, call_expr2)

    def test_two_call_exprs_different_by_args_are_not_equal(self):
        call_expr1 = self.get_expr('foo(1, 2)', 'int')
        call_expr2 = self.get_expr('foo(1)', 'int')
        self.assertNotEqual(call_expr1, call_expr2)

    def test_two_equal_call_exprs_have_same_hash(self):
        call_expr1 = self.get_expr('foo(1, 2)', 'int')
        call_expr2 = self.get_expr('foo(1, 2)', 'int')
        self.assertEqual(call_expr1, call_expr2)
        self.assertEqual(hash(call_expr1), hash(call_expr2))

    def test_repr_returns_correct_repr(self):
        call_expr = self.get_expr('foo(1, 2)', 'int')
        self.assertEqual(repr(call_expr), '<CallExpr name=foo args=(1, 2)>')

    def test_repr_returns_correct_repr_for_call_without_args(self):
        call_expr = self.get_expr('foo()', 'int')
        self.assertEqual(repr(call_expr), '<CallExpr name=foo args=()>')

    def test_str_returns_correct_str(self):
        call_expr = self.get_expr('foo(1, 2)', 'int')
        self.assertEqual(str(call_expr), 'foo(1, 2)')

    def test_str_returns_correct_str_for_call_without_args(self):
        call_expr = self.get_expr('foo()', 'int')
        self.assertEqual(str(call_expr), 'foo()')
