"""
    Tests for the :module`regression_tests.parsers.c_parser.stmts.goto_stmt` module.
"""

from tests.parsers.c_parser import WithModuleTests


class GotoStmtTests(WithModuleTests):
    """Tests for `GotoStmt`."""

    def get_goto_stmt(self, code, func_name):
        """Returns the first goto statement in the given code."""
        func = self.get_func("""
            void %s(void) {
                %s
            }
        """ % (func_name, code), func_name)
        return func.goto_stmts[0]

    def test_goto_stmt_is_goto_stmt(self):
        goto_stmt = self.get_goto_stmt("goto abc; abc: ;", 'foo')
        self.assertTrue(goto_stmt.is_goto_stmt())

    def test_goto_stmt_is_no_other_kind_of_statement(self):
        goto_stmt = self.get_goto_stmt("goto abc; abc: ;", 'foo')
        self.assertFalse(goto_stmt.is_for_loop())
        self.assertFalse(goto_stmt.is_assign())
        self.assertFalse(goto_stmt.is_if_stmt())
        self.assertFalse(goto_stmt.is_var_def())
        self.assertFalse(goto_stmt.is_while_loop())
        self.assertFalse(goto_stmt.is_empty_stmt())
        self.assertFalse(goto_stmt.is_break_stmt())
        self.assertFalse(goto_stmt.is_continue_stmt())
        self.assertFalse(goto_stmt.is_switch_stmt())
        self.assertFalse(goto_stmt.is_do_while_loop())
        self.assertFalse(goto_stmt.is_loop())

    def test_identification_returns_correct_value(self):
        goto_stmt = self.get_goto_stmt("goto abc; abc: ;", 'foo')
        self.assertEqual(goto_stmt.identification, 'gotoabc')

    def test_correct_goto_expr_is_extracted(self):
        goto_stmt = self.get_goto_stmt("goto abc; abc: ;", 'foo')
        self.assertEqual(goto_stmt.target, 'abc')

    def test_goto_stmt_is_equal_to_itself(self):
        goto_stmt = self.get_goto_stmt("goto abc; abc: ;", 'foo')
        self.assertEqual(goto_stmt, goto_stmt)

    def test_two_different_goto_stmts_are_not_equal(self):
        goto_stmt1 = self.get_goto_stmt("goto abc; abc: ;", 'foo')
        goto_stmt2 = self.get_goto_stmt("goto xyz; xyz: ;", 'foo')
        self.assertNotEqual(goto_stmt1, goto_stmt2)

    def test_two_goto_stmts_with_same_string_representation_are_not_equal(self):
        goto_stmt1 = self.get_goto_stmt("goto abc; abc: ;", 'foo')
        goto_stmt2 = self.get_goto_stmt("goto abc; abc: ;", 'bar')
        self.assertNotEqual(goto_stmt1, goto_stmt2)

    def test_repr_gotos_correct_repr(self):
        goto_stmt = self.get_goto_stmt("goto abc; abc: ;", 'foo')
        self.assertEqual(repr(goto_stmt), '<GotoStmt target=abc>')

    def test_str_gotos_correct_str(self):
        goto_stmt = self.get_goto_stmt("goto abc; abc: ;", 'foo')
        self.assertEqual(str(goto_stmt), 'goto abc')


class LabelTests(WithModuleTests):
    """Tests for `Label`."""

    def get_label(self, code, func_name):
        """Returns the first label in the given code."""
        func = self.get_func("""
            void %s(void) {
                %s
            }
        """ % (func_name, code), func_name)
        return func.labels[0]

    def test_identification_returns_correct_value(self):
        label = self.get_label("abc: foo();", 'foo')
        self.assertEqual(label.identification, 'abc')

    def test_correct_label_expr_is_extracted(self):
        label = self.get_label("abc: foo();", 'foo')
        self.assertEqual(label.name, 'abc')

    def test_label_is_equal_to_itself(self):
        label = self.get_label("abc: foo();", 'foo')
        self.assertEqual(label, label)

    def test_two_different_labels_are_not_equal(self):
        label1 = self.get_label("abc: foo();", 'foo')
        label2 = self.get_label("xyz: foo();", 'foo')
        self.assertNotEqual(label1, label2)

    def test_two_labels_with_same_string_representation_are_not_equal(self):
        label1 = self.get_label("abc: foo();", 'foo')
        label2 = self.get_label("abc: foo();", 'bar')
        self.assertNotEqual(label1, label2)

    def test_repr_labels_correct_repr(self):
        label = self.get_label("abc: foo();", 'foo')
        self.assertEqual(repr(label), '<Label name=abc>')

    def test_str_labels_correct_str(self):
        label = self.get_label("abc: foo();", 'foo')
        self.assertEqual(str(label), 'abc:')
