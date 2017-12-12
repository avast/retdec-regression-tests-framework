"""
    Tests for the :module`regression_tests.parsers.c_parser.module` module.
"""

import io
import re
import sys
from textwrap import dedent
from unittest import mock

from regression_tests.utils.list import NamedObjectList
from tests.parsers.c_parser import WithModuleTests


class ModuleTests(WithModuleTests):
    """Tests for `Module`."""

    def test_code_returns_original_source_code(self):
        CODE = 'int main() {}'
        module = self.parse(CODE)
        self.assertEqual(module.code, CODE)

    def test_file_name_returns_original_file_name(self):
        FILE_NAME = 'test.c'
        module = self.parse('int main() {}', FILE_NAME)
        self.assertEqual(module.file_name, FILE_NAME)

    def test_has_parse_errors_returns_false_when_no_errors(self):
        module = self.parse('int main() { return 0; }')
        self.assertFalse(module.has_parse_errors())

    def test_has_parse_errors_returns_true_when_some_error(self):
        module = self.parse('int main() { abcd }')
        self.assertTrue(module.has_parse_errors())

    def test_global_vars_returns_empty_list_when_no_global_vars(self):
        module = self.parse('')
        self.assertEqual(len(module.global_vars), 0)

    def test_global_vars_returns_list_with_two_items_when_two_global_vars(self):
        module = self.parse("""
            int a;
            int b;
        """)
        self.assertEqual(len(module.global_vars), 2)

    def test_global_vars_returns_correct_variable_when_one_variable_with_initializer(self):
        module = self.parse("""
            int a = 1;
        """)
        var = module.global_vars[0]
        self.assertEqual(var.name, 'a')
        self.assertTrue(var.type.is_int())
        self.assertEqual(var.initializer.value, 1)

    def test_global_vars_returns_correct_var_when_var_is_array_with_initializer(self):
        module = self.parse("""
            char *p[] = {
                "aaaa",
                "bbbb"
            };
        """)
        var = module.global_vars[0]
        self.assertEqual(var.name, 'p')
        self.assertTrue(var.type.is_array())
        self.assertTrue(var.type.element_type.is_pointer())
        self.assertTrue(var.type.element_type.pointed_type.is_char())
        self.assertEqual(len(var.initializer), 2)
        self.assertEqual(var.initializer[0], "aaaa")
        self.assertEqual(var.initializer[1], 'bbbb')

    def test_global_vars_returns_correct_var_when_var_is_struct_with_initializer(self):
        module = self.parse("""
            struct S {
                int a;
                double d;
            };
            struct S s1 = {2, 5.7};
        """)
        var = module.global_vars[0]
        self.assertEqual(var.name, 's1')
        self.assertTrue(var.type.is_struct())
        self.assertEqual(len(var.initializer), 2)
        self.assertEqual(var.initializer[0], 2)
        self.assertEqual(var.initializer[1], 5.7)

    def test_global_vars_returns_named_object_list(self):
        module = self.parse("""
            int a;
            int b;
        """)
        self.assertIsInstance(module.global_vars, NamedObjectList)

    def test_global_var_names_returns_global_var_names(self):
        module = self.parse("""
            int a;
            int b;
            int c;
        """)
        self.assertEqual(module.global_var_names, ['a', 'b', 'c'])

    def test_global_var_count_returns_zero_when_no_global_vars(self):
        module = self.parse('')
        self.assertEqual(module.global_var_count, 0)

    def test_global_var_count_returns_two_when_two_global_vars(self):
        module = self.parse("""
            int a;
            int b;
        """)
        self.assertEqual(module.global_var_count, 2)

    def test_has_global_vars_without_names_returns_false_when_no_global_vars(self):
        module = self.parse('')
        self.assertFalse(module.has_global_vars())

    def test_has_global_vars_without_names_returns_true_when_there_are_global_vars(self):
        module = self.parse('int g;')
        self.assertTrue(module.has_global_vars())

    def test_has_global_vars_with_single_empty_list_checks_presence_of_at_least_one_global_var(self):
        module = self.parse('int g;')
        self.assertTrue(module.has_global_vars([]))

    def test_has_global_vars_returns_true_when_all_given_global_vars_are_present(self):
        module = self.parse("""
            int g1;
            int g2;
            int g3;
        """)
        self.assertTrue(module.has_global_vars('g1', 'g2'))

    def test_has_global_vars_returns_true_when_all_given_global_vars_passed_as_list_are_present(self):
        module = self.parse("""
            int g1;
            int g2;
            int g3;
        """)
        self.assertTrue(module.has_global_vars(['g1', 'g2']))

    def test_has_global_vars_disregards_order(self):
        module = self.parse("""
            int g1;
            int g2;
            int g3;
        """)
        self.assertTrue(module.has_global_vars('g2', 'g1'))

    def test_has_global_vars_returns_false_when_not_all_given_global_vars_are_present(self):
        module = self.parse("""
            int g1;
            int g3;
        """)
        self.assertFalse(module.has_global_vars('g1', 'g2'))

    def test_has_global_vars_can_be_called_with_variable_object_as_argument(self):
        module = self.parse("""
            int g1;
            int g2;
        """)
        var1 = self.get_var('int', 'g1')
        self.assertTrue(module.has_global_vars(var1, 'g2'))

    def test_has_no_global_vars_returns_true_when_no_global_vars(self):
        module = self.parse('')
        self.assertTrue(module.has_no_global_vars())

    def test_has_no_global_vars_returns_false_when_there_are_global_vars(self):
        module = self.parse('int a;')
        self.assertFalse(module.has_no_global_vars())

    def test_has_just_global_vars_returns_true_when_no_global_vars_and_no_global_vars_given(self):
        module = self.parse('')
        self.assertTrue(module.has_just_global_vars())

    def test_has_just_global_vars_returns_false_when_no_global_vars_and_global_var_given(self):
        module = self.parse('')
        self.assertFalse(module.has_just_global_vars('g1'))

    def test_has_just_global_vars_returns_false_when_more_global_vars_are_present(self):
        module = self.parse("""
            int g1;
            int g2;
        """)
        self.assertFalse(module.has_just_global_vars('g1'))

    def test_has_just_global_vars_returns_true_when_just_given_global_vars_are_present(self):
        module = self.parse("""
            int g1;
            int g2;
        """)
        self.assertTrue(module.has_just_global_vars('g1', 'g2'))

    def test_has_just_global_vars_disregards_order(self):
        module = self.parse("""
            int g1;
            int g2;
        """)
        self.assertTrue(module.has_just_global_vars('g2', 'g1'))

    def test_has_just_global_vars_global_var_can_be_passed_in_list(self):
        module = self.parse("""
            int g1;
            int g2;
        """)
        self.assertTrue(module.has_just_global_vars(['g2', 'g1']))

    def test_has_just_global_vars_global_var_can_be_passed_in_set(self):
        module = self.parse("""
            int g1;
            int g2;
        """)
        self.assertTrue(module.has_just_global_vars({'g2', 'g1'}))

    def test_has_just_global_vars_can_be_called_with_variable_object_as_argument(self):
        module = self.parse("""
            int g1;
            int g2;
        """)
        var1 = self.get_var('int', 'g1')
        self.assertTrue(module.has_just_global_vars(var1, 'g2'))

    def test_has_global_var_returns_true_when_global_var_exists(self):
        module = self.parse('int a;')
        self.assertTrue(module.has_global_var('a'))

    def test_has_global_var_can_be_called_with_variable_object_as_argument(self):
        module = self.parse('int a;')
        var = self.get_var('int', 'a')
        self.assertTrue(module.has_global_var(var))

    def test_global_vars_with_initializers_are_not_recognized_as_funcs(self):
        module = self.parse("""
            int a = 1;
        """)
        self.assertEqual(module.global_var_count, 1)
        self.assertEqual(module.func_count, 0)

    def test_global_var_array_initializer_compared_to_list(self):
        module = self.parse("""
            int array[3] = {1, 2, 3};
        """)
        self.assertEqual(module.global_vars[0].initializer, [1, 2, 3])

    def test_global_var_array_initializer_float_is_not_equal_to_int(self):
        module = self.parse("""
            float array[3] = {1, 2.0, 3};
        """)
        self.assertNotEqual(module.global_vars[0].initializer, '[1, 2, 3]')

    def test_funcs_returns_empty_list_when_no_funcs(self):
        module = self.parse('')
        self.assertEqual(len(module.funcs), 0)

    def test_funcs_returns_two_funcs_when_two_funcs(self):
        module = self.parse("""
            void func1() {}
            void func2() {}
        """)
        self.assertEqual(len(module.funcs), 2)

    def test_funcs_ignores_declarations(self):
        module = self.parse('int func();')
        self.assertEqual(len(module.funcs), 0)

    def test_funcs_ignores_structures(self):
        module = self.parse('struct X { int a; };')
        self.assertEqual(len(module.funcs), 0)

    def test_funcs_ignores_external_funcs_from_headers(self):
        module = self.parse('#include <stdio.h>')
        self.assertEqual(len(module.funcs), 0)

    def test_funcs_returns_named_object_list(self):
        module = self.parse("""
            void func1() {}
            void func2() {}
        """)
        self.assertIsInstance(module.funcs, NamedObjectList)

    def test_funcs_returns_list_with_correct_type_of_parameter_which_is_struct(self):
        module = self.parse("""
            struct X { int a; };
            void func(struct X x) {}
        """)
        param_type = module.funcs[0].params[0].type
        self.assertTrue(param_type.is_struct())
        self.assertEqual(param_type.name, 'X')

    def test_func_raises_exception_when_no_such_function_is_found(self):
        module = self.parse("""
            void func() {}
        """)
        with self.assertRaises(AssertionError):
            module.func('a', 'b')

    def test_func_returns_first_func_when_both_of_them_exist(self):
        module = self.parse("""
            void func() {}
            void _func() {}
        """)
        self.assertEqual(module.func('func', '_func').name, 'func')

    def test_func_returns_second_func_when_first_does_not_exist(self):
        module = self.parse("""
            void _func() {}
        """)
        self.assertEqual(module.func('func', '_func').name, '_func')

    def test_func_can_be_called_with_function_object_as_argument(self):
        code = """
            void _func() {}
        """
        module = self.parse(code)
        fn = self.get_func(code, '_func')
        self.assertEqual(module.func(fn).name, '_func')

    def test_func_raises_exception_when_no_function_name_is_given(self):
        module = self.parse("""
            void func() {}
        """)
        with self.assertRaises(AssertionError):
            module.func()

    def test_has_funcs_without_names_returns_false_when_no_funcs(self):
        module = self.parse('')
        self.assertFalse(module.has_funcs())

    def test_has_funcs_without_names_returns_true_when_there_are_funcs(self):
        module = self.parse('void func() {}')
        self.assertTrue(module.has_funcs())

    def test_has_funcs_with_single_empty_list_checks_presence_of_at_least_one_func(self):
        module = self.parse('void func() {}')
        self.assertTrue(module.has_funcs([]))

    def test_has_funcs_returns_true_when_all_given_funcs_are_present(self):
        module = self.parse("""
            void func1() {}
            void func2() {}
            void func3() {}
        """)
        self.assertTrue(module.has_funcs('func1', 'func2'))

    def test_has_funcs_returns_true_when_all_given_funcs_passed_as_list_are_present(self):
        module = self.parse("""
            void func1() {}
            void func2() {}
            void func3() {}
        """)
        self.assertTrue(module.has_funcs(['func1', 'func2']))

    def test_has_funcs_disrgards_order(self):
        module = self.parse("""
            void func1() {}
            void func2() {}
            void func3() {}
        """)
        self.assertTrue(module.has_funcs('func2', 'func1'))

    def test_has_funcs_returns_false_when_not_all_given_funcs_are_present(self):
        module = self.parse("""
            void func1() {}
            void func3() {}
        """)
        self.assertFalse(module.has_funcs('func1', 'func2'))

    def test_has_funcs_can_be_called_with_function_object_as_argument(self):
        code = """
            void func1() {}
            void func2() {}
        """
        module = self.parse(code)
        fn = self.get_func(code, 'func2')
        self.assertTrue(module.has_funcs('func1', fn))

    def test_has_no_funcs_returns_true_when_no_funcs(self):
        module = self.parse('')
        self.assertTrue(module.has_no_funcs())

    def test_has_no_funcs_returns_false_when_there_are_funcs(self):
        module = self.parse('void func() {}')
        self.assertFalse(module.has_no_funcs())

    def test_has_just_funcs_returns_true_when_no_funcs_and_no_funcs_given(self):
        module = self.parse('')
        self.assertTrue(module.has_just_funcs())

    def test_has_just_funcs_returns_false_when_no_funcs_and_func_given(self):
        module = self.parse('')
        self.assertFalse(module.has_just_funcs('func'))

    def test_has_just_funcs_returns_false_when_more_funcs_are_present(self):
        module = self.parse("""
            int func1() {}
            int func2() {}
        """)
        self.assertFalse(module.has_just_funcs('func1'))

    def test_has_just_funcs_returns_true_when_just_given_funcs_are_present(self):
        module = self.parse("""
            int func1() {}
            int func2() {}
        """)
        self.assertTrue(module.has_just_funcs('func1', 'func2'))

    def test_has_just_funcs_disregards_order(self):
        module = self.parse("""
            int func1() {}
            int func2() {}
        """)
        self.assertTrue(module.has_just_funcs('func2', 'func1'))

    def test_has_just_funcs_func_can_be_passed_in_list(self):
        module = self.parse("""
            int func1() {}
            int func2() {}
        """)
        self.assertTrue(module.has_just_funcs(['func2', 'func1']))

    def test_has_just_funcs_func_can_be_passed_in_set(self):
        module = self.parse("""
            int func1() {}
            int func2() {}
        """)
        self.assertTrue(module.has_just_funcs({'func2', 'func1'}))

    def test_has_just_funcs_can_be_called_with_function_object_as_argument(self):
        code = """
            void func1() {}
            void func2() {}
        """
        module = self.parse(code)
        fn = self.get_func(code, 'func2')
        self.assertTrue(module.has_just_funcs('func1', fn))

    def test_has_func_returns_true_when_func_exists(self):
        module = self.parse('void func() {}')
        self.assertTrue(module.has_func('func'))

    def test_has_func_returns_false_when_no_such_func(self):
        module = self.parse('')
        self.assertFalse(module.has_func('func'))

    def test_has_func_matching_returns_true_when_func_matches(self):
        module = self.parse('''
            void func1() {}
            void _func2() {}
        ''')
        self.assertTrue(module.has_func_matching(r'_?func1'))
        self.assertTrue(module.has_func_matching(r'_?func2'))

    def test_has_func_matching_returns_false_when_func_does_not_match(self):
        module = self.parse('void func() {}')
        self.assertFalse(module.has_func_matching(r'foo'))

    def test_has_func_matching_checks_whole_name(self):
        module = self.parse('void func() {}')
        self.assertFalse(module.has_func_matching(r''))
        self.assertFalse(module.has_func_matching(r'f'))
        self.assertFalse(module.has_func_matching(r'fu'))
        self.assertFalse(module.has_func_matching(r'fun'))
        self.assertTrue(module.has_func_matching(r'func'))

    def test_func_names_returns_func_names(self):
        module = self.parse("""
            void func1() {}
            void func2() {}
            void func3() {}
        """)
        self.assertEqual(module.func_names, ['func1', 'func2', 'func3'])

    def test_func_count_returns_zero_when_no_funcs(self):
        module = self.parse('')
        self.assertEqual(module.func_count, 0)

    def test_func_count_returns_two_when_two_funcs(self):
        module = self.parse("""
            void func1() {}
            void func2() {}
        """)
        self.assertEqual(module.func_count, 2)

    def test_funcs_are_not_recognized_as_global_vars(self):
        module = self.parse("""
            int func() {}
        """)
        self.assertEqual(module.func_count, 1)
        self.assertEqual(module.global_var_count, 0)

    def test_comments_returns_empty_list_when_no_comments(self):
        module = self.parse('int main() {}')
        self.assertEqual(len(module.comments), 0)

    def test_comments_returns_two_comments_when_two_comments(self):
        module = self.parse("""
            // before
            int main() {
               // inside
            }
        """)
        self.assertEqual(module.comments, ['// before', '// inside'])

    def test_hash_comment_matching_returns_true_when_comment_matches(self):
        module = self.parse("""
            // test
        """)
        self.assertTrue(module.has_comment_matching(r'// test'))

    def test_hash_comment_matching_returns_false_when_comment_does_not_match(self):
        module = self.parse("""
            // test
        """)
        self.assertFalse(module.has_comment_matching(r'test'))

    def test_hash_comment_matching_checks_whole_comment(self):
        module = self.parse("""
            // test
        """)
        self.assertFalse(module.has_comment_matching(r''))
        self.assertFalse(module.has_comment_matching(r'/'))
        self.assertFalse(module.has_comment_matching(r'// tes'))
        self.assertTrue(module.has_comment_matching(r'// test'))

    def test_includes_returns_empty_list_when_no_includes(self):
        module = self.parse('int i;')
        self.assertEqual(len(module.includes), 0)

    def test_includes_returns_correct_result_when_one_include_with_angle_brackets(self):
        module = self.parse("""
            #include <stdio.h>
        """)
        self.assertEqual(len(module.includes), 1)
        self.assertEqual(module.includes[0], '#include <stdio.h>')

    def test_includes_returns_correct_result_when_one_include_with_quotes(self):
        module = self.parse("""
            #include "stdio.h"
        """)
        self.assertEqual(len(module.includes), 1)
        self.assertEqual(module.includes[0], '#include "stdio.h"')

    def test_includes_returns_list_with_two_includes_when_two_includes(self):
        module = self.parse("""
            #include <stdio.h>
            #include <stdlib.h>
        """)
        self.assertEqual(len(module.includes), 2)

    def test_has_include_of_file_returns_true_when_include_exists(self):
        module = self.parse("""
            #include <stdio.h>
        """)
        self.assertTrue(module.has_include_of_file('stdio.h'))

    def test_has_include_of_file_returns_false_when_include_does_not_exist(self):
        module = self.parse('')
        self.assertFalse(module.has_include_of_file('stdio.h'))

    def test_string_literal_values_returns_empty_set_if_no_literals(self):
        module = self.parse('')
        self.assertEqual(module.string_literal_values, set())

    def test_string_literal_values_returns_correct_set_when_two_string_literals(self):
        module = self.parse("""
            #include <stdio.h>

            void func() {
                printf("str1");
                printf("str2");
            }
        """)
        self.assertEqual(module.string_literal_values, {'str1', 'str2'})

    def test_string_literal_values_include_wide_string_literals(self):
        module = self.parse("""
            #include <stdio.h>
            #include <wchar.h>

            void func() {
                wprintf(L"wide string");
            }
        """)
        self.assertEqual(module.string_literal_values, {'wide string'})

    def test_string_literal_values_does_not_consider_nan_as_string(self):
        # There seems to be a bug in clang (cindex) that causes NAN, which
        # expands to __builtin_nanf, to be considered a string literal. This
        # test checks that we correctly detect and handle such situations.
        module = self.parse("""
            #include <math.h>

            float my_nan = NAN;
        """)
        self.assertEqual(module.string_literal_values, set())

    def test_has_string_literal_returns_false_when_no_such_literal(self):
        module = self.parse('')
        self.assertFalse(module.has_string_literal('contents'))

    def test_has_string_literal_returns_true_when_literal_in_global_var_initializer(self):
        module = self.parse("""
            const char *msg = "test me";
        """)
        self.assertTrue(module.has_string_literal('test me'))

    def test_has_string_literal_returns_true_when_literal_in_function_body(self):
        module = self.parse("""
            #include <stdio.h>

            void func() {
                if (1) {
                    printf("Answer is: %d", 42);
                }
            }
        """)
        self.assertTrue(module.has_string_literal('Answer is: %d'))

    def test_has_string_literal_returns_true_even_when_error(self):
        module = self.parse("""
            int main() {
                if (undefined_variable) {
                    puts("hello");
                }
            }
        """)
        self.assertTrue(module.has_string_literal('hello'))

    def test_has_string_literal_returns_true_when_literal_in_comment(self):
        # This is a side-effect of using contains() to check the presence of
        # the literal.
        module = self.parse("""
            // "hello"
        """)
        self.assertTrue(module.has_string_literal('hello'))

    def test_has_string_literal_returns_false_when_literal_without_quotes(self):
        module = self.parse("""
            int main() {
                if (undefined_variable) {
                    puts(hello);
                }
            }
        """)
        self.assertFalse(module.has_string_literal('hello'))

    def test_has_string_literal_escapes_passed_value_before_calling_contains(self):
        module = self.parse("""
            int main() {
                if (undefined_variable) {
                    puts("$^()[]{}.*+?");
                }
            }
        """)
        self.assertTrue(module.has_string_literal('$^()[]{}.*+?'))

    def test_has_string_literal_matching_returns_false_when_no_such_literal(self):
        module = self.parse('')
        self.assertFalse(module.has_string_literal_matching(r'.*'))

    def test_has_string_literal_matching_returns_true_when_literal_in_global_var_initializer(self):
        module = self.parse("""
            const char *msg = "test me";
        """)
        self.assertTrue(module.has_string_literal_matching(r'te.. me'))

    def test_has_string_literal_matching_returns_true_when_literal_in_function_body(self):
        module = self.parse("""
            #include <stdio.h>

            void func() {
                if (1) {
                    printf("Answer is: %d", 42);
                }
            }
        """)
        self.assertTrue(module.has_string_literal_matching('Answer is: .*'))

    def test_has_string_literal_matching_returns_true_even_when_error(self):
        module = self.parse("""
            int main() {
                if (undefined_variable) {
                    puts("hello");
                }
            }
        """)
        self.assertTrue(module.has_string_literal_matching(r'he[l]+o'))

    def test_has_string_literal_matching_returns_true_when_literal_in_comment(self):
        # This is a side-effect of using contains() to check the presence of
        # the literal.
        module = self.parse("""
            // "hello"
        """)
        self.assertTrue(module.has_string_literal_matching(r'he[l]+o'))

    def test_has_string_literal_matching_returns_false_when_literal_without_quotes(self):
        module = self.parse("""
            int main() {
                if (undefined_variable) {
                    puts(hello);
                }
            }
        """)
        self.assertFalse(module.has_string_literal_matching(r'he[l]+o'))

    def test_has_string_literal_matching_properly_handles_caret_and_dollar_in_regexp(self):
        module = self.parse("""
            int main() {
                if (undefined_variable) {
                    puts("hello");
                }
            }
        """)
        # A caret ('^') marks the beginning of the string and a dollar ('$')
        # marks the end.
        self.assertTrue(module.has_string_literal_matching(r'^hello$'))

    def test_has_string_literal_matching_works_even_if_regexep_is_compiled(self):
        module = self.parse("""
            int main() {
                if (undefined_variable) {
                    puts("hello");
                }
            }
        """)
        self.assertTrue(module.has_string_literal_matching(re.compile(r'^hello$')))

    def test_has_any_global_vars_returns_false_when_no_code(self):
        module = self.parse("")
        self.assertFalse(module.has_any_global_vars())

    def test_has_any_global_vars_returns_true_when_global_variable_present(self):
        module = self.parse("""
            int i;
        """)
        self.assertTrue(module.has_any_global_vars())

    def test_structs_returns_empty_list_when_no_structs(self):
        module = self.parse('')
        self.assertEqual(len(module.structs), 0)
        self.assertEqual(len(module.unnamed_structs), 0)
        self.assertEqual(len(module.named_structs), 0)

    def test_structs_returns_list_with_two_items_when_two_structs(self):
        module = self.parse("""
            struct {int a};
            struct S {int b};
        """)
        self.assertEqual(len(module.structs), 2)

    def test_unnamed_structs_returns_list_with_one_items_when_two_structs_and_only_one_unnamed(self):
        module = self.parse("""
            struct {int a};
            struct S {int b};
        """)
        self.assertEqual(len(module.unnamed_structs), 1)

    def test_named_structs_returns_list_with_one_items_when_two_structs_and_only_one_named(self):
        module = self.parse("""
            struct {int a};
            struct S {int b};
        """)
        self.assertEqual(len(module.named_structs), 1)

    def test_unnamed_structs_returns_correct_struct_when_one_unnamed_struct(self):
        module = self.parse("""
            struct {int a};
        """)
        struct = module.unnamed_structs[0]
        self.assertIsNone(struct.name)
        self.assertEqual(struct.member_count, 1)
        self.assertEqual(struct.member_names[0], 'a')

    def test_named_structs_returns_correct_struct_when_one_named_struct(self):
        module = self.parse("""
            struct S {int a};
        """)
        struct = module.named_structs[0]
        self.assertEqual(struct.name, 'S')
        self.assertEqual(struct.member_count, 1)
        self.assertEqual(struct.member_names[0], 'a')

    def test_named_structs_returns_named_object_list(self):
        module = self.parse("""
            struct S {int a};
        """)
        self.assertIsInstance(module.named_structs, NamedObjectList)

    def test_named_structs_returns_named_structs_names(self):
        module = self.parse("""
            struct S1 {int a};
            struct S2 {int a};
        """)
        self.assertEqual(module.struct_names, ['S1', 'S2'])

    def test_struct_count_returns_zero_when_no_structs(self):
        module = self.parse('')
        self.assertEqual(module.struct_count, 0)
        self.assertEqual(module.unnamed_struct_count, 0)
        self.assertEqual(module.named_struct_count, 0)

    def test_named_struct_count_returns_zero_when_no_named_structs(self):
        module = self.parse("""
            struct {int a};
        """)
        self.assertEqual(module.named_struct_count, 0)

    def test_unnamed_struct_count_returns_zero_when_no_unnamed_structs(self):
        module = self.parse("""
            struct S {int a};
        """)
        self.assertEqual(module.unnamed_struct_count, 0)

    def test_counters_return_correct_values_when_one_named_struct_and_two_unnamed_structs(self):
        module = self.parse("""
            struct {char c};
            struct S {int a};
            struct {double d};
        """)
        self.assertEqual(module.struct_count, 3)
        self.assertEqual(module.unnamed_struct_count, 2)
        self.assertEqual(module.named_struct_count, 1)

    def test_has_structs_returns_false_when_no_structs(self):
        module = self.parse('')
        self.assertFalse(module.has_any_structs())
        self.assertFalse(module.has_any_named_structs())
        self.assertFalse(module.has_any_unnamed_structs())

    def test_has_structs_returns_true_when_there_are_structs(self):
        module = self.parse("""
            struct {char c};
            struct S {int a};
        """)
        self.assertTrue(module.has_any_structs())
        self.assertTrue(module.has_any_unnamed_structs())
        self.assertTrue(module.has_any_named_structs())

    def test_has_named_structs_with_empty_list_checks_presence_of_at_least_one_named_struct(self):
        module = self.parse("""
            struct S {int a};
        """)
        self.assertTrue(module.has_named_structs([]))

    def test_has_named_structs_returns_true_when_all_given_named_structs_are_present(self):
        module = self.parse("""
            struct S {int a};
            struct SO {int a};
            struct SOS {int a};
        """)
        self.assertTrue(module.has_named_structs('S', 'SOS'))

    def test_has_named_structs_returns_true_when_all_given_named_structs_passed_as_list_are_present(self):
        module = self.parse("""
            struct S {int a};
            struct SO {int a};
            struct SOS {int a};
        """)
        self.assertTrue(module.has_named_structs(['S', 'SOS']))

    def test_has_named_structs_disregards_order(self):
        module = self.parse("""
            struct S {int a};
            struct SO {int a};
            struct SOS {int a};
        """)
        self.assertTrue(module.has_named_structs('SOS', 'S'))

    def test_has_named_structs_returns_false_when_not_all_given_named_structs_are_present(self):
        module = self.parse("""
            struct S {int a};
            struct SO {int a};
        """)
        self.assertFalse(module.has_named_structs('SOS', 'S'))

    def test_has_named_structs_can_be_called_with_struct_object_as_argument(self):
        code = """
            struct S {int a};
            struct SO {int a};
        """
        module = self.parse(code)
        struct = self.get_named_struct(code, 'SO')
        self.assertTrue(module.has_named_structs('S', struct))

    def test_has_no_structs_returns_true_when_no_structs(self):
        module = self.parse('')
        self.assertTrue(module.has_no_structs())
        self.assertTrue(module.has_no_unnamed_structs())
        self.assertTrue(module.has_no_named_structs())

    def test_has_no_structs_returns_false_when_there_are_structs(self):
        module = self.parse("""
            struct S {int a};
            struct {int a};
        """)
        self.assertFalse(module.has_no_structs())
        self.assertFalse(module.has_no_unnamed_structs())
        self.assertFalse(module.has_no_named_structs())

    def test_has_just_named_structs_returns_true_when_no_named_structs_and_no_named_structs_given(self):
        module = self.parse('')
        self.assertTrue(module.has_just_named_structs())

    def test_has_just_named_structs_returns_false_when_no_named_structs_and_named_struct_given(self):
        module = self.parse('')
        self.assertFalse(module.has_just_named_structs('S'))

    def test_has_just_named_structs_returns_false_when_more_named_structs_are_present(self):
        module = self.parse("""
            struct S {int a};
            struct S2 {int a};
        """)
        self.assertFalse(module.has_just_named_structs('S'))

    def test_has_just_named_structs_returns_true_when_just_given_named_structs_are_present(self):
        module = self.parse("""
            struct S {int a};
            struct S2 {int a};
        """)
        self.assertTrue(module.has_just_named_structs('S', 'S2'))

    def test_has_just_named_structs_disregards_order(self):
        module = self.parse("""
            struct S {int a};
            struct S2 {int a};
        """)
        self.assertTrue(module.has_just_named_structs('S2', 'S'))

    def test_has_just_named_structs_can_be_passed_in_list(self):
        module = self.parse("""
            struct S {int a};
            struct S2 {int a};
        """)
        self.assertTrue(module.has_just_named_structs(['S2', 'S']))

    def test_has_just_named_structs_can_be_passed_in_set(self):
        module = self.parse("""
            struct S {int a};
            struct S2 {int a};
        """)
        self.assertTrue(module.has_just_named_structs({'S2', 'S'}))

    def test_has_just_named_structs_disregards_unnamed_structs(self):
        module = self.parse("""
            struct S {int a};
            struct S2 {int a};
            struct {double d};
        """)
        self.assertTrue(module.has_just_named_structs('S', 'S2'))

    def test_has_just_named_structs_can_be_called_with_struct_object_as_argument(self):
        code = """
            struct S {int a};
            struct SO {int a};
        """
        module = self.parse(code)
        struct = self.get_named_struct(code, 'SO')
        self.assertTrue(module.has_just_named_structs('S', struct))

    def test_has_named_struct_returns_true_when_named_struct_exists(self):
        module = self.parse("""
            struct S {int a};
            struct S2 {int a};
        """)
        self.assertTrue(module.has_named_struct('S'))

    def test_has_named_struct_returns_false_when_named_struct_does_not_exist(self):
        module = self.parse('')
        self.assertFalse(module.has_named_struct('S'))

    def test_has_named_struct_can_be_called_with_struct_object_as_argument(self):
        code = """
            struct S {int a};
            struct SO {int a};
        """
        module = self.parse(code)
        struct = self.get_named_struct(code, 'SO')
        self.assertTrue(module.has_named_struct(struct))

    def test_unions_returns_empty_list_when_no_unions(self):
        module = self.parse('')
        self.assertEqual(len(module.unions), 0)
        self.assertEqual(len(module.unnamed_unions), 0)
        self.assertEqual(len(module.named_unions), 0)

    def test_unions_returns_list_with_two_items_when_two_unions(self):
        module = self.parse("""
            union {int a};
            union U {int b};
        """)
        self.assertEqual(len(module.unions), 2)

    def test_unnamed_unions_returns_list_with_one_items_when_two_unions_and_only_one_unnamed(self):
        module = self.parse("""
            union {int a};
            union U {int b};
        """)
        self.assertEqual(len(module.unnamed_unions), 1)

    def test_named_unions_returns_list_with_one_items_when_two_unions_and_only_one_named(self):
        module = self.parse("""
            union {int a};
            union U {int b};
        """)
        self.assertEqual(len(module.named_unions), 1)

    def test_unnamed_unions_returns_correct_union_when_one_unnamed_union(self):
        module = self.parse("""
            union {int a};
        """)
        union = module.unnamed_unions[0]
        self.assertIsNone(union.name)
        self.assertEqual(union.member_count, 1)
        self.assertEqual(union.member_names[0], 'a')

    def test_named_unions_returns_correct_union_when_one_named_union(self):
        module = self.parse("""
            union U {int a};
        """)
        union = module.named_unions[0]
        self.assertEqual(union.name, 'U')
        self.assertEqual(union.member_count, 1)
        self.assertEqual(union.member_names[0], 'a')

    def test_named_unions_returns_named_object_list(self):
        module = self.parse("""
            union U {int a};
        """)
        self.assertIsInstance(module.named_unions, NamedObjectList)

    def test_named_unions_returns_named_unions_names(self):
        module = self.parse("""
            union U1 {int a};
            union U2 {int a};
        """)
        self.assertEqual(module.union_names, ['U1', 'U2'])

    def test_union_count_returns_zero_when_no_unions(self):
        module = self.parse('')
        self.assertEqual(module.union_count, 0)
        self.assertEqual(module.unnamed_union_count, 0)
        self.assertEqual(module.named_union_count, 0)

    def test_named_union_count_returns_zero_when_no_named_unions(self):
        module = self.parse("""
            union {int a};
        """)
        self.assertEqual(module.named_union_count, 0)

    def test_unnamed_union_count_returns_zero_when_no_unnamed_unions(self):
        module = self.parse("""
            union U {int a};
        """)
        self.assertEqual(module.unnamed_union_count, 0)

    def test_counters_return_correct_values_when_one_named_union_and_two_unnamed_unions(self):
        module = self.parse("""
            union {char c};
            union U {int a};
            union {double d};
        """)
        self.assertEqual(module.union_count, 3)
        self.assertEqual(module.unnamed_union_count, 2)
        self.assertEqual(module.named_union_count, 1)

    def test_has_unions_returns_false_when_no_unions(self):
        module = self.parse('')
        self.assertFalse(module.has_any_unions())
        self.assertFalse(module.has_any_named_unions())
        self.assertFalse(module.has_any_unnamed_unions())

    def test_has_unions_returns_true_when_there_are_unions(self):
        module = self.parse("""
            union {char c};
            union U {int a};
        """)
        self.assertTrue(module.has_any_unions())
        self.assertTrue(module.has_any_named_unions())
        self.assertTrue(module.has_any_unnamed_unions())

    def test_has_named_unions_with_empty_list_checks_presence_of_at_least_one_named_union(self):
        module = self.parse("""
            union U {int a};
        """)
        self.assertTrue(module.has_named_unions([]))

    def test_has_named_unions_returns_true_when_all_given_named_unions_are_present(self):
        module = self.parse("""
            union U {int a};
            union UO {int a};
            union UOO {int a};
        """)
        self.assertTrue(module.has_named_unions('U', 'UOO'))

    def test_has_named_unions_returns_true_when_all_given_named_unions_passed_as_list_are_present(self):
        module = self.parse("""
            union U {int a};
            union UO {int a};
            union UOO {int a};
        """)
        self.assertTrue(module.has_named_unions(['U', 'UOO']))

    def test_has_named_unions_disregards_order(self):
        module = self.parse("""
            union U {int a};
            union UO {int a};
            union UOO {int a};
        """)
        self.assertTrue(module.has_named_unions('UOO', 'U'))

    def test_has_named_unions_returns_false_when_not_all_given_named_unions_are_present(self):
        module = self.parse("""
            union U {int a};
            union UO {int a};
        """)
        self.assertFalse(module.has_named_unions('UOO', 'U'))

    def test_has_named_unions_can_be_called_with_union_object_as_argument(self):
        code = """
            union U {int a};
            union UO {int a};
        """
        module = self.parse(code)
        union = self.get_named_union(code, 'UO')
        self.assertTrue(module.has_named_unions('U', union))

    def test_has_no_unions_returns_true_when_no_unions(self):
        module = self.parse('')
        self.assertTrue(module.has_no_unions())
        self.assertTrue(module.has_no_unnamed_unions())
        self.assertTrue(module.has_no_named_unions())

    def test_has_no_unions_returns_false_when_there_are_unions(self):
        module = self.parse("""
            union U {int a};
            union {int a};
        """)
        self.assertFalse(module.has_no_unions())
        self.assertFalse(module.has_no_unnamed_unions())
        self.assertFalse(module.has_no_named_unions())

    def test_has_just_named_unions_returns_true_when_no_named_unions_and_no_named_unions_given(self):
        module = self.parse('')
        self.assertTrue(module.has_just_named_unions())

    def test_has_just_named_unions_returns_false_when_no_named_unions_and_named_union_given(self):
        module = self.parse('')
        self.assertFalse(module.has_just_named_unions('U'))

    def test_has_just_named_unions_returns_false_when_more_named_unions_are_present(self):
        module = self.parse("""
            union U {int a};
            union U2 {int a};
        """)
        self.assertFalse(module.has_just_named_unions('U'))

    def test_has_just_named_unions_returns_true_when_just_given_named_unions_are_present(self):
        module = self.parse("""
            union U {int a};
            union U2 {int a};
        """)
        self.assertTrue(module.has_just_named_unions('U', 'U2'))

    def test_has_just_named_unions_disregards_order(self):
        module = self.parse("""
            union U {int a};
            union U2 {int a};
        """)
        self.assertTrue(module.has_just_named_unions('U2', 'U'))

    def test_has_just_named_unions_can_be_passed_in_list(self):
        module = self.parse("""
            union U {int a};
            union U2 {int a};
        """)
        self.assertTrue(module.has_just_named_unions(['U2', 'U']))

    def test_has_just_named_unions_can_be_passed_in_set(self):
        module = self.parse("""
            union U {int a};
            union U2 {int a};
        """)
        self.assertTrue(module.has_just_named_unions({'U2', 'U'}))

    def test_has_just_named_unions_disregards_unnamed_unions(self):
        module = self.parse("""
            union U {int a};
            union U2 {int a};
            union {double d};
        """)
        self.assertTrue(module.has_just_named_unions('U', 'U2'))

    def test_has_just_named_unions_can_be_called_with_union_object_as_argument(self):
        code = """
            union U {int a};
            union UO {int a};
        """
        module = self.parse(code)
        union = self.get_named_union(code, 'UO')
        self.assertTrue(module.has_just_named_unions('U', union))

    def test_has_named_union_returns_true_when_named_union_exists(self):
        module = self.parse("""
            union U {int a};
            union U2 {int a};
        """)
        self.assertTrue(module.has_named_union('U'))

    def test_has_named_union_returns_false_when_named_union_does_not_exist(self):
        module = self.parse('')
        self.assertFalse(module.has_named_unions('U'))

    def test_has_named_union_can_be_called_with_union_object_as_argument(self):
        code = """
            union U {int a};
            union UO {int a};
        """
        module = self.parse(code)
        union = self.get_named_union(code, 'UO')
        self.assertTrue(module.has_named_union(union))

    def test_enums_returns_empty_list_when_no_enums(self):
        module = self.parse('')
        self.assertEqual(len(module.enums), 0)
        self.assertEqual(len(module.unnamed_enums), 0)
        self.assertEqual(len(module.named_enums), 0)

    def test_enums_returns_list_with_two_items_when_two_enums(self):
        module = self.parse("""
            enum {a};
            enum e {b};
        """)
        self.assertEqual(len(module.enums), 2)

    def test_unnamed_enums_returns_list_with_one_items_when_two_enums_and_only_one_unnamed(self):
        module = self.parse("""
            enum {a};
            enum e {b};
        """)
        self.assertEqual(len(module.unnamed_enums), 1)

    def test_named_enums_returns_list_with_one_items_when_two_enums_and_only_one_named(self):
        module = self.parse("""
            enum {a};
            enum e {b};
        """)
        self.assertEqual(len(module.named_enums), 1)

    def test_unnamed_enums_returns_correct_enum_when_one_unnamed_enum(self):
        module = self.parse("""
            enum {a};
        """)
        enum = module.unnamed_enums[0]
        self.assertIsNone(enum.name)
        self.assertEqual(enum.item_count, 1)
        self.assertEqual(enum.item_names[0], 'a')

    def test_named_enums_returns_correct_enum_when_one_named_enum(self):
        module = self.parse("""
            enum e {a};
        """)
        enum = module.named_enums[0]
        self.assertEqual(enum.name, 'e')
        self.assertEqual(enum.item_count, 1)
        self.assertEqual(enum.item_names[0], 'a')

    def test_named_enums_returns_named_object_list(self):
        module = self.parse("""
            enum e {a};
        """)
        self.assertIsInstance(module.named_enums, NamedObjectList)

    def test_named_enums_returns_named_enums_names(self):
        module = self.parse("""
            enum e1 {a};
            enum e2 {a};
        """)
        self.assertEqual(module.enum_names, ['e1', 'e2'])

    def test_enum_count_returns_zero_when_no_enums(self):
        module = self.parse('')
        self.assertEqual(module.enum_count, 0)
        self.assertEqual(module.unnamed_enum_count, 0)
        self.assertEqual(module.named_enum_count, 0)

    def test_named_enum_count_returns_zero_when_no_named_enums(self):
        module = self.parse("""
            enum {a};
        """)
        self.assertEqual(module.named_enum_count, 0)

    def test_unnamed_enum_count_returns_zero_when_no_unnamed_enums(self):
        module = self.parse("""
            enum e {a};
        """)
        self.assertEqual(module.unnamed_enum_count, 0)

    def test_counters_return_correct_values_when_one_named_enum_and_two_unnamed_enums(self):
        module = self.parse("""
            enum {c};
            enum e {a};
            enum {d};
        """)
        self.assertEqual(module.enum_count, 3)
        self.assertEqual(module.unnamed_enum_count, 2)
        self.assertEqual(module.named_enum_count, 1)

    def test_has_enums_returns_false_when_no_enums(self):
        module = self.parse('')
        self.assertFalse(module.has_any_enums())
        self.assertFalse(module.has_any_named_enums())
        self.assertFalse(module.has_any_unnamed_enums())

    def test_has_enums_returns_true_when_there_are_enums(self):
        module = self.parse("""
            enum {c};
            enum e {a};
        """)
        self.assertTrue(module.has_any_enums())
        self.assertTrue(module.has_any_named_enums())
        self.assertTrue(module.has_any_unnamed_enums())

    def test_has_named_enums_with_empty_list_checks_presence_of_at_least_one_named_enum(self):
        module = self.parse("""
            enum e {a};
        """)
        self.assertTrue(module.has_named_enums([]))

    def test_has_named_enums_returns_true_when_all_given_named_enums_are_present(self):
        module = self.parse("""
            enum e {a};
            enum e1 {b};
            enum e2 {c};
        """)
        self.assertTrue(module.has_named_enums('e', 'e2'))

    def test_has_named_enums_returns_true_when_all_given_named_enums_passed_as_list_are_present(self):
        module = self.parse("""
            enum e {a};
            enum e1 {b};
            enum e2 {c};
        """)
        self.assertTrue(module.has_named_enums(['e', 'e2']))

    def test_has_named_enums_disregards_order(self):
        module = self.parse("""
            enum e {a};
            enum e1 {b};
            enum e2 {c};
        """)
        self.assertTrue(module.has_named_enums('e', 'e2'))

    def test_has_named_enums_returns_false_when_not_all_given_named_enums_are_present(self):
        module = self.parse("""
            enum e {a};
            enum e1 {b};
        """)
        self.assertFalse(module.has_named_enums('e2', 'e'))

    def test_has_named_enums_can_be_called_with_enum_object_as_argument(self):
        code = """
            enum e {a};
            enum e1 {b};
        """
        module = self.parse(code)
        enum = self.get_named_enum(code, 'e1')
        self.assertTrue(module.has_named_enums('e', enum))

    def test_has_no_enums_returns_true_when_no_enums(self):
        module = self.parse('')
        self.assertTrue(module.has_no_enums())
        self.assertTrue(module.has_no_unnamed_enums())
        self.assertTrue(module.has_no_named_enums())

    def test_has_no_enums_returns_false_when_there_are_enums(self):
        module = self.parse("""
            enum e {a};
            enum {b};
        """)
        self.assertFalse(module.has_no_enums())
        self.assertFalse(module.has_no_unnamed_enums())
        self.assertFalse(module.has_no_named_enums())

    def test_has_just_named_enums_returns_true_when_no_named_enums_and_no_named_enums_given(self):
        module = self.parse('')
        self.assertTrue(module.has_just_named_enums())

    def test_has_just_named_enums_returns_false_when_no_named_enums_and_named_enum_given(self):
        module = self.parse('')
        self.assertFalse(module.has_just_named_enums('e'))

    def test_has_just_named_enums_returns_false_when_more_named_enums_are_present(self):
        module = self.parse("""
            enum e {a};
            enum e2 {b};
        """)
        self.assertFalse(module.has_just_named_enums('e'))

    def test_has_just_named_enums_returns_true_when_just_given_named_enums_are_present(self):
        module = self.parse("""
            enum e {a};
            enum e2 {b};
        """)
        self.assertTrue(module.has_just_named_enums('e', 'e2'))

    def test_has_just_named_enums_disregards_order(self):
        module = self.parse("""
            enum e {a};
            enum e2 {b};
        """)
        self.assertTrue(module.has_just_named_enums('e2', 'e'))

    def test_has_just_named_enums_can_be_passed_in_list(self):
        module = self.parse("""
            enum e {a};
            enum e2 {b};
        """)
        self.assertTrue(module.has_just_named_enums(['e2', 'e']))

    def test_has_just_named_enums_can_be_passed_in_set(self):
        module = self.parse("""
            enum e {a};
            enum e2 {b};
        """)
        self.assertTrue(module.has_just_named_enums({'e2', 'e'}))

    def test_has_just_named_enums_disregards_unnamed_enums(self):
        module = self.parse("""
            enum e {a};
            enum e2 {b};
            enum {c};
        """)
        self.assertTrue(module.has_just_named_enums('e', 'e2'))

    def test_has_just_named_enums_can_be_called_with_enum_object_as_argument(self):
        code = """
            enum e {a};
            enum e1 {b};
        """
        module = self.parse(code)
        enum = self.get_named_enum(code, 'e1')
        self.assertTrue(module.has_just_named_enums('e', enum))

    def test_has_named_enum_returns_true_when_named_enum_exists(self):
        module = self.parse("""
            enum e {a};
            enum e2 {b};
        """)
        self.assertTrue(module.has_named_enum('e'))

    def test_has_named_enum_returns_false_when_named_enum_does_not_exist(self):
        module = self.parse('')
        self.assertFalse(module.has_named_enums('e'))

    def test_has_named_enum_can_be_called_with_enum_object_as_argument(self):
        code = """
            enum e {a};
            enum e1 {b};
        """
        module = self.parse(code)
        enum = self.get_named_enum(code, 'e1')
        self.assertTrue(module.has_named_enum(enum))

    def test_enum_item_names_returns_names_of_all_items_in_all_enums_in_module(self):
        module = self.parse("""
            enum e {a};
            enum e2 {b};
            enum {c};
        """)
        self.assertEqual(module.enum_item_names, ['a', 'b', 'c'])

    def test_enum_item_count_returns_correct_value(self):
        module = self.parse("""
            enum e {a};
            enum e2 {b};
            enum {c};
        """)
        self.assertEqual(module.enum_item_count, 3)

    def test_empty_enums_returns_empty_enums(self):
        module = self.parse("""
            enum e {a};
            enum e2 {};
            enum e3 {c};
        """)
        self.assertEqual(len(module.empty_enums), 1)
        self.assertEqual(module.empty_enums[0].name, 'e2')

    def test_empty_enum_count_returns_correct_value(self):
        module = self.parse("""
            enum e {a};
            enum e2 {};
            enum e3 {c};
        """)
        self.assertEqual(module.empty_enum_count, 1)

    def test_has_any_empty_enums_returns_true_when_empty_enums(self):
        module = self.parse("""
            enum {};
        """)
        self.assertTrue(module.has_any_empty_enums())

    def test_has_any_empty_enums_returns_false_when_no_empty_enums(self):
        module = self.parse("""
            enum {a};
        """)
        self.assertFalse(module.has_any_empty_enums())

    def test_has_no_empty_enums_returns_false_when_empty_enums(self):
        module = self.parse("""
            enum {};
        """)
        self.assertFalse(module.has_no_empty_enums())

    def test_has_no_empty_enums_returns_true_when_no_empty_enums(self):
        module = self.parse("""
            enum {a};
        """)
        self.assertTrue(module.has_no_empty_enums())

    def test_dump_calls_dump_to_with_stdout(self):
        module = self.parse('')
        module.dump_to = mock.Mock()
        module.dump()
        module.dump_to.assert_called_once_with(sys.stdout, False)

    def test_dump_calls_dump_to_with_stdout_and_verbose(self):
        module = self.parse('')
        module.dump_to = mock.Mock()
        module.dump(True)
        module.dump_to.assert_called_once_with(sys.stdout, True)

    def test_dump_to(self):
        stream = io.StringIO()
        module = self.parse("""
            #include <stdio.h>
            #include <stdlib.h>

            int x = 25;
            double d;

            struct s {
                int a;
                char c;
            } s1 = {14, 1};

            union u {
                float f;
                double d;
            } u1;

            enum e {
                LEFT,
                RIGHT
            };

            float func(int a) {
                return 42.0;
            }

            int main() {
                printf("str1");
                return 0;
            }
        """)
        module.dump_to(stream)
        self.assertEqual(
            stream.getvalue(),
            dedent("""\
                dummy.c

                Includes:
                ---------
                #include <stdio.h>
                #include <stdlib.h>

                Global vars:
                ------------
                int x = 25
                double d
                struct s s1 = {14, 1}
                union u u1

                Structs:
                --------
                struct s {
                    int a;
                    char c;
                }

                Unions:
                -------
                union u {
                    float f;
                    double d;
                }

                Enums:
                ------
                enum e {
                    LEFT,
                    RIGHT
                }

                Functions:
                ----------
                float func(int a)
                int main()

                String literals:
                ----------------
                str1
                """)
        )

    def test_dump_to_verbose(self):
        stream = io.StringIO()
        module = self.parse("""
            #include <stdio.h>

            struct s {
                int a;
                char c;
            } s1 = {14, 1};

            union u {
                double d;
            };

            enum { LEFT, RIGHT };

            int main() {
                printf("str1");
                int i;
                i = 8;
                double pi = 3.14;

                for(int i = 0; i < 10; i++) {
                    for(int j = 0; j < 10; j++) {
                        ;
                    }

                    if(1) {
                        i = 5;

                        while(35) {
                            ;
                        }
                    }
                }

                while(6) {
                    if(1 > 2) {
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

                return 42;
            }
        """)
        module.dump_to(stream, True)
        self.assertEqual(
            stream.getvalue(),
            dedent("""\
                dummy.c

                Includes:
                ---------
                #include <stdio.h>

                Global vars:
                ------------
                struct s s1 = {14, 1}

                Structs:
                --------
                struct s {
                    int a;
                    char c;
                }

                Unions:
                -------
                union u {
                    double d;
                }

                Enums:
                ------
                enum {
                    LEFT,
                    RIGHT
                }

                Functions:
                ----------
                int main()

                String literals:
                ----------------
                str1

                Dump of main:
                =============
                int main()

                Called functions:
                -----------------
                printf

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
                return 42

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
        module = self.parse("""
            enum {};
        """)
        self.assertEqual(repr(module), "<Module file_name='dummy.c'>")
