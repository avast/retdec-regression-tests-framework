"""
    Tests for the :module`regression_tests.parsers.c_parser.stmts.var_def_stmt` module.
"""

from tests.parsers.c_parser import WithModuleTests


class VarDefStmtTests(WithModuleTests):
    """Tests for `VarDefStmt`."""

    def get_var_def_stmt(self, code, func_name):
        """Returns the first var_def statement in the given code."""
        func = self.get_func("""
            int %s(void) {
                %s
            }
        """ % (func_name, code), func_name)
        return func.var_def_stmts[0]

    def test_var_def_stmt_with_initializer_is_var_def_and_assign(self):
        var_def = self.get_var_def_stmt('int a = 5;', 'foo')
        self.assertTrue(var_def.is_var_def())
        self.assertTrue(var_def.is_assign())

    def test_var_def_without_initializer_is_var_def_but_not_assign(self):
        var_def = self.get_var_def_stmt('int a;', 'foo')
        self.assertTrue(var_def.is_var_def())
        self.assertFalse(var_def.is_assign())

    def test_var_def_stmt_is_no_other_kind_of_statement(self):
        var_def = self.get_var_def_stmt('int a = 5;', 'foo')
        self.assertFalse(var_def.is_for_loop())
        self.assertFalse(var_def.is_if_stmt())
        self.assertFalse(var_def.is_while_loop())
        self.assertFalse(var_def.is_return_stmt())
        self.assertFalse(var_def.is_empty_stmt())
        self.assertFalse(var_def.is_break_stmt())
        self.assertFalse(var_def.is_continue_stmt())
        self.assertFalse(var_def.is_switch_stmt())
        self.assertFalse(var_def.is_goto_stmt())
        self.assertFalse(var_def.is_do_while_loop())
        self.assertFalse(var_def.is_loop())

    def test_identification_returns_correct_value(self):
        var_def = self.get_var_def_stmt('int a = 5;', 'foo')
        self.assertEqual(var_def.identification, 'a=5')

    def test_correct_variable_is_extracted_for_definition(self):
        var_def = self.get_var_def_stmt('int a = 5;', 'foo')
        self.assertEqual(var_def.var.name, 'a')
        self.assertTrue(var_def.var.type.is_int())
        self.assertEqual(var_def.initializer, 5)

    def test_correct_variable_is_extracted_for_declaration(self):
        var_def = self.get_var_def_stmt('int a;', 'foo')
        self.assertEqual(var_def.var.name, 'a')
        self.assertTrue(var_def.var.type.is_int())
        self.assertIsNone(var_def.initializer)

    def test_lhs_raises_assertion_error_when_not_assignment(self):
        var_def = self.get_var_def_stmt('int a;', 'foo')
        with self.assertRaises(AssertionError):
            var_def.lhs

    def test_lhs_returns_correct_value(self):
        var_def = self.get_var_def_stmt('int a = 7;', 'foo')
        self.assertEqual(var_def.lhs, 'a')

    def test_rhs_raises_assertion_error_when_not_assignment(self):
        var_def = self.get_var_def_stmt('int a;', 'foo')
        with self.assertRaises(AssertionError):
            var_def.rhs

    def test_rhs_returns_correct_value(self):
        var_def = self.get_var_def_stmt('int a = 7;', 'foo')
        self.assertEqual(var_def.rhs, 7)

    def test_str_without_type_returns_correct_str_when_initializer_present(self):
        var_def = self.get_var_def_stmt('int a = 5;', 'foo')
        self.assertEqual(var_def.str_without_type(), 'a = 5')

    def test_str_without_type_returns_correct_str_when_initializer_not_present(self):
        var_def = self.get_var_def_stmt('int a;', 'foo')
        self.assertEqual(var_def.str_without_type(), 'a')

    def test_var_def_stmt_is_equal_to_itself(self):
        var_def = self.get_var_def_stmt('int a = 5;', 'foo')
        self.assertEqual(var_def, var_def)

    def test_two_different_assign_stmts_are_not_equal(self):
        var_def1 = self.get_var_def_stmt('int a = 5;', 'foo')
        var_def2 = self.get_var_def_stmt('int a = 7;', 'foo')
        self.assertNotEqual(var_def1, var_def2)

    def test_two_assign_stmts_with_same_string_representation_are_not_equal(self):
        var_def1 = self.get_var_def_stmt('int a = 5;', 'foo')
        var_def2 = self.get_var_def_stmt('int a = 5;', 'bar')
        self.assertNotEqual(var_def1, var_def2)

    def test_repr_returns_correct_repr(self):
        var_def = self.get_var_def_stmt('int a = 5;', 'foo')
        self.assertEqual(repr(var_def), '<VarDefStmt name=a type=int initializer=5>')

    def test_str_returns_correct_str_when_initializer_present(self):
        var_def = self.get_var_def_stmt('int a = 5;', 'foo')
        self.assertEqual(str(var_def), 'int a = 5')

    def test_str_returns_correct_str_when_initializer_not_present(self):
        var_def = self.get_var_def_stmt('int a;', 'foo')
        self.assertEqual(str(var_def), 'int a')
