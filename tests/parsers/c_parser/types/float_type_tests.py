"""
    Tests for the :module`regression_tests.parsers.c_parser.float_type` module.
"""

from regression_tests.parsers.c_parser.types.float_type import FloatType
from tests.parsers.c_parser import WithModuleTests


class FloatTypeTests(WithModuleTests):
    """Tests for `FloatType`."""

    def test_float_type_is_float(self):
        type = self.get_type('float')
        self.assertTrue(type.is_float())

    def test_float_type_is_floating_point(self):
        type = self.get_type('float')
        self.assertTrue(type.is_floating_point())

    def test_float_type_is_no_other_type(self):
        type = self.get_type('float')
        self.assertFalse(type.is_void())
        self.assertFalse(type.is_char())
        self.assertFalse(type.is_integral())
        self.assertFalse(type.is_int())
        self.assertFalse(type.is_pointer())
        self.assertFalse(type.is_double())
        self.assertFalse(type.is_composite_type())
        self.assertFalse(type.is_struct())
        self.assertFalse(type.is_union())
        self.assertFalse(type.is_array())
        self.assertFalse(type.is_enum())
        self.assertFalse(type.is_function())
        self.assertFalse(type.is_bool())

    def test_is_of_correct_size_when_size_is_known(self):
        # We cannot simply parse "float32_t" because it is our custom typedef.
        # Therefore, we create a FloatType ourselves, but we have to pass None
        # as the internal type.
        type = FloatType(None, 32)
        self.assertTrue(type.is_float(32))

    def test_is_not_of_correct_size_when_size_is_not_known(self):
        type = self.get_type('float')
        self.assertFalse(type.is_float(32))

    def test_two_identical_types_are_equal(self):
        type = self.get_type('float')
        self.assertEqual(type, type)

    def test_two_same_types_are_equal(self):
        type1 = self.get_type('float')
        type2 = self.get_type('float')
        self.assertEqual(type1, type2)

    def test_two_different_types_are_not_equal(self):
        type1 = self.get_type('void')
        type2 = self.get_type('float')
        self.assertNotEqual(type1, type2)

    def test_two_equal_types_have_same_hash(self):
        type1 = self.get_type('float')
        type2 = self.get_type('float')
        self.assertEqual(type1, type2)
        self.assertEqual(hash(type1), hash(type2))

    def test_repr_returns_corroct_value(self):
        type = self.get_type('float')
        self.assertEqual(repr(type), '<FloatType>')

    def test_str_returns_corroct_value(self):
        type = self.get_type('float')
        self.assertEqual(str(type), 'float')
