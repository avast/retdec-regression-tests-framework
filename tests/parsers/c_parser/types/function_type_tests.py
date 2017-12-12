"""
    Tests for the :module`regression_tests.parsers.c_parser.function_type` module.
"""

from tests.parsers.c_parser import WithModuleTests


class PointerTypeTests(WithModuleTests):
    """Tests for `FunctionType`."""

    def get_function_type(self, code):
        module = self.parse(code)
        return module.global_vars[0].type.pointed_type

    def test_function_type_is_a_function(self):
        type = self.get_function_type('char (*fp)(int, float);')
        self.assertTrue(type.is_function())

    def test_function_type_is_no_other_type(self):
        type = self.get_function_type('char (*fp)(int, float);')
        self.assertFalse(type.is_void())
        self.assertFalse(type.is_char())
        self.assertFalse(type.is_integral())
        self.assertFalse(type.is_int())
        self.assertFalse(type.is_floating_point())
        self.assertFalse(type.is_float())
        self.assertFalse(type.is_double())
        self.assertFalse(type.is_pointer())
        self.assertFalse(type.is_composite_type())
        self.assertFalse(type.is_struct())
        self.assertFalse(type.is_union())
        self.assertFalse(type.is_array())
        self.assertFalse(type.is_enum())
        self.assertFalse(type.is_bool())

    def test_return_type_returns_correct_type(self):
        type = self.get_function_type('char (*fp)(int, float);')
        self.assertTrue(type.return_type.is_char())

    def test_param_types_returns_correct_types(self):
        type = self.get_function_type('char (*fp)(char (*fp2)(int), float);')
        self.assertTrue(type.param_types[0].is_pointer())
        self.assertTrue(type.param_types[0].pointed_type.is_function())
        self.assertTrue(type.param_types[0].pointed_type.return_type.is_char())
        self.assertTrue(type.param_types[0].pointed_type.param_types[0].is_int())
        self.assertTrue(type.param_types[1].is_float())

    def test_param_count_returns_correct_value(self):
        type = self.get_function_type('void (*fp)(int, double, int);')
        self.assertEqual(type.param_count, 3)

    def test_is_variadic_returns_true_when_function_is_variadic(self):
        type = self.get_function_type('int (*fp)(int, ...);')
        self.assertTrue(type.is_variadic())

    def test_is_variadic_returns_false_when_function_is_not_variadic(self):
        type = self.get_function_type('int (*fp)(int);')
        self.assertFalse(type.is_variadic())

    def test_two_identical_types_are_equal(self):
        type = self.get_function_type('void (*fp)(int, double, int);')
        self.assertEqual(type, type)

    def test_two_same_types_are_equal(self):
        type1 = self.get_function_type('void (*fp)(int, double, int);')
        type2 = self.get_function_type('void (*xy)(int, double, int);')
        self.assertEqual(type1, type2)

    def test_two_different_types_are_not_equal(self):
        type1 = self.get_function_type('void (*fp)(int, double, int);')
        type2 = self.get_function_type('char (*fp)(char (*fp2)(int), float);')
        self.assertNotEqual(type1, type2)

    def test_two_equal_types_have_same_hash(self):
        type1 = self.get_function_type('void (*fp)(int, double, int);')
        type2 = self.get_function_type('void (*xy)(int, double, int);')
        self.assertEqual(type1, type2)
        self.assertEqual(hash(type1), hash(type2))

    def test_repr_returns_corroct_value(self):
        type = self.get_function_type('void (*fp)(int, double, int);')
        self.assertEqual(repr(type), '<FunctionType return_type=void param_types=(int, double, int)>')
