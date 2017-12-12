"""
    Tests for the :mod:`regression_tests.parsers.c_parser` package.
"""

import re
import unittest

from regression_tests.parsers.c_parser import parse


class WithModuleTests(unittest.TestCase):
    """Base class for all tests with parsed C code."""

    def parse(self, code, file_name='dummy.c'):
        # If there are any errors, print them so when a test fails, we know
        # whether it is due to a parse error or our error.
        return parse(code, file_name, print_errors=True)

    def get_func(self, code, func_name):
        module = self.parse(code)
        return module.funcs[func_name]

    def get_named_struct(self, code, struct_name):
        module = self.parse(code)
        return module.named_structs[struct_name]

    def get_named_union(self, code, union_name):
        module = self.parse(code)
        return module.named_unions[union_name]

    def get_named_enum(self, code, enum_name):
        module = self.parse(code)
        return module.named_enums[enum_name]

    def get_expr(self, expr, type):
        module = self.parse("""
            func() {
              %s a = %s;
            }
        """ % (type, expr))
        return module.func('func').var_def_stmts[0].var.initializer

    def get_expr_from_global_var(self, expr, type):
        # Include stdint.h to recognize the intX_t typedefs.
        # Include stdbool.h to recognize bool.
        module = self.parse("""
            #include <stdbool.h>
            #include <stdint.h>
            #include <wchar.h>

            {} a = {};
        """.format(type, expr))
        return module.global_vars['a'].initializer

    def get_literal(self, literal, type):
        return self.get_expr_from_global_var(literal, type)

    def get_array_initializer(self, initializer, type):
        code = '{} a[] = {};'.format(type, initializer)
        module = self.parse(code)
        return module.global_vars['a'].initializer

    def get_var(self, type, name, initializer=None):
        code = ''
        # Include stdint.h to recognize the intX_t typedefs.
        code += '#include <stdint.h>\n'
        # Include stdbool.h to recognize bool.
        code += '#include <stdbool.h>\n'
        # The array type has to be handled specifically because in C,
        # we have to write
        #
        #     int a[10];
        #
        # and not
        #
        #     int[10] a;
        #
        m = re.match(r'([^\[]*?)\s*(\[.*)', type)
        if m is not None:
            # It is an array, so place the name of the variable before '['.
            code += '{} {}{};'.format(m.group(1), name, m.group(2))
        else:
            # Is not an array, so we can use the standard variable declaration
            # of the form `type name;`.
            code += '{} {}'.format(type, name)
            if initializer:
                code += ' = {}'.format(initializer)
            code += ';'

        module = self.parse(code)
        return module.global_vars[name]

    def get_type(self, type):
        return self.get_var(type, 'a').type

    def get_array_index_op_expr(self, array_name, index, type):
        module = self.parse("""
            func() {
              %s %s[%s];
              %s x = %s[%d];
            }
        """ % (type, array_name, index + 1, type, array_name, index))
        return module.func('func').var_def_stmts[1].var.initializer

    def get_comma_op_expr(self, lhs, rhs):
        module = self.parse("""
            func() {
              while (%s, %s) {}
            }
        """ % (lhs, rhs))
        return module.func('func').while_loops[0].condition

    def get_struct_ref_op_expr(self, lhs, rhs):
        module = self.parse("""
            func() {
                struct { int %s; } %s;

                if(%s.%s) {}
            }
        """ % (rhs, lhs, lhs, rhs))
        return module.func('func').if_stmts[0].condition

    def get_struct_deref_op_expr(self, lhs, rhs):
        module = self.parse("""
            func() {
                struct { int %s; } *%s;

                if(%s->%s) {}
            }
        """ % (rhs, lhs, lhs, rhs))
        return module.func('func').if_stmts[0].condition
