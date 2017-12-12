"""
    Tests for the :module`regression_tests.parsers.c_parser.variable` module.
"""

from regression_tests.parsers.c_parser.exprs.init_list_expr import InitListExpr
from tests.parsers.c_parser import WithModuleTests


class VariableTests(WithModuleTests):
    """Tests for `Variable`."""

    def test_name_returns_correct_name(self):
        NAME = 'a'
        var = self.get_var('int', NAME)
        self.assertEqual(var.name, NAME)

    def test_initializer_returns_correct_initializer(self):
        var = self.get_var('int', 'a', 7)
        self.assertEqual(var.initializer, 7)

    def test_initializer_returns_correct_initializer_for_composite_type_var(self):
        var = self.get_var('struct { int x; }', 's', '{ 42 }')
        self.assertTrue(isinstance(var.initializer, InitListExpr))
        self.assertEqual(len(var.initializer), 1)
        self.assertEqual(var.initializer[0], 42)

    def test_type_returns_correct_type(self):
        var = self.get_var('int', 'a')
        self.assertTrue(var.type.is_int())

    def test_type_returns_correct_type_for_composite_type_var(self):
        var = self.get_var('struct { int x; }', 's')
        self.assertTrue(var.type.is_struct())

    def test_returned_types_are_equal_to_each_other(self):
        var = self.get_var('int', 'a')
        self.assertEqual(var.type, var.type)

    def test_initializer_returns_none_when_no_initializer(self):
        var = self.get_var('int', 'a')
        self.assertIsNone(var.initializer)

    def test_initializer_returns_none_for_composite_type_var_without_initializer(self):
        var = self.get_var('struct { int x; }', 's')
        self.assertIsNone(var.initializer)

    def test_str_with_type_returns_correct_str(self):
        var = self.get_var('int', 'a')
        self.assertEqual(var.str_with_type(), 'int a')

    def test_str_with_type_returns_correct_str_for_composite_type_var(self):
        var = self.get_var('struct { int x; }', 's')
        self.assertEqual(var.str_with_type(), 'struct s')

    def test_str_with_type_returns_correct_str_for_var_with_initializer(self):
        var = self.get_var('int', 'a', 5)
        self.assertEqual(var.str_with_type(), 'int a = 5')

    def test_str_with_type_returns_correct_str_for_composite_type_var_with_initializer(self):
        var = self.get_var('struct { int x; }', 's', '{ 42 }')
        self.assertEqual(var.str_with_type(), 'struct s = {42}')

    def test_variable_can_be_compared_to_strings(self):
        var = self.get_var('int', 'a', 5)
        self.assertEqual(var, ' \ta\n')

    def test_two_variables_with_same_type_and_name_are_equal(self):
        var1 = self.get_var('int', 'a')
        var2 = self.get_var('int', 'a')
        self.assertEqual(var1, var2)

    def test_two_variables_with_different_type_are_not_equal(self):
        var1 = self.get_var('int', 'a')
        var2 = self.get_var('int *', 'a')
        self.assertNotEqual(var1, var2)

    def test_two_variables_with_different_name_are_not_equal(self):
        var1 = self.get_var('int', 'a')
        var2 = self.get_var('int', 'b')
        self.assertNotEqual(var1, var2)

    def test_repr_returns_correct_repr(self):
        var = self.get_var('int', 'a')
        self.assertEqual(repr(var), '<Variable type=int name=a initializer=None>')

    def test_str_returns_correct_str(self):
        var = self.get_var('int', 'a')
        self.assertEqual(str(var), 'a')

    def test_str_returns_correct_str_for_var_with_initializer(self):
        var = self.get_var('int', 'a', 5)
        self.assertEqual(str(var), 'a = 5')
