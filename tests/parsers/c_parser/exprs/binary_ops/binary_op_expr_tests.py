"""
    Tests for the
    :module`regression_tests.parsers.c_parser.exprs.binary_ops.binary_op_expr`
    module.
"""

from tests.parsers.c_parser import WithModuleTests


class BinaryOpExprTests(WithModuleTests):
    """Tests for `BinaryOpExpr`."""

    def test_lhs_is_correctly_extracted(self):
        binary_op_expr = self.get_expr('a + 2', 'int')
        self.assertEqual(binary_op_expr.lhs, 'a')

    def test_rhs_is_correctly_extracted(self):
        binary_op_expr = self.get_expr('a + 2', 'int')
        self.assertEqual(binary_op_expr.rhs, '2')

    def test_two_same_binary_op_exprs_are_equal(self):
        binary_op_expr1 = self.get_expr('a = 2', 'int')
        binary_op_expr2 = self.get_expr('a = 2', 'int')
        self.assertEqual(binary_op_expr1, binary_op_expr2)

    def test_binary_op_exprs_can_be_compared_to_strings(self):
        binary_op_expr = self.get_expr('a = 2', 'int')
        self.assertEqual(binary_op_expr, 'a =\t2\n')

    def test_binary_op_expr_is_not_equal_to_other_binary_op_with_same_operands(self):
        binary_op_expr1 = self.get_expr('a + 2', 'int')
        binary_op_expr2 = self.get_expr('a - 2', 'int')
        self.assertNotEqual(binary_op_expr1, binary_op_expr2)

    def test_two_different_binary_op_exprs_are_not_equal(self):
        binary_op_expr1 = self.get_expr('a = 2', 'int')
        binary_op_expr2 = self.get_expr('2 >> 3', 'int')
        self.assertNotEqual(binary_op_expr1, binary_op_expr2)

    def test_two_same_binary_op_exprs_with_different_operands_are_not_equal(self):
        binary_op_expr1 = self.get_expr('1 + 2', 'int')
        binary_op_expr2 = self.get_expr('3 + 2', 'int')
        self.assertNotEqual(binary_op_expr1, binary_op_expr2)

    def test_two_equal_binary_op_exprs_have_same_hash(self):
        binary_op_expr1 = self.get_expr('a = 2', 'int')
        binary_op_expr2 = self.get_expr('a = 2', 'int')
        self.assertEqual(binary_op_expr1, binary_op_expr2)
        self.assertEqual(hash(binary_op_expr1), hash(binary_op_expr1))
