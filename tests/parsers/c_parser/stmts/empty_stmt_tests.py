"""
    Tests for the :module`regression_tests.parsers.c_parser.stmts.empty_stmt` module.
"""

from tests.parsers.c_parser import WithModuleTests


class EmptyStmtTests(WithModuleTests):
    """Tests for `EmptyStmt`."""

    def get_empty_stmt(self, code, func_name):
        """Returns the first empty statement in the given code."""
        func = self.get_func("""
            void %s(void) {
                %s
            }
        """ % (func_name, code), func_name)
        return func.empty_stmts[0]

    def test_empty_stmt_is_empty_stmt(self):
        empty_stmt = self.get_empty_stmt(";", 'foo')
        self.assertTrue(empty_stmt.is_empty_stmt())

    def test_empty_stmt_is_no_other_kind_of_statement(self):
        empty_stmt = self.get_empty_stmt(";", 'foo')
        self.assertFalse(empty_stmt.is_for_loop())
        self.assertFalse(empty_stmt.is_assign())
        self.assertFalse(empty_stmt.is_if_stmt())
        self.assertFalse(empty_stmt.is_var_def())
        self.assertFalse(empty_stmt.is_while_loop())
        self.assertFalse(empty_stmt.is_return_stmt())
        self.assertFalse(empty_stmt.is_break_stmt())
        self.assertFalse(empty_stmt.is_continue_stmt())
        self.assertFalse(empty_stmt.is_switch_stmt())
        self.assertFalse(empty_stmt.is_goto_stmt())
        self.assertFalse(empty_stmt.is_do_while_loop())
        self.assertFalse(empty_stmt.is_loop())

    def test_empty_stmt_is_equal_to_itself(self):
        empty_stmt = self.get_empty_stmt(";", 'foo')
        self.assertEqual(empty_stmt, empty_stmt)

    def test_two_different_empty_stmts_are_not_equal(self):
        empty_stmt1 = self.get_empty_stmt(";", 'foo')
        empty_stmt2 = self.get_empty_stmt(";", 'bar')
        self.assertNotEqual(empty_stmt1, empty_stmt2)

    def test_repr_returns_correct_repr(self):
        empty_stmt = self.get_empty_stmt(";", 'foo')
        self.assertEqual(repr(empty_stmt), '<EmptyStmt>')

    def test_str_returns_correct_str(self):
        empty_stmt = self.get_empty_stmt(";", 'foo')
        self.assertEqual(str(empty_stmt), '')
