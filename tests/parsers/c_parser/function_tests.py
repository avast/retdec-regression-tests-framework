"""
    Tests for the :module`regression_tests.parsers.c_parser.function` module.
"""

import io
import sys
from textwrap import dedent
from unittest import mock

from regression_tests.parsers.c_parser.stmts.goto_stmt import Label
from regression_tests.utils.list import NamedObjectList
from tests.parsers.c_parser import WithModuleTests


class FunctionTests(WithModuleTests):
    """Tests for `Function`."""

    def test_func_name_returns_correct_name(self):
        func = self.get_func('int main() {}', 'main')
        self.assertEqual(func.name, 'main')

    def test_type_is_correct(self):
        func = self.get_func('int func(void) {}', 'func')
        self.assertTrue(func.type.is_function())
        self.assertTrue(func.type.return_type.is_int())
        self.assertEqual(func.type.param_count, 0)
        self.assertFalse(func.type.is_variadic())

    def test_return_type_returns_void_for_void_func(self):
        func = self.get_func('void func() {}', 'func')
        self.assertTrue(func.return_type.is_void())

    def test_params_returns_empty_list_when_no_params(self):
        func = self.get_func('void func() {}', 'func')
        self.assertEqual(len(func.params), 0)

    def test_params_returns_list_with_two_params_when_two_params(self):
        func = self.get_func('void func(int a, int b) {}', 'func')
        self.assertEqual(len(func.params), 2)

    def test_params_returns_correct_variable_when_one_int_param(self):
        func = self.get_func('void func(int a) {}', 'func')
        var = func.params[0]
        self.assertEqual(var.name, 'a')
        self.assertTrue(var.type.is_int())

    def test_params_returns_variables_of_correct_types_for_standard_main(self):
        func = self.get_func('int main(int argc, char **argv) {}', 'main')
        self.assertTrue(len(func.params), 2)
        self.assertEqual(func.params[0].name, 'argc')
        self.assertTrue(func.params[0].type.is_int())
        self.assertEqual(func.params[1].name, 'argv')
        self.assertTrue(func.params[1].type.is_pointer())
        self.assertTrue(func.params[1].type.pointed_type.is_pointer())
        self.assertTrue(func.params[1].type.pointed_type.pointed_type.is_char())

    def test_params_returns_named_object_list(self):
        func = self.get_func('void func(int a, int b) {}', 'func')
        self.assertIsInstance(func.params, NamedObjectList)

    def test_param_names_returns_empty_list_when_no_params(self):
        func = self.get_func('void func() {}', 'func')
        self.assertEqual(len(func.param_names), 0)

    def test_param_names_returns_correct_list_when_two_params(self):
        func = self.get_func('void func(int a, int b) {}', 'func')
        self.assertEqual(func.param_names, ['a', 'b'])

    def test_param_count_returns_zero_when_no_params(self):
        func = self.get_func('void func() {}', 'func')
        self.assertEqual(func.param_count, 0)

    def test_param_count_returns_one_when_one_param(self):
        func = self.get_func('void func(int a) {}', 'func')
        self.assertEqual(func.param_count, 1)

    def test_param_count_returns_two_when_two_params(self):
        func = self.get_func('void func(int a, int b) {}', 'func')
        self.assertEqual(func.param_count, 2)

    def test_has_params_with_single_empty_list_checks_presence_of_at_least_one_param(self):
        func = self.get_func('void func(int a) {}', 'func')
        self.assertTrue(func.has_params([]))

    def test_has_params_returns_true_when_all_given_params_are_present(self):
        func = self.get_func('void func(int p1, int p2) {}', 'func')
        self.assertTrue(func.has_params('p1', 'p2'))

    def test_has_params_returns_true_when_all_given_params_passed_as_list_are_present(self):
        func = self.get_func('void func(int p1, int p2) {}', 'func')
        self.assertTrue(func.has_params(['p1', 'p2']))

    def test_has_params_disregards_order(self):
        func = self.get_func('void func(int p1, int p2) {}', 'func')
        self.assertTrue(func.has_params('p2', 'p1'))

    def test_has_params_returns_false_when_not_all_given_params_are_present(self):
        func = self.get_func('void func(int p1, int p3) {}', 'func')
        self.assertFalse(func.has_params(['p1', 'p2']))

    def test_has_no_params_returns_true_when_no_params(self):
        func = self.get_func('void func() {}', 'func')
        self.assertTrue(func.has_no_params())

    def test_has_no_params_returns_false_when_one_param(self):
        func = self.get_func('void func(int a) {}', 'func')
        self.assertFalse(func.has_no_params())

    def test_has_just_params_returns_true_when_no_params_and_no_params_given(self):
        func = self.get_func('void func() {}', 'func')
        self.assertTrue(func.has_just_params())

    def test_has_just_params_returns_false_when_no_params_and_param_given(self):
        func = self.get_func('void func() {}', 'func')
        self.assertFalse(func.has_just_params('param'))

    def test_has_just_params_returns_false_when_more_params_are_present(self):
        func = self.get_func('void func(int p1, int p2) {}', 'func')
        self.assertFalse(func.has_just_params('p1'))

    def test_has_just_params_returns_true_when_just_given_params_are_present(self):
        func = self.get_func('void func(int p1, int p2) {}', 'func')
        self.assertTrue(func.has_just_params('p1', 'p2'))

    def test_has_just_params_disregards_order(self):
        func = self.get_func('void func(int p1, int p2) {}', 'func')
        self.assertTrue(func.has_just_params('p2', 'p1'))

    def test_has_just_params_param_can_be_passed_in_list(self):
        func = self.get_func('void func(int p1, int p2) {}', 'func')
        self.assertTrue(func.has_just_params(['p2', 'p1']))

    def test_has_just_params_param_can_be_passed_in_set(self):
        func = self.get_func('void func(int p1, int p2) {}', 'func')
        self.assertTrue(func.has_just_params({'p2', 'p1'}))

    def test_has_param_returns_false_when_no_such_param(self):
        func = self.get_func('void func() {}', 'func')
        self.assertFalse(func.has_param('a'))

    def test_has_param_returns_true_when_there_is_such_param(self):
        func = self.get_func('void func(int a) {}', 'func')
        self.assertTrue(func.has_param('a'))

    def test_calls_returns_false_when_no_such_call(self):
        func = self.get_func("""
            void func() {}
        """, 'func')
        self.assertFalse(func.calls('other_func'))

    def test_calls_returns_false_when_not_all_calls_are_present(self):
        func = self.get_func("""
            void func1() {}
            void func2() {}

            void func() {
                func1();
            }
        """, 'func')
        self.assertFalse(func.calls('func1', 'func2'))

    def test_calls_returns_true_when_all_calls_are_present(self):
        func = self.get_func("""
            void func1() {}
            void func2() {}
            void func3() {}

            void func() {
                func1();
                func2();
            }
        """, 'func')
        self.assertTrue(func.calls('func1', 'func2'))

    def test_calls_are_found_even_if_nested(self):
        func = self.get_func("""
            void func1() {}
            void func2() {}

            void func() {
                if (1) {
                    for (int i = 1; i < 5; ++i) {
                        func1();
                    }
                } else {
                    if (2) {
                        func2();
                    }
                }
            }
        """, 'func')
        self.assertTrue(func.calls('func1', 'func2'))

    def test_calls_are_found_in_while_true_loop(self):
        # This tests that the 'true' literal is parsed correctly (it caused
        # problems when parsing by using clang without proper include path).
        func = self.get_func("""
            #include <stdbool.h>

            void other_func() {}

            void func() {
                while (true) {
                    other_func();
                }
            }
        """, 'func')
        self.assertTrue(func.calls('other_func'))

    def test_calls_disregards_order(self):
        func = self.get_func("""
            void func1() {}
            void func2() {}

            void func() {
                func1();
                func2();
            }
        """, 'func')
        self.assertTrue(func.calls('func2', 'func1'))

    def test_calls_can_be_called_with_function_as_argument(self):
        func = self.get_func("""
            void func() {}
        """, 'func')
        foo = self.get_func("""
            void foo() {
                func();
            }
        """, 'foo')
        self.assertTrue(foo.calls(func))

    def test_calls_functions_and_strings_can_be_mixed_as_arguments(self):
        func = self.get_func("""
            void func() {}
        """, 'func')
        foo = self.get_func("""
            void foo() {
                func();
                bar();
            }
        """, 'foo')
        self.assertTrue(foo.calls('bar', func))

    def test_calls_does_not_include_empty_function_name_when_there_is_error(self):
        # Based on commit 591255e.
        func = self.get_func("""
            void func() {
                (((void (*)())func)(); // <-- syntax error
            }
        """, 'func')
        self.assertFalse(func.calls(''))

    def test_calls_names_can_be_passed_in_list(self):
        func = self.get_func("""
            void func1() {}
            void func2() {}

            void func() {
                func1();
                func2();
            }
        """, 'func')
        self.assertTrue(func.calls(['func1', 'func2']))

    def test_calls_function_objects_can_be_passed_in_list(self):
        func1 = self.get_func('void func1() {}', 'func1')
        func = self.get_func("""
            void func() {
                func1();
                func2();
            }
        """, 'func')
        self.assertTrue(func.calls([func1, 'func2']))

    def test_calls_raises_exception_when_no_name(self):
        func = self.get_func("""
            void func() {}
        """, 'func')
        with self.assertRaises(AssertionError):
            func.calls()

    def test_calls_raises_exception_when_empty_list_of_names(self):
        func = self.get_func("""
            void func() {}
        """, 'func')
        with self.assertRaises(AssertionError):
            func.calls([])

    def test_calls_raises_exception_when_unsupported_type_of_arg_used(self):
        func = self.get_func("""
            void func() {}
        """, 'func')
        with self.assertRaises(AttributeError):
            func.calls(123)

    def test_called_func_names_returns_correct_set(self):
        func = self.get_func("""
            void func1() {}
            void func2() {}

            void func() {
                func1();
                func2();
            }
        """, 'func')
        self.assertEqual(func.called_func_names, {'func1', 'func2'})

    def test_has_any_for_loops_returns_false_when_there_is_no_for_loop(self):
        func = self.get_func("""
            void func() {}
        """, 'func')
        self.assertFalse(func.has_any_for_loops())

    def test_has_any_for_loops_returns_true_when_there_is_for_loop(self):
        func = self.get_func("""
            void func() {
                for (int i = 0; i < 10; ++i) {}
            }
        """, 'func')
        self.assertTrue(func.has_any_for_loops())

    def test_has_for_loops_returns_true_when_function_contains_all_given_for_loops(self):
        func = self.get_func("""
            void func() {
                for (int i = 0; i < 10; ++i) {}
                for (int x = 5; x > 0; x--) {}
                for (int a = 0; a < 1; a++) {}
            }
        """, 'func')
        func2 = self.get_func("""
            void func() {
                for (int x = 5; x > 0; x--) {}
            }
        """, 'func')
        for_obj = func2.for_loops[0]
        self.assertTrue(func.has_for_loops('for (int i = 0; i < 10; ++i)', for_obj))

    def test_has_for_loops_returns_false_when_function_is_missing_some_of_given_for_loops(self):
        func = self.get_func("""
            void func() {
                for (int i = 0; i < 10; ++i) {}
            }
        """, 'func')
        func2 = self.get_func("""
            void func() {
                for (int x = 5; x > 0; x++) {}
            }
        """, 'func')
        for_obj = func2.for_loops[0]
        self.assertFalse(func.has_for_loops('for (int i = 0; i < 10; ++i)', for_obj))

    def test_for_loops_returns_empty_list_when_there_are_no_for_loops(self):
        func = self.get_func("""
            void func() {}
        """, 'func')
        self.assertEqual(func.for_loops, [])

    def test_for_loops_returns_list_with_two_loops_when_there_are_two_consecutive_for_loops(self):
        func = self.get_func("""
            void func() {
                for (int i = 0; i < 10; ++i) {}
                for (int i = 0; i < 10; ++i) {}
            }
        """, 'func')
        self.assertEqual(len(func.for_loops), 2)

    def test_for_loops_returns_list_with_two_loops_when_there_are_two_nested_for_loops(self):
        func = self.get_func("""
            void func() {
                for (int i = 0; i < 10; ++i) {
                    for (int j = 0; i < j; ++j) {}
                }
            }
        """, 'func')
        self.assertEqual(len(func.for_loops), 2)

    def test_for_loops_can_be_indexed_by_string_with_identification_of_searched_for_loop(self):
        func = self.get_func("""
            void func() {
                for (int i = 0; i < 10; ++i) {}
            }
        """, 'func')
        self.assertEqual(func.for_loops['for (int i = 0; i < 10; ++i)'].header, 'int i = 0; i < 10; ++i')

    def test_has_any_while_loops_returns_false_when_there_is_no_while_loop(self):
        func = self.get_func("""
            void func() {}
        """, 'func')
        self.assertFalse(func.has_any_while_loops())

    def test_has_any_while_loops_returns_true_when_there_is_while_loop(self):
        func = self.get_func("""
            void func() {
                while (1) {}
            }
        """, 'func')
        self.assertTrue(func.has_any_while_loops())

    def test_has_while_loops_returns_true_when_function_contains_all_given_while_loops(self):
        func = self.get_func("""
            void func() {
                while(0) {}
                while(1) {}
                while(2) {}
            }
        """, 'func')
        func2 = self.get_func("""
            void func() {
                while(1) {}
            }
        """, 'func')
        while_obj = func2.while_loops[0]
        self.assertTrue(func.has_while_loops('while (0)', while_obj))

    def test_has_while_loops_returns_false_when_function_is_missing_some_of_given_while_loops(self):
        func = self.get_func("""
            void func() {
                while(0) {}
            }
        """, 'func')
        func2 = self.get_func("""
            void func() {
                while(1) {}
            }
        """, 'func')
        while_obj = func2.while_loops[0]
        self.assertFalse(func.has_while_loops('while (0)', while_obj))

    def test_while_loop_is_correctly_parsed(self):
        func = self.get_func("""
            void func() {
                while (1) {}
            }
        """, 'func')
        self.assertTrue(func.while_loops[0].is_while_loop())
        self.assertEqual(func.while_loops[0].condition, 1)

    def test_while_loops_returns_empty_list_when_there_are_no_while_loops(self):
        func = self.get_func("""
            void func() {}
        """, 'func')
        self.assertEqual(func.while_loops, [])

    def test_while_loops_returns_list_with_two_loops_when_there_are_two_consecutive_while_loops(self):
        func = self.get_func("""
            void func() {
                while (1) {}
                while (1) {}
            }
        """, 'func')
        self.assertEqual(len(func.while_loops), 2)

    def test_while_loops_returns_list_with_two_loops_when_there_are_two_nested_while_loops(self):
        func = self.get_func("""
            void func() {
                while (1) {
                    while (1) {}
                }
            }
        """, 'func')
        self.assertEqual(len(func.while_loops), 2)

    def test_while_loops_can_be_indexed_by_string_with_identification_of_searched_while_loop(self):
        func = self.get_func("""
            void func() {
                while (1) {}
            }
        """, 'func')
        self.assertEqual(func.while_loops['while (1)'].condition, 1)

    def test_all_while_loops_are_found(self):
        func = self.get_func("""
            void func(void) {
                while (1) {}
                for (;;) {}
                while (2) {}
            }
        """, 'func')
        self.assertEqual(len(func.while_loops), 2)
        self.assertTrue(func.while_loops[0].is_while_loop())
        self.assertEqual(func.while_loops[0].condition, 1)
        self.assertTrue(func.while_loops[1].is_while_loop())
        self.assertEqual(func.while_loops[1].condition, 2)

    def test_while_loop_is_found_in_other_stmt(self):
        func = self.get_func("""
            void func(void) {
                for (;;) {
                    while (1) {}
                }
            }
        """, 'func')
        self.assertEqual(len(func.while_loops), 1)
        self.assertTrue(func.while_loops[0].is_while_loop())
        self.assertEqual(func.while_loops[0].condition, 1)

    def test_has_any_assignments_returns_true_when_there_is_assign_stmt(self):
        func = self.get_func("""
            void func(void) {
                int a;
                a = 5;
            }
        """, 'func')
        self.assertTrue(func.has_any_assignments())

    def test_has_any_assignments_returns_false_when_there_is_no_assignment(self):
        func = self.get_func("""
            void func(void) {}
        """, 'func')
        self.assertFalse(func.has_any_assignments())

    def test_has_assignments_returns_true_when_function_contains_all_given_assignments(self):
        func = self.get_func("""
            void func() {
                int x;
                x = 4;
                x = 5;
                x = 6;
            }
        """, 'func')
        func2 = self.get_func("""
            void func() {
                int x;
                x = 4;
            }
        """, 'func')
        assign_obj = func2.assignments[0]
        self.assertTrue(func.has_assignments('x = 5', assign_obj))

    def test_has_assignments_returns_false_when_function_is_missing_some_of_given_assignments(self):
        func = self.get_func("""
            void func() {
                int x;
                x = 4;
            }
        """, 'func')
        func2 = self.get_func("""
            void func() {
                int x;
                x = 5;
            }
        """, 'func')
        assign_obj = func2.assignments[0]
        self.assertFalse(func.has_assignments('x = 4', assign_obj))

    def test_no_assignment_parsed_when_none_present_in_body(self):
        func = self.get_func("""
            void func(void) {
                for (;;) {}
            }
        """, 'func')
        self.assertEqual(len(func.assignments), 0)

    def test_assignment_is_correctly_parsed(self):
        func = self.get_func("""
            void func(void) {
                int a;
                a = 5;
            }
        """, 'func')
        self.assertEqual(len(func.assignments), 1)
        self.assertEqual(func.assignments[0].lhs, 'a')
        self.assertEqual(func.assignments[0].rhs, '5')

    def test_all_assignments_are_found(self):
        func = self.get_func("""
            void func(void) {
                int a;
                a = 5;
                for (;;) {}
                double b;
                b = 2.0;
            }
        """, 'func')
        self.assertEqual(len(func.assignments), 2)
        self.assertEqual(func.assignments[0].lhs, 'a')
        self.assertEqual(func.assignments[0].rhs, 5)
        self.assertEqual(func.assignments[1].lhs, 'b')
        self.assertEqual(func.assignments[1].rhs, 2.0)

    def test_assignment_is_found_in_other_stmt(self):
        func = self.get_func("""
            void func(void) {
                for (;;) {
                    int a;
                    a = 5;
                }
            }
        """, 'func')
        self.assertEqual(len(func.assignments), 1)
        self.assertEqual(func.assignments[0].lhs, 'a')
        self.assertEqual(func.assignments[0].rhs, 5)

    def test_assignments_can_be_indexed_by_string_with_identification_of_searched_assignment(self):
        func = self.get_func("""
            void func() {
                int a;
                a = 4
            }
        """, 'func')
        self.assertEqual(func.assignments['a = 4'].lhs, 'a')
        self.assertEqual(func.assignments['a = 4'].rhs, 4)

    def test_assign_item_of_array(self):
        func = self.get_func("""
            void func(void) {
                int arr[5];
                arr[0] = 2;
            }
        """, 'func')
        self.assertEqual(len(func.assignments), 1)
        self.assertEqual(func.assignments[0].lhs, 'arr[0]')
        self.assertEqual(func.assignments[0].rhs, 2)

    def test_assign_to_dereferenced_pointer(self):
        func = self.get_func("""
            void func(void) {
                int x = 0;
                int *p = &x;
                *p = 7;
            }
        """, 'func')
        self.assertEqual(len(func.assignments), 3)
        self.assertEqual(func.assignments['*p = 7'].lhs, '*p')
        self.assertEqual(func.assignments['*p = 7'].rhs, 7)

    def test_assign_to_struct_item(self):
        func = self.get_func("""
            void func(void) {
                struct {
                    int x;
                } s;
                s.x = 25;
            }
        """, 'func')
        self.assertEqual(len(func.assignments), 1)
        self.assertEqual(func.assignments[0].lhs, 's.x')
        self.assertEqual(func.assignments[0].rhs, 25)

    def test_compound_assignments_are_found(self):
        func = self.get_func("""
            void func(void) {
                int x = 0;
                x += 5;
                x %= 2;
                x *= 3;
            }
        """, 'func')
        self.assertEqual(len(func.assignments), 4)
        self.assertEqual(func.assignments['x = 0'].lhs, 'x')
        self.assertEqual(func.assignments['x = 0'].rhs, 0)
        self.assertEqual(func.assignments['x += 5'].lhs, 'x')
        self.assertEqual(func.assignments['x += 5'].rhs, 5)
        self.assertEqual(func.assignments['x %= 2'].lhs, 'x')
        self.assertEqual(func.assignments['x %= 2'].rhs, 2)
        self.assertEqual(func.assignments['x *= 3'].lhs, 'x')
        self.assertEqual(func.assignments['x *= 3'].rhs, 3)

    def test_has_any_if_stmts_returns_true_when_there_is_if_stmt(self):
        func = self.get_func("""
            void func(void) {
                if (1) foo();
            }
        """, 'func')
        self.assertTrue(func.has_any_if_stmts())

    def test_has_any_if_stmts_returns_false_when_there_is_no_if_stmt(self):
        func = self.get_func("""
            void func(void) {}
        """, 'func')
        self.assertFalse(func.has_any_if_stmts())

    def test_has_var_def_stmts_returns_true_when_function_contains_all_given_var_def_stmts(self):
        func = self.get_func("""
            void func() {
                int x = 0;
                int y = 1;
                int z = 2;
            }
        """, 'func')
        func2 = self.get_func("""
            void func() {
                int y = 1;
            }
        """, 'func')
        var_def_obj = func2.var_def_stmts[0]
        self.assertTrue(func.has_var_def_stmts('int x = 0', var_def_obj))

    def test_has_var_def_stmts_returns_false_when_function_is_missing_some_of_given_var_def_stmts(self):
        func = self.get_func("""
            void func() {
                int y = 1;
                int z = 2;
            }
        """, 'func')
        func2 = self.get_func("""
            void func() {
                int y = 1;
            }
        """, 'func')
        var_def_obj = func2.var_def_stmts[0]
        self.assertFalse(func.has_var_def_stmts('int x = 0', var_def_obj))

    def test_no_if_stmt_parsed_when_none_present_in_body(self):
        func = self.get_func("""
            void func(void) {
                for (;;) {}
            }
        """, 'func')
        self.assertEqual(len(func.if_stmts), 0)

    def test_if_stmt_is_correctly_parsed(self):
        func = self.get_func("""
            void func(void) {
                if (1) foo();
                else bar();
            }
        """, 'func')
        self.assertEqual(len(func.if_stmts), 1)
        self.assertTrue(func.if_stmts[0].is_if_stmt())
        self.assertTrue(func.if_stmts[0].has_else_clause())
        self.assertEqual(func.if_stmts[0].condition, '1')

    def test_if_stmt_is_found_in_other_stmt(self):
        func = self.get_func("""
            void func(void) {
                for (;;) {
                    if (1) foo();
                }
            }
        """, 'func')
        self.assertEqual(len(func.if_stmts), 1)
        self.assertTrue(func.if_stmts[0].is_if_stmt())
        self.assertFalse(func.if_stmts[0].has_else_clause())
        self.assertEqual(func.if_stmts[0].condition, '1')

    def test_all_if_stmts_are_found(self):
        func = self.get_func("""
            void func(void) {
                if (1) foo();
                for (;;) {}
                if (1) foo();
                else bar();
            }
        """, 'func')
        self.assertEqual(len(func.if_stmts), 2)
        self.assertTrue(func.if_stmts[0].is_if_stmt())
        self.assertTrue(func.if_stmts[1].is_if_stmt())

    def test_if_statements_can_be_indexed_by_string_with_identification_of_searched_if_statement(self):
        func = self.get_func("""
            void func() {
                if (2) {}
            }
        """, 'func')
        self.assertEqual(func.if_stmts['if (2)'].condition, 2)

    def test_else_if_branch_is_child_of_if_branch_above_it(self):
        func = self.get_func("""
            void func(void) {
                if (1) {
                    foo();
                } else if (2) {
                    bar();
                } else if (3) {
                    baz();
                }
            }
        """, 'func')
        self.assertEqual(len(func.if_stmts), 3)
        self.assertEqual(func.if_stmts[0].condition, '1')
        self.assertTrue(func.if_stmts[0].has_else_clause())
        self.assertEqual(func.if_stmts[1].condition, '2')
        self.assertTrue(func.if_stmts[1].has_else_clause())
        self.assertEqual(func.if_stmts[2].condition, '3')
        self.assertFalse(func.if_stmts[2].has_else_clause())
        self.assertIsNone(func.if_stmts[0].next_stmt)
        self.assertIsNone(func.if_stmts[1].next_stmt)
        self.assertIsNone(func.if_stmts[2].next_stmt)

    def test_next_stmt_is_set_correctly_for_all_stmts(self):
        func = self.get_func("""
            void func(void) {
                int a;
                double b;
                a = 5;
                for (;;) {}
                b = 2.0;
            }
        """, 'func')
        var_defs = func.var_def_stmts
        self.assertEqual(var_defs[0].next_stmt, var_defs[1])
        self.assertIsNone(var_defs[1].next_stmt)
        self.assertIsNone(func.for_loops[0].next_stmt)

    def test_has_any_var_def_stmts_returns_true_when_there_is_var_def_stmt(self):
        func = self.get_func("""
            void func(void) {
                int a = 5;
            }
        """, 'func')
        self.assertTrue(func.has_any_var_def_stmts())

    def test_has_any_var_def_stmts_returns_false_when_there_is_no_var_def_stmt(self):
        func = self.get_func("""
            void func(void) {}
        """, 'func')
        self.assertFalse(func.has_any_var_def_stmts())

    def test_has_if_stmts_returns_true_when_function_contains_all_given_if_stmts(self):
        func = self.get_func("""
            void func() {
                if (0) {}
                if (1) {}
                if (2) {}
            }
        """, 'func')
        func2 = self.get_func("""
            void func() {
                if (1) {}
            }
        """, 'func')
        if_obj = func2.if_stmts[0]
        self.assertTrue(func.has_if_stmts('if(0)', if_obj))

    def test_has_if_stmts_returns_false_when_function_is_missing_some_of_given_if_stmts(self):
        func = self.get_func("""
            void func() {
                if (0) {}
                if (2) {}
            }
        """, 'func')
        func2 = self.get_func("""
            void func() {
                if (1) {}
            }
        """, 'func')
        if_obj = func2.if_stmts[0]
        self.assertFalse(func.has_if_stmts('if(0)', if_obj))

    def test_no_var_def_stmt_parsed_when_none_present_in_body(self):
        func = self.get_func("""
            void func(void) {
                for (;;) {}
            }
        """, 'func')
        self.assertEqual(len(func.var_def_stmts), 0)

    def test_var_def_stmt_is_correctly_parsed(self):
        func = self.get_func("""
            void func(void) {
                int a = 5;
            }
        """, 'func')
        self.assertEqual(len(func.var_def_stmts), 1)
        self.assertTrue(func.var_def_stmts[0].is_var_def())
        self.assertEqual(func.var_def_stmts[0].var.name, 'a')
        self.assertTrue(func.var_def_stmts[0].var.type.is_int())
        self.assertEqual(func.var_def_stmts[0].initializer, 5)

    def test_all_var_def_stmts_are_found(self):
        func = self.get_func("""
            void func(void) {
                int a = 5;
                for (;;) {}
                double b = 1.0;
            }
        """, 'func')
        self.assertEqual(len(func.var_def_stmts), 2)
        self.assertTrue(func.var_def_stmts[0].is_var_def())
        self.assertEqual(func.var_def_stmts[0].var.name, 'a')
        self.assertTrue(func.var_def_stmts[0].var.type.is_int())
        self.assertEqual(func.var_def_stmts[0].initializer, 5)
        self.assertTrue(func.var_def_stmts[1].is_var_def())
        self.assertEqual(func.var_def_stmts[1].var.name, 'b')
        self.assertTrue(func.var_def_stmts[1].var.type.is_double())
        self.assertEqual(func.var_def_stmts[1].initializer, 1.0)

    def test_var_def_stmt_is_found_in_other_stmt(self):
        func = self.get_func("""
            void func(void) {
                if(1) {
                    int a = 5;
                }
            }
        """, 'func')
        self.assertEqual(len(func.var_def_stmts), 1)
        self.assertTrue(func.var_def_stmts[0].is_var_def())
        self.assertEqual(func.var_def_stmts[0].var.name, 'a')
        self.assertTrue(func.var_def_stmts[0].var.type.is_int())
        self.assertEqual(func.var_def_stmts[0].initializer, 5)

    def test_var_def_stmts_can_be_indexed_by_string_with_identification_of_searched_var_def_stmt(self):
        func = self.get_func("""
            void func() {
                int a = 5;
            }
        """, 'func')
        self.assertEqual(func.var_def_stmts['a = 5'].initializer, 5)

    def test_has_any_return_stmts_returns_false_when_there_is_no_return_stmt(self):
        func = self.get_func("""
            void func() {}
        """, 'func')
        self.assertFalse(func.has_any_return_stmts())

    def test_has_any_return_stmts_returns_true_when_there_is_return_stmt(self):
        func = self.get_func("""
            void func() {
                return;
            }
        """, 'func')
        self.assertTrue(func.has_any_return_stmts())

    def test_has_return_stmts_returns_true_when_function_contains_all_given_return_stmts(self):
        func = self.get_func("""
            void func() {
                return 0;
                return 1;
                return 2;
            }
        """, 'func')
        func2 = self.get_func("""
            void func() {
                return 1;
            }
        """, 'func')
        return_obj = func2.return_stmts[0]
        self.assertTrue(func.has_return_stmts('return 0', return_obj))

    def test_has_return_stmts_returns_false_when_function_is_missing_some_of_given_return_stmts(self):
        func = self.get_func("""
            void func() {
                return 0;
            }
        """, 'func')
        func2 = self.get_func("""
            void func() {
                return 1;
            }
        """, 'func')
        return_obj = func2.return_stmts[0]
        self.assertFalse(func.has_return_stmts('return 0', return_obj))

    def test_return_stmt_is_correctly_parsed(self):
        func = self.get_func("""
            int func() {
                return 1 + 2;
            }
        """, 'func')
        self.assertTrue(func.return_stmts[0].is_return_stmt())
        self.assertTrue(func.return_stmts[0].return_expr.is_add_op())
        self.assertEqual(func.return_stmts[0].return_expr.lhs, 1)
        self.assertEqual(func.return_stmts[0].return_expr.rhs, 2)

    def test_return_stmts_returns_empty_list_when_there_are_no_return_stmts(self):
        func = self.get_func("""
            void func() {}
        """, 'func')
        self.assertEqual(func.return_stmts, [])

    def test_return_stmts_returns_list_with_two_loops_when_there_are_two_consecutive_return_stmts(self):
        func = self.get_func("""
            void func() {
                return;
                return;
            }
        """, 'func')
        self.assertEqual(len(func.return_stmts), 2)

    def test_all_return_stmts_are_found(self):
        func = self.get_func("""
            int func(void) {
                return 123;
                for (;;) {}
                return 321;
            }
        """, 'func')
        self.assertEqual(len(func.return_stmts), 2)
        self.assertEqual(func.return_stmts[0].return_expr.value, 123)
        self.assertEqual(func.return_stmts[1].return_expr.value, 321)

    def test_return_stmt_is_found_in_other_stmt(self):
        func = self.get_func("""
            int func(void) {
                for (;;) {
                    return 456;
                }
            }
        """, 'func')
        self.assertEqual(len(func.return_stmts), 1)
        self.assertTrue(func.return_stmts[0].is_return_stmt())
        self.assertEqual(func.return_stmts[0].return_expr.value, 456)

    def test_return_stmts_can_be_indexed_by_string_with_identification_of_searched_return_stmt(self):
        func = self.get_func("""
            int func() {
                return 4;
            }
        """, 'func')
        self.assertEqual(func.return_stmts['return 4'].return_expr, 4)

    def test_has_any_empty_stmts_returns_false_when_there_is_no_empty_stmt(self):
        func = self.get_func("""
            void func() {}
        """, 'func')
        self.assertFalse(func.has_any_empty_stmts())

    def test_has_any_empty_stmts_returns_true_when_there_is_empty_stmt(self):
        func = self.get_func("""
            void func() {
                ;
            }
        """, 'func')
        self.assertTrue(func.has_any_empty_stmts())

    def test_empty_stmt_is_correctly_parsed(self):
        func = self.get_func("""
            int func() {
                ;
            }
        """, 'func')
        self.assertTrue(func.empty_stmts[0].is_empty_stmt())

    def test_empty_stmts_returns_empty_list_when_there_are_no_empty_stmts(self):
        func = self.get_func("""
            void func() {}
        """, 'func')
        self.assertEqual(func.empty_stmts, [])

    def test_empty_stmts_returns_list_with_two_loops_when_there_are_two_consecutive_empty_stmts(self):
        func = self.get_func("""
            void func() {
                ;;
            }
        """, 'func')
        self.assertEqual(len(func.empty_stmts), 2)

    def test_all_empty_stmts_are_found(self):
        func = self.get_func("""
            int func(void) {
                ;
                for (;;) {}
                ;
            }
        """, 'func')
        self.assertEqual(len(func.empty_stmts), 2)

    def test_empty_stmt_is_found_in_other_stmt(self):
        func = self.get_func("""
            int func(void) {
                for (;;) {
                    ;
                }
            }
        """, 'func')
        self.assertEqual(len(func.empty_stmts), 1)
        self.assertTrue(func.empty_stmts[0].is_empty_stmt())

    def test_has_any_switch_stmts_returns_false_when_there_is_no_switch_stmt(self):
        func = self.get_func("""
            void func() {}
        """, 'func')
        self.assertFalse(func.has_any_switch_stmts())

    def test_has_any_switch_stmts_returns_true_when_there_is_switch_stmt(self):
        func = self.get_func("""
            void func() {
                int a;

                switch(a) {}
            }
        """, 'func')
        self.assertTrue(func.has_any_switch_stmts())

    def test_has_switch_stmts_returns_true_when_function_contains_all_given_switch_stmts(self):
        func = self.get_func("""
            void func() {
                int a;
                switch(a) {case 1: break;}
                switch(a) {case 3: break;}
                switch(a) {default: break;}
            }
        """, 'func')
        func2 = self.get_func("""
            void func() {
                int a;
                switch(a) {default: break;}
            }
        """, 'func')
        switch_obj = func2.switch_stmts[0]
        self.assertTrue(func.has_switch_stmts('switch(a) {case 1}', switch_obj))

    def test_has_switch_stmts_returns_false_when_function_is_missing_some_of_given_switch_stmts(self):
        func = self.get_func("""
            void func() {
                int a;
                switch(a) {case 1: break;}
                switch(a) {case 3: break;}
            }
        """, 'func')
        func2 = self.get_func("""
            void func() {
                int a;
                switch(a) {default: break;}
            }
        """, 'func')
        switch_obj = func2.switch_stmts[0]
        self.assertFalse(func.has_switch_stmts('switch(a) {case 1}', switch_obj))

    def test_switch_stmt_is_correctly_parsed(self):
        func = self.get_func("""
            void func() {
                int a;

                switch(a) {
                    case 7: ;
                    case 5: ;
                    default:
                        break;
                }
            }
        """, 'func')
        self.assertTrue(func.switch_stmts[0].is_switch_stmt())
        self.assertEqual(func.switch_stmts[0].switch_expr, 'a')
        self.assertTrue(func.switch_stmts[0].has_cases())
        self.assertEqual(len(func.switch_stmts[0].cases), 2)
        self.assertTrue(func.switch_stmts[0].has_default_case())

    def test_switch_stmts_returns_empty_list_when_there_are_no_switch_stmts(self):
        func = self.get_func("""
            void func() {}
        """, 'func')
        self.assertEqual(func.switch_stmts, [])

    def test_switch_stmts_returns_list_with_two_loops_when_there_are_two_consecutive_switch_stmts(self):
        func = self.get_func("""
            void func() {
                int a, b;

                switch(a) {
                    switch(b) {}
                }
            }
        """, 'func')
        self.assertEqual(len(func.switch_stmts), 2)

    def test_all_switch_stmts_are_found(self):
        func = self.get_func("""
            int func(void) {
                int a, b;
                switch(a) {}
                for (;;) {}
                switch(b) {}
            }
        """, 'func')
        self.assertEqual(len(func.switch_stmts), 2)

    def test_switch_stmt_is_found_in_other_stmt(self):
        func = self.get_func("""
            int func(void) {
                for (;;) {
                    int a;

                    switch(a) {}
                }
            }
        """, 'func')
        self.assertEqual(len(func.switch_stmts), 1)
        self.assertTrue(func.switch_stmts[0].is_switch_stmt())

    def test_switch_stmts_can_be_indexed_by_string_with_identification_of_searched_switch_statement(self):
        func = self.get_func("""
            void func() {
                int a;
                switch(a) {
                    case 2: break;
                }
            }
        """, 'func')
        self.assertEqual(len(func.switch_stmts['switch(a){case 2}'].cases), 1)

    def test_has_any_goto_stmts_returns_false_when_there_is_no_goto_stmt(self):
        func = self.get_func("""
            void func() {}
        """, 'func')
        self.assertFalse(func.has_any_goto_stmts())

    def test_has_any_goto_stmts_returns_true_when_there_is_goto_stmt(self):
        func = self.get_func("""
            void func() {
                abc: ;

                goto abc;
            }
        """, 'func')
        self.assertTrue(func.has_any_goto_stmts())

    def test_has_goto_stmts_returns_true_when_function_contains_all_given_goto_stmts(self):
        func = self.get_func("""
            void func() {
                abc:
                goto xyz;
                def:
                goto abc;
                xyz:
                goto def;
            }
        """, 'func')
        func2 = self.get_func("""
            void func() {
                def:
                goto def;
            }
        """, 'func')
        goto_obj = func2.goto_stmts[0]
        self.assertTrue(func.has_goto_stmts('goto xyz', goto_obj))

    def test_has_goto_stmts_returns_false_when_function_is_missing_some_of_given_goto_stmts(self):
        func = self.get_func("""
            void func() {
                abc:
                def:
                goto abc;
                xyz:
                goto def;
            }
        """, 'func')
        func2 = self.get_func("""
            void func() {
                def:
                goto def;
            }
        """, 'func')
        goto_obj = func2.goto_stmts[0]
        self.assertFalse(func.has_goto_stmts('goto xyz', goto_obj))

    def test_goto_stmt_is_correctly_parsed(self):
        func = self.get_func("""
            void func() {
                abc: ;

                goto abc;
            }
        """, 'func')
        self.assertTrue(func.goto_stmts[0].is_goto_stmt())
        self.assertEqual(func.goto_stmts[0].target, 'abc')

    def test_goto_stmts_returns_empty_list_when_there_are_no_goto_stmts(self):
        func = self.get_func("""
            void func() {}
        """, 'func')
        self.assertEqual(func.goto_stmts, [])

    def test_goto_stmts_returns_list_with_two_loops_when_there_are_two_consecutive_goto_stmts(self):
        func = self.get_func("""
            void func() {
                abc: ;

                goto abc;
                goto abc;
                }
            }
        """, 'func')
        self.assertEqual(len(func.goto_stmts), 2)

    def test_all_goto_stmts_are_found(self):
        func = self.get_func("""
            int func(void) {
                abc: ;
                goto abc;
                for (;;) {}
                goto abc;
            }
        """, 'func')
        self.assertEqual(len(func.goto_stmts), 2)

    def test_goto_stmt_is_found_in_other_stmt(self):
        func = self.get_func("""
            int func(void) {
                abc: ;
                for (;;) {
                    goto abc;
                }
            }
        """, 'func')
        self.assertEqual(len(func.goto_stmts), 1)
        self.assertTrue(func.goto_stmts[0].is_goto_stmt())

    def test_goto_stmts_can_be_indexed_by_string_with_identification_of_searched_goto_statement(self):
        func = self.get_func("""
            void func() {
                abc:
                goto abc;
            }
        """, 'func')
        self.assertEqual(func.goto_stmts['goto abc'].target, 'abc')

    def test_has_any_labels_returns_false_when_there_is_no_label(self):
        func = self.get_func("""
            void func() {}
        """, 'func')
        self.assertFalse(func.has_any_labels())

    def test_has_any_labels_returns_true_when_there_is_label(self):
        func = self.get_func("""
            void func() {
                abc: ;
            }
        """, 'func')
        self.assertTrue(func.has_any_labels())

    def test_has_labels_returns_true_when_function_contains_all_given_labels(self):
        func = self.get_func("""
            void func() {
                abc: ;
                def: ;
                xyz: ;
            }
        """, 'func')
        func2 = self.get_func("""
            void func() {
                def: ;
            }
        """, 'func')
        label_obj = func2.labels[0]
        self.assertTrue(func.has_labels('abc:', label_obj))

    def test_has_labels_returns_false_when_function_is_missing_some_of_given_labels(self):
        func = self.get_func("""
            void func() {
                abc: ;
                xyz: ;
            }
        """, 'func')
        func2 = self.get_func("""
            void func() {
                def: ;
            }
        """, 'func')
        label_obj = func2.labels[0]
        self.assertFalse(func.has_labels('abc:', label_obj))

    def test_label_is_correctly_parsed(self):
        func = self.get_func("""
            void func() {
                abc: ;
            }
        """, 'func')
        self.assertTrue(isinstance(func.labels[0], Label))
        self.assertEqual(func.labels[0].name, 'abc')

    def test_labels_returns_empty_list_when_there_are_no_labels(self):
        func = self.get_func("""
            void func() {}
        """, 'func')
        self.assertEqual(func.labels, [])

    def test_labels_returns_list_with_two_loops_when_there_are_two_consecutive_labels(self):
        func = self.get_func("""
            void func() {
                abc: ;
                def: ;
                }
            }
        """, 'func')
        self.assertEqual(len(func.labels), 2)

    def test_all_labels_are_found(self):
        func = self.get_func("""
            int func(void) {
                abc: ;
                for (;;) {}
                def: ;
            }
        """, 'func')
        self.assertEqual(len(func.labels), 2)

    def test_label_is_found_in_other_stmt(self):
        func = self.get_func("""
            int func(void) {
                for (;;) {
                    abc: ;
                }
            }
        """, 'func')
        self.assertEqual(len(func.labels), 1)

    def test_labels_can_be_indexed_by_string_with_identification_of_searched_label(self):
        func = self.get_func("""
            void func() {
                abc:
            }
        """, 'func')
        self.assertEqual(func.labels['abc'].name, 'abc')

    def test_has_any_do_while_loops_returns_false_when_there_is_no_do_while_loop(self):
        func = self.get_func("""
            void func() {}
        """, 'func')
        self.assertFalse(func.has_any_do_while_loops())

    def test_has_any_do_while_loops_returns_true_when_there_is_do_while_loop(self):
        func = self.get_func("""
            void func() {
                do {} while (1);
            }
        """, 'func')
        self.assertTrue(func.has_any_do_while_loops())

    def test_has_do_while_loops_returns_true_when_function_contains_all_given_do_while_loops(self):
        func = self.get_func("""
            void func() {
                do {} while(0);
                do {} while(1);
                do {} while(2);
            }
        """, 'func')
        func2 = self.get_func("""
            void func() {
                do {} while(1);
            }
        """, 'func')
        do_while_obj = func2.do_while_loops[0]
        self.assertTrue(func.has_do_while_loops('do while (0)', do_while_obj))

    def test_has_do_while_loops_returns_false_when_function_is_missing_some_of_given_do_while_loops(self):
        func = self.get_func("""
            void func() {
                do {} while(0);
                do {} while(2);
            }
        """, 'func')
        func2 = self.get_func("""
            void func() {
                do {} while(1);
            }
        """, 'func')
        do_while_obj = func2.do_while_loops[0]
        self.assertFalse(func.has_do_while_loops('do while (0)', do_while_obj))

    # def test_do_while_loop_returns_correct_do_while_loop_from_function_body_using_string_param(self):
    #     func = self.get_func("""
    #         void func() {
    #             do {} while(1);
    #         }
    #     """, 'func')
    #     self.assertEqual(func.do_while_loop('do while (1)').condition, '1')
    #
    # def test_do_while_loop_returns_correct_do_while_loop_from_function_body_using_object_param(self):
    #     func = self.get_func("""
    #         void func() {
    #             do {} while(1);
    #         }
    #     """, 'func')
    #     do_while_obj = func.do_while_loops[0]
    #     self.assertEqual(func.do_while_loop(do_while_obj).condition, '1')

    def test_do_while_loop_is_correctly_parsed(self):
        func = self.get_func("""
            void func() {
                do {} while (1);
            }
        """, 'func')
        self.assertTrue(func.do_while_loops[0].is_do_while_loop())
        self.assertEqual(func.do_while_loops[0].condition, 1)

    def test_do_while_loops_returns_empty_list_when_there_are_no_do_while_loops(self):
        func = self.get_func("""
            void func() {}
        """, 'func')
        self.assertEqual(func.do_while_loops, [])

    def test_do_while_loops_returns_list_with_two_loops_when_there_are_two_consecutive_do_while_loops(self):
        func = self.get_func("""
            void func() {
                do {} while (1);
                do {} while (1);
            }
        """, 'func')
        self.assertEqual(len(func.do_while_loops), 2)

    def test_do_while_loops_returns_list_with_two_loops_when_there_are_two_nested_do_while_loops(self):
        func = self.get_func("""
            void func() {
                do {
                   do {} while (1);
                } while (1);
            }
        """, 'func')
        self.assertEqual(len(func.do_while_loops), 2)

    def test_do_while_loops_can_be_indexed_by_string_with_identification_of_searched_while_loop(self):
        func = self.get_func("""
            void func() {
                do {} while (1);
            }
        """, 'func')
        self.assertEqual(func.do_while_loops['do while (1)'].condition, 1)

    def test_all_do_while_loops_are_found(self):
        func = self.get_func("""
            void func(void) {
                do {} while (1);
                for (;;) {}
                do {} while (2);
            }
        """, 'func')
        self.assertEqual(len(func.do_while_loops), 2)
        self.assertTrue(func.do_while_loops[0].is_do_while_loop())
        self.assertEqual(func.do_while_loops[0].condition, 1)
        self.assertTrue(func.do_while_loops[1].is_do_while_loop())
        self.assertEqual(func.do_while_loops[1].condition, 2)

    def test_do_while_loop_is_found_in_other_stmt(self):
        func = self.get_func("""
            void func(void) {
                for (;;) {
                    do {} while (1);
                }
            }
        """, 'func')
        self.assertEqual(len(func.do_while_loops), 1)
        self.assertTrue(func.do_while_loops[0].is_do_while_loop())
        self.assertEqual(func.do_while_loops[0].condition, 1)

    def test_assignments_returns_all_assignments(self):
        func = self.get_func("""
            int func() {
                int a = 5;
                a = 6;
                int b = 2;
                b = b + a;
            }
        """, 'func')
        self.assertEqual(len(func.assignments), 4)
        self.assertEqual(func.assignments['a = 5'].lhs, 'a')
        self.assertEqual(func.assignments['a = 6'].rhs, '6')
        self.assertEqual(func.assignments['b = 2'].lhs, 'b')
        self.assertEqual(func.assignments['b = b + a'].rhs, 'b + a')

    def test_dump_calls_dump_to_with_stdout(self):
        func = self.get_func('int func(void) {}', 'func')
        func.dump_to = mock.Mock()
        func.dump()
        func.dump_to.assert_called_once_with(sys.stdout)

    def test_dump_to(self):
        stream = io.StringIO()
        function = self.get_func("""
            float foo(int a) {
                int i;
                i = 8;
                double pi = 3.14;

                for(int i = 0; i < 10; i++) {
                    for(int j = 0; j < 10; j++) {
                        ;
                    }

                    if(1) {
                        abc();
                        i = 5;

                        while(35) {
                            ;
                        }
                    }
                }

                while(6) {
                    if(1 > 2) {
                        abc();
                    }
                }

                xyz: ;
                ijk: ;

                switch(i) {
                    case 25:
                        goto xyz;
                        break;
                    default:
                        goto ijk;
                }

                do {} while(7);

                return 42.0;
            }
        """, 'foo')
        function.dump_to(stream)
        self.assertEqual(
            stream.getvalue(),
            dedent("""\
                float foo(int a)

                Called functions:
                -----------------
                abc

                For loops:
                ----------
                for (int i = 0; i < 10; i++)
                for (int j = 0; j < 10; j++)

                While loops:
                ------------
                while (35)
                while (6)

                Do while loops:
                ---------------
                do while (7)

                Assignments:
                ------------
                i = 8
                double pi = 3.14
                int i = 0
                int j = 0
                i = 5

                Variable definitions:
                ---------------------
                int i
                double pi = 3.14
                int i = 0
                int j = 0

                If statements:
                --------------
                if (1)
                if (1 > 2)

                Return statements:
                ------------------
                return 42.0

                Switch statements:
                ------------------
                switch(i) {
                    case 25
                    default
                }

                Goto statements:
                ----------------
                goto xyz
                goto ijk

                Labels:
                -------
                xyz:
                ijk:

                Empty statement count:
                ----------------------
                4
                """)
        )

    def test_repr_returns_correct_repr(self):
        func = self.get_func("""
            int func(float f, char c) {
                return 42;
            }
        """, 'func')
        self.assertEqual(repr(func), "<Function name=func return_type=int params=[float f, char c]>")

    def test_str_returns_correct_str(self):
        func = self.get_func("""
            int func(float f, char c) {
                return 42;
            }
        """, 'func')
        self.assertEqual(str(func), "int func(float f, char c)")

    def test_exception_is_raised_when_searching_statements_and_none_specified(self):
        func = self.get_func("""
            void func() {
                if (0) {}
            }
        """, 'func')
        with self.assertRaises(AssertionError):
            func.has_if_stmts()
