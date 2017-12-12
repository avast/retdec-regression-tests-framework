"""
    Tests for the :module`regression_tests.parsers.c_parser.stmts.continue_stmt` module.
"""

from tests.parsers.c_parser import WithModuleTests


class ContinueStmtTests(WithModuleTests):
    """Tests for `ContinueStmt`."""

    def get_continue_stmt(self, code, func_name):
        """Returns the first continue statement in the given code."""
        func = self.get_func("""
            void %s(void) {
                while(1) {
                    %s
                }
            }
        """ % (func_name, code), func_name)
        return func.while_loops[0].continue_stmts[0]

    def test_continue_stmt_is_continue_stmt(self):
        continue_stmt = self.get_continue_stmt("continue;", 'foo')
        self.assertTrue(continue_stmt.is_continue_stmt())

    def test_continue_stmt_is_no_other_kind_of_statement(self):
        continue_stmt = self.get_continue_stmt("continue;", 'foo')
        self.assertFalse(continue_stmt.is_for_loop())
        self.assertFalse(continue_stmt.is_assign())
        self.assertFalse(continue_stmt.is_if_stmt())
        self.assertFalse(continue_stmt.is_var_def())
        self.assertFalse(continue_stmt.is_while_loop())
        self.assertFalse(continue_stmt.is_return_stmt())
        self.assertFalse(continue_stmt.is_empty_stmt())
        self.assertFalse(continue_stmt.is_break_stmt())
        self.assertFalse(continue_stmt.is_switch_stmt())
        self.assertFalse(continue_stmt.is_goto_stmt())
        self.assertFalse(continue_stmt.is_do_while_loop())
        self.assertFalse(continue_stmt.is_loop())

    def test_continue_stmt_is_equal_to_itself(self):
        continue_stmt = self.get_continue_stmt("continue;", 'foo')
        self.assertEqual(continue_stmt, continue_stmt)

    def test_two_different_continue_stmts_are_not_equal(self):
        continue_stmt1 = self.get_continue_stmt("continue;", 'foo')
        continue_stmt2 = self.get_continue_stmt("continue;", 'bar')
        self.assertNotEqual(continue_stmt1, continue_stmt2)

    def test_repr_returns_correct_repr(self):
        continue_stmt = self.get_continue_stmt("continue;", 'foo')
        self.assertEqual(repr(continue_stmt), '<ContinueStmt>')
