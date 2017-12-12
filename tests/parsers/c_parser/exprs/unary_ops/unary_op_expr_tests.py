"""
    Tests for the
    :module`regression_tests.parsers.c_parser.exprs.unary_ops.binary_op_expr`
    module.
"""

from tests.parsers.c_parser import WithModuleTests


class UnaryOpExprTests(WithModuleTests):
    """Tests for `UnaryOpExpr`."""

    def test_op_is_correctly_extracted(self):
        unary_op_expr = self.get_expr('&a', 'int')
        self.assertEqual(unary_op_expr.op, 'a')

    def test_two_same_unary_op_exprs_are_equal(self):
        unary_op_expr1 = self.get_expr('&a', 'int')
        unary_op_expr2 = self.get_expr('&a', 'int')
        self.assertEqual(unary_op_expr1, unary_op_expr2)

    def test_unary_op_exprs_can_be_compared_to_strings(self):
        unary_op_expr = self.get_expr('-1', 'int')
        self.assertEqual(unary_op_expr, ' -\t1\n')

    def test_unary_op_expr_is_not_equal_to_other_unary_op_with_same_operand(self):
        unary_op_expr1 = self.get_expr('&a', 'int')
        unary_op_expr2 = self.get_expr('!a', 'int')
        self.assertNotEqual(unary_op_expr1, unary_op_expr2)

    def test_two_different_unary_op_exprs_are_not_equal(self):
        unary_op_expr1 = self.get_expr('&a', 'int')
        unary_op_expr2 = self.get_expr('-1', 'int')
        self.assertNotEqual(unary_op_expr1, unary_op_expr2)

    def test_two_same_unary_op_exprs_with_different_operand_are_not_equal(self):
        unary_op_expr1 = self.get_expr('-1', 'int')
        unary_op_expr2 = self.get_expr('-2', 'int')
        self.assertNotEqual(unary_op_expr1, unary_op_expr2)

    def test_two_equal_unary_op_exprs_have_same_hash(self):
        unary_op_expr1 = self.get_expr('&a', 'int')
        unary_op_expr2 = self.get_expr('&a', 'int')
        self.assertEqual(unary_op_expr1, unary_op_expr2)
        self.assertEqual(hash(unary_op_expr1), hash(unary_op_expr2))
