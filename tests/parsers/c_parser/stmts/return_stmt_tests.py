"""
    Tests for the :module`regression_tests.parsers.c_parser.stmts.return_stmt` module.
"""

from tests.parsers.c_parser import WithModuleTests


class ReturnStmtTests(WithModuleTests):
    """Tests for `ReturnStmt`."""

    def get_return_stmt(self, code, func_name, return_type):
        """Returns the first return statement in the given code."""
        func = self.get_func("""
            %s %s(void) {
                %s
            }
        """ % (return_type, func_name, code), func_name)
        return func.return_stmts[0]

    def test_return_stmt_is_return_stmt(self):
        return_stmt = self.get_return_stmt("return 123;", 'foo', 'int')
        self.assertTrue(return_stmt.is_return_stmt())

    def test_return_stmt_is_no_other_kind_of_statement(self):
        return_stmt = self.get_return_stmt("return 123;", 'foo', 'int')
        self.assertFalse(return_stmt.is_for_loop())
        self.assertFalse(return_stmt.is_assign())
        self.assertFalse(return_stmt.is_if_stmt())
        self.assertFalse(return_stmt.is_var_def())
        self.assertFalse(return_stmt.is_while_loop())
        self.assertFalse(return_stmt.is_empty_stmt())
        self.assertFalse(return_stmt.is_break_stmt())
        self.assertFalse(return_stmt.is_continue_stmt())
        self.assertFalse(return_stmt.is_switch_stmt())
        self.assertFalse(return_stmt.is_goto_stmt())
        self.assertFalse(return_stmt.is_do_while_loop())
        self.assertFalse(return_stmt.is_loop())

    def test_identification_returns_correct_value(self):
        return_stmt = self.get_return_stmt("return 1 + 2;", 'foo', 'int')
        self.assertEqual(return_stmt.identification, 'return1+2')

    def test_correct_return_expr_is_extracted(self):
        return_stmt = self.get_return_stmt("return 1 + 2;", 'foo', 'int')
        self.assertTrue(return_stmt.return_expr.is_add_op())
        self.assertEqual(return_stmt.return_expr.lhs, 1)
        self.assertEqual(return_stmt.return_expr.rhs, 2)

    def test_return_expr_returns_none_if_nothing_returned(self):
        return_stmt = self.get_return_stmt("return;", 'foo', 'void')
        self.assertIsNone(return_stmt.return_expr)

    def test_returns_something_is_true_if_something_is_returned(self):
        return_stmt = self.get_return_stmt("return 1 + 2;", 'foo', 'int')
        self.assertTrue(return_stmt.returns_something())

    def test_returns_something_is_false_if_nothing_is_returned(self):
        return_stmt = self.get_return_stmt("return;", 'foo', 'void')
        self.assertFalse(return_stmt.returns_something())

    def test_return_stmt_is_equal_to_itself(self):
        return_stmt = self.get_return_stmt("return 123;", 'foo', 'int')
        self.assertEqual(return_stmt, return_stmt)

    def test_two_different_return_stmts_are_not_equal(self):
        return_stmt1 = self.get_return_stmt("return 123;", 'foo', 'int')
        return_stmt2 = self.get_return_stmt("return 321;", 'foo', 'int')
        self.assertNotEqual(return_stmt1, return_stmt2)

    def test_two_return_stmts_with_same_string_representation_are_not_equal(self):
        return_stmt1 = self.get_return_stmt("return 123;", 'foo', 'int')
        return_stmt2 = self.get_return_stmt("return 123;", 'bar', 'int')
        self.assertNotEqual(return_stmt1, return_stmt2)

    def test_repr_returns_correct_repr(self):
        return_stmt = self.get_return_stmt("return 123;", 'foo', 'int')
        self.assertEqual(repr(return_stmt), '<ReturnStmt return_expr=123>')

    def test_str_returns_correct_str(self):
        return_stmt = self.get_return_stmt("return 123;", 'foo', 'int')
        self.assertEqual(str(return_stmt), 'return 123')
