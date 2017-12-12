"""
    Tests for the :module`regression_tests.parsers.c_parser.stmts.if_stmt` module.
"""

from tests.parsers.c_parser import WithModuleTests

from regression_tests.parsers.c_parser.stmts.if_stmt import IfStmt


class IfStmtTests(WithModuleTests):
    """Tests for `IfStmt`."""

    def get_if_stmt(self, code, func_name):
        """Returns the first if statement in the given code."""
        func = self.get_func("""
            void %s(void) {
                %s
            }
        """ % (func_name, code), func_name)
        return func.if_stmts[0]

    def test_if_stmt_is_if_stmt(self):
        if_stmt = self.get_if_stmt("if(1) bar();", 'foo')
        self.assertTrue(if_stmt.is_if_stmt())

    def test_if_stmt_is_no_other_kind_of_statement(self):
        if_stmt = self.get_if_stmt("if(1) bar();", 'foo')
        self.assertFalse(if_stmt.is_for_loop())
        self.assertFalse(if_stmt.is_assign())
        self.assertFalse(if_stmt.is_var_def())
        self.assertFalse(if_stmt.is_while_loop())
        self.assertFalse(if_stmt.is_return_stmt())
        self.assertFalse(if_stmt.is_empty_stmt())
        self.assertFalse(if_stmt.is_break_stmt())
        self.assertFalse(if_stmt.is_continue_stmt())
        self.assertFalse(if_stmt.is_switch_stmt())
        self.assertFalse(if_stmt.is_goto_stmt())
        self.assertFalse(if_stmt.is_do_while_loop())
        self.assertFalse(if_stmt.is_loop())

    def test_identification_returns_correct_value(self):
        if_stmt = self.get_if_stmt("if(1) bar();", 'foo')
        self.assertEqual(if_stmt.identification, 'if(1)')

    def test_correct_condition_is_extracted(self):
        if_stmt = self.get_if_stmt("if(1) bar();", 'foo')
        self.assertEqual(if_stmt.condition, '1')

    def test_if_stmt_without_else_part_does_not_have_else_part(self):
        if_stmt = self.get_if_stmt("if(1) bar();", 'foo')
        self.assertFalse(if_stmt.has_else_clause())

    def test_if_stmt_with_else_part_has_else_part(self):
        if_stmt = self.get_if_stmt("""
            if(1) bar();
            else foo();
        """, 'foo')
        self.assertTrue(if_stmt.has_else_clause())

    def test_if_stmt_is_equal_to_itself(self):
        if_stmt = self.get_if_stmt("if(1) bar();", 'foo')
        self.assertEqual(if_stmt, if_stmt)

    def test_two_different_if_stmts_are_not_equal(self):
        if_stmt1 = self.get_if_stmt("if(1) bar();", 'foo')
        if_stmt2 = self.get_if_stmt("if(1) foo();", 'foo')
        self.assertNotEqual(if_stmt1, if_stmt2)

    def test_two_if_stmts_with_same_string_representation_are_not_equal(self):
        if_stmt1 = self.get_if_stmt("if(1) foo();", 'foo')
        if_stmt2 = self.get_if_stmt("if(1) foo();", 'bar')
        self.assertNotEqual(if_stmt1, if_stmt2)

    def test_else_if_statement_is_new_if_statement_in_else_clause(self):
        parent_if_stmt = self.get_if_stmt("""
            if(1) {
                bar();
            } else if (2) {
                foo();
            }
        """, 'foo')
        child_if_stmt = IfStmt(list(parent_if_stmt._node.get_children())[2])
        self.assertEqual(child_if_stmt.condition, '2')
        self.assertFalse(child_if_stmt.has_else_clause())

    def test_repr_returns_correct_repr(self):
        if_stmt = self.get_if_stmt("if(1) foo();", 'foo')
        self.assertEqual(repr(if_stmt), '<IfStmt condition=1>')

    def test_str_returns_correct_str(self):
        if_stmt = self.get_if_stmt("if(1) foo();", 'foo')
        self.assertEqual(str(if_stmt), 'if (1)')
