"""
    Tests for the :module`regression_tests.parsers.c_parser.stmts.break_stmt` module.
"""

from tests.parsers.c_parser import WithModuleTests


class BreakStmtTests(WithModuleTests):
    """Tests for `BreakStmt`."""

    def get_break_stmt(self, code, func_name):
        """Returns the first break statement in the given code."""
        func = self.get_func("""
            void %s(void) {
                while(1) {
                    %s
                }
            }
        """ % (func_name, code), func_name)
        return func.while_loops[0].break_stmts[0]

    def test_break_stmt_is_break_stmt(self):
        break_stmt = self.get_break_stmt("break;", 'foo')
        self.assertTrue(break_stmt.is_break_stmt())

    def test_break_stmt_is_no_other_kind_of_statement(self):
        break_stmt = self.get_break_stmt("break;", 'foo')
        self.assertFalse(break_stmt.is_for_loop())
        self.assertFalse(break_stmt.is_assign())
        self.assertFalse(break_stmt.is_if_stmt())
        self.assertFalse(break_stmt.is_var_def())
        self.assertFalse(break_stmt.is_while_loop())
        self.assertFalse(break_stmt.is_return_stmt())
        self.assertFalse(break_stmt.is_empty_stmt())
        self.assertFalse(break_stmt.is_continue_stmt())
        self.assertFalse(break_stmt.is_switch_stmt())
        self.assertFalse(break_stmt.is_goto_stmt())
        self.assertFalse(break_stmt.is_do_while_loop())
        self.assertFalse(break_stmt.is_loop())

    def test_break_stmt_is_equal_to_itself(self):
        break_stmt = self.get_break_stmt("break;", 'foo')
        self.assertEqual(break_stmt, break_stmt)

    def test_two_different_break_stmts_are_not_equal(self):
        break_stmt1 = self.get_break_stmt("break;", 'foo')
        break_stmt2 = self.get_break_stmt("break;", 'bar')
        self.assertNotEqual(break_stmt1, break_stmt2)

    def test_repr_returns_correct_repr(self):
        break_stmt = self.get_break_stmt("break;", 'foo')
        self.assertEqual(repr(break_stmt), '<BreakStmt>')
