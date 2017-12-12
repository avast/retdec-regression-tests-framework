"""
    Tests for the :module`regression_tests.parsers.c_parser.bool_type` module.
"""

from tests.parsers.c_parser import WithModuleTests


class BoolTypeTests(WithModuleTests):
    """Tests for `BoolType`."""

    def test_bool_type_is_bool(self):
        type = self.get_type('bool')
        self.assertTrue(type.is_bool())

    def test_bool_type_is_integral(self):
        type = self.get_type('bool')
        self.assertTrue(type.is_integral())

    def test_bool_type_is_no_other_type(self):
        type = self.get_type('bool')
        self.assertFalse(type.is_void())
        self.assertFalse(type.is_int())
        self.assertFalse(type.is_char())
        self.assertFalse(type.is_pointer())
        self.assertFalse(type.is_floating_point())
        self.assertFalse(type.is_float())
        self.assertFalse(type.is_double())
        self.assertFalse(type.is_composite_type())
        self.assertFalse(type.is_struct())
        self.assertFalse(type.is_union())
        self.assertFalse(type.is_array())
        self.assertFalse(type.is_enum())
        self.assertFalse(type.is_function())

    def test_two_identical_types_are_equal(self):
        type = self.get_type('bool')
        self.assertEqual(type, type)

    def test_two_same_types_are_equal(self):
        type1 = self.get_type('bool')
        type2 = self.get_type('bool')
        self.assertEqual(type1, type2)

    def test_two_different_types_are_not_equal(self):
        type1 = self.get_type('int')
        type2 = self.get_type('bool')
        self.assertNotEqual(type1, type2)

    def test_two_equal_types_have_same_hash(self):
        type1 = self.get_type('bool')
        type2 = self.get_type('bool')
        self.assertEqual(type1, type2)
        self.assertEqual(hash(type1), hash(type2))

    def test_repr_returns_corroct_value(self):
        type = self.get_type('bool')
        self.assertEqual(repr(type), '<BoolType>')

    def test_str_returns_corroct_value(self):
        type = self.get_type('bool')
        self.assertEqual(str(type), 'bool')
