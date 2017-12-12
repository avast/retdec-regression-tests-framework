"""
    Tests for the :module`regression_tests.parsers.c_parser.stmts.switch_stmt` module.
"""

from textwrap import dedent

from tests.parsers.c_parser import WithModuleTests

from regression_tests.parsers.c_parser.stmts.switch_stmt import Case
from regression_tests.parsers.c_parser.stmts.switch_stmt import DefaultCase


class SwitchStmtTests(WithModuleTests):
    """Tests for `SwitchStmt`."""

    def get_switch_stmt(self, code, func_name):
        """Returns the first switch statement in the given code."""
        func = self.get_func("""
            int %s(void) {
                %s
            }
        """ % (func_name, code), func_name)
        return func.switch_stmts[0]

    def test_switch_stmt_is_switch_stmt(self):
        switch_stmt = self.get_switch_stmt("int a; switch(a) { case 1: break; }", 'foo')
        self.assertTrue(switch_stmt.is_switch_stmt())

    def test_switch_stmt_is_no_other_kind_of_statement(self):
        switch_stmt = self.get_switch_stmt("int a; switch(a) { case 1: break; }", 'foo')
        self.assertFalse(switch_stmt.is_for_loop())
        self.assertFalse(switch_stmt.is_assign())
        self.assertFalse(switch_stmt.is_if_stmt())
        self.assertFalse(switch_stmt.is_var_def())
        self.assertFalse(switch_stmt.is_while_loop())
        self.assertFalse(switch_stmt.is_return_stmt())
        self.assertFalse(switch_stmt.is_empty_stmt())
        self.assertFalse(switch_stmt.is_break_stmt())
        self.assertFalse(switch_stmt.is_continue_stmt())
        self.assertFalse(switch_stmt.is_goto_stmt())
        self.assertFalse(switch_stmt.is_do_while_loop())
        self.assertFalse(switch_stmt.is_loop())

    def test_identification_returns_correct_value(self):
        switch_stmt = self.get_switch_stmt("""
            int a;
            switch(a) {
                case 1: break;
            }
        """, 'func')
        self.assertEqual(switch_stmt.identification, 'switch(a){case1}')

    def test_switch_expr_is_correctly_extracted_when_int(self):
        switch_stmt = self.get_switch_stmt("""
            int a;
            switch(a) {}
        """, 'func')
        self.assertEqual(switch_stmt.switch_expr, 'a')

    def test_switch_expr_is_correctly_extracted_when_char(self):
        switch_stmt = self.get_switch_stmt("""
            char c;
            switch(c) {}
        """, 'func')
        self.assertEqual(switch_stmt.switch_expr, 'c')

    def test_has_cases_returns_false_for_switch_with_no_cases(self):
        switch_stmt = self.get_switch_stmt("""
            int a;
            switch(a) {}
        """, 'func')
        self.assertFalse(switch_stmt.has_cases())

    def test_has_cases_returns_true_for_switch_with_case(self):
        switch_stmt = self.get_switch_stmt("""
            int a;
            switch(a) {
                case 1: break;
            }
        """, 'func')
        self.assertTrue(switch_stmt.has_cases())

    def test_all_cases_are_found(self):
        switch_stmt = self.get_switch_stmt("""
            int a;
            switch(a) {
                case 1:
                    ;
                case 12:
                    foo();
                case 5:
                    break;
            }
        """, 'func')
        self.assertEqual(len(switch_stmt.cases), 3)
        self.assertEqual(switch_stmt.cases[0].condition, 1)
        self.assertTrue(isinstance(switch_stmt.cases[0], Case))
        self.assertEqual(switch_stmt.cases[1].condition, 12)
        self.assertTrue(isinstance(switch_stmt.cases[1], Case))
        self.assertEqual(switch_stmt.cases[2].condition, 5)
        self.assertTrue(isinstance(switch_stmt.cases[2], Case))

    def test_cases_of_nested_switch_are_not_considered_cases_of_enclosing_switch(self):
        func = self.get_func("""
            void func() {
                int a, b;
                char c;

                switch(a) {
                    case 1:
                        ;
                    switch(c) {
                        case 'x':
                            bar();
                    }
                    case 5:
                        break;
                }
            }
        """, 'func')
        switch = func.switch_stmts[0]
        nested_switch = func.switch_stmts[1]
        self.assertEqual(len(switch.cases), 2)
        self.assertEqual(switch.cases[0].condition, 1)
        self.assertEqual(switch.cases[1].condition, 5)
        self.assertEqual(len(nested_switch.cases), 1)
        self.assertEqual(nested_switch.cases[0].condition, 'x')

    def test_has_default_case_returns_false_for_switch_with_no_default_case(self):
        switch_stmt = self.get_switch_stmt("""
            int a;
            switch(a) {}
        """, 'func')
        self.assertFalse(switch_stmt.has_default_case())

    def test_has_default_case_returns_true_for_switch_with_default_case(self):
        switch_stmt = self.get_switch_stmt("""
            int a;
            switch(a) {
                default: break;
            }
        """, 'func')
        self.assertTrue(switch_stmt.has_default_case())

    def test_default_is_found(self):
        switch_stmt = self.get_switch_stmt("""
            char c;
            switch(c) {
                default: break;
            }
        """, 'func')
        self.assertTrue(isinstance(switch_stmt.default_case, DefaultCase))

    def test_default_case_of_nested_switch_is_not_considered_default_case_of_enclosing_switch(self):
        func = self.get_func("""
            void func() {
                int a, b;

                switch(a) {
                    case 1:
                        ;
                    switch(b) {
                        default:
                            bar();
                    }
                }
            }
        """, 'func')
        switch = func.switch_stmts[0]
        nested_switch = func.switch_stmts[1]
        self.assertFalse(switch.has_default_case())
        self.assertTrue(nested_switch.has_default_case())

    def test_switch_stmt_is_equal_to_itself(self):
        switch_stmt = self.get_switch_stmt("int a; switch(a) { case 1: break; }", 'foo')
        self.assertEqual(switch_stmt, switch_stmt)

    def test_two_different_switch_stmts_are_not_equal(self):
        switch_stmt1 = self.get_switch_stmt("int a; switch(a) { case 1: break; }", 'foo')
        switch_stmt2 = self.get_switch_stmt("char c; switch(c) { case 'a': break; }", 'foo')
        self.assertNotEqual(switch_stmt1, switch_stmt2)

    def test_repr_returns_correct_repr(self):
        switch_stmt = self.get_switch_stmt("""
                int a;
                switch(a) {
                    case 1:
                        ;
                    case 5:
                        break;
                }
        """, 'func')
        self.assertEqual(repr(switch_stmt), '<SwitchStmt switch_expr=a cases=2 has_default_case=False>')

    def test_str_returns_correct_str(self):
        switch_stmt = self.get_switch_stmt("""
            int a;
            switch(a) {
                case 1:
                    ;
                case 5:
                    break;
                default:
                    foo();
            }
        """, 'func')
        self.assertEqual(
            str(switch_stmt),
            dedent("""\
                switch(a) {
                    case 1
                    case 5
                    default
                }""")
        )


class CaseTests(WithModuleTests):
    """Tests for `Case`."""

    def get_case(self, code, func_name):
        """Returns the first case in the given switch."""
        func = self.get_func("""
            void %s(void) {
                %s
            }
        """ % (func_name, code), func_name)
        switch = func.switch_stmts[0]
        return switch.cases[0]

    def test_correct_condition_is_extracted_when_using_int_switch_expr(self):
        case = self.get_case("int a; switch(a) { case 1: break; }", 'foo')
        self.assertEqual(case.condition, '1')

    def test_correct_condition_is_extracted_when_using_char_switch_expr(self):
        case = self.get_case("{char c; switch(c) { case 'a': break; }", 'foo')
        self.assertEqual(case.condition, 'a')

    def test_case_is_equal_to_itself(self):
        case = self.get_case("int a; switch(a) { case 1: break; }", 'foo')
        self.assertEqual(case, case)

    def test_two_cases_with_same_string_representation_are_not_equal(self):
        case1 = self.get_case("int a; switch(a) { case 1: break; }", 'foo')
        case2 = self.get_case("int a; switch(a) { case 1: break; }", 'bar')
        self.assertNotEqual(case1, case2)

    def test_two_different_cases_are_not_equal(self):
        case1 = self.get_case("int a; switch(a) { case 1: break; }", 'foo')
        case2 = self.get_case("int a; switch(a) { case 2: break; }", 'foo')
        self.assertNotEqual(case1, case2)

    def test_repr_returns_correct_repr(self):
        case = self.get_case("int a; switch(a) { case 1: break; }", 'foo')
        self.assertEqual(repr(case), '<Case>')

    def test_str_returns_correct_str_when_using_int_switch_expr(self):
        case = self.get_case("int a; switch(a) { case 1: break; }", 'foo')
        self.assertEqual(str(case), 'case 1')

    def test_str_returns_correct_str_when_using_char_switch_expr(self):
        case = self.get_case("char c; switch(c) { case 'a': break; }", 'foo')
        self.assertEqual(str(case), 'case a')


class DefaultCaseTests(WithModuleTests):
    """Tests for `DefaultCase`."""

    def get_default_case(self, code, func_name):
        """Returns the default case in the given switch."""
        func = self.get_func("""
            void %s(void) {
                %s
            }
        """ % (func_name, code), func_name)
        switch = func.switch_stmts[0]
        return switch.default_case

    def test_default_case_is_equal_to_itself(self):
        default_case = self.get_default_case("int a; switch(a) { default: break; }", 'foo')
        self.assertEqual(default_case, default_case)

    def test_two_default_cases_with_same_string_representation_are_not_equal(self):
        default_case1 = self.get_default_case("int a; switch(a) { default: break; }", 'foo')
        default_case2 = self.get_default_case("int a; switch(a) { default: break; }", 'bar')
        self.assertNotEqual(default_case1, default_case2)

    def test_two_different_default_cases_are_not_equal(self):
        default_case1 = self.get_default_case("int a; switch(a) { default: break; }", 'foo')
        default_case2 = self.get_default_case("int a; switch(a) { default: foo(); }", 'foo')
        self.assertNotEqual(default_case1, default_case2)

    def test_repr_returns_correct_repr(self):
        default_case = self.get_default_case("int a; switch(a) { default: break; }", 'foo')
        self.assertEqual(repr(default_case), '<DefaultCase>')

    def test_str_returns_correct_str(self):
        default_case = self.get_default_case("int a; switch(a) { default: break; }", 'foo')
        self.assertEqual(str(default_case), 'default')
