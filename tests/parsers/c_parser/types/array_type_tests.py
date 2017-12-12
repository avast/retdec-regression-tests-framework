"""
    Tests for the :module`regression_tests.parsers.c_parser.array_type` module.
"""

from tests.parsers.c_parser import WithModuleTests


class ArrayTypeTests(WithModuleTests):
    """Tests for `ArrayType`."""

    def test_array_type_is_array(self):
        type = self.get_type('int [10]')
        self.assertTrue(type.is_array())

    def test_array_type_is_no_other_type(self):
        type = self.get_type('int [10]')
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
        self.assertFalse(type.is_enum())
        self.assertFalse(type.is_function())
        self.assertFalse(type.is_bool())

    def test_element_type_returns_correct_value_for_array_of_int(self):
        type = self.get_type('int [10]')
        self.assertTrue(type.element_type.is_int())

    def test_element_type_returns_correct_value_for_array_of_arrays(self):
        type = self.get_type('int [10][20]')
        self.assertTrue(type.element_type.is_int())

    def test_element_count_returns_correct_value_for_complete_array(self):
        type = self.get_type('int [10]')
        self.assertEqual(type.element_count, 10)

    def test_element_count_returns_one_for_incomplete_array(self):
        type = self.get_type('int []')
        # Clang behaves this way (it returns 1 for incomplete arrays).
        self.assertEqual(type.element_count, 1)

    def test_element_count_for_two_dimensional_array_returns_correct_value(self):
        type = self.get_type('int [5][10]')
        self.assertEqual(type.element_count, (5, 10))

    def test_element_count_for_incomplete_two_dimensional_array_is_correct(self):
        type = self.get_type('int [][10]')
        # Clang behaves this way (it returns 1 for incomplete arrays).
        self.assertEqual(type.element_count, (1, 10))

    def test_dimension_of_one_dimensional_array_is_one(self):
        type = self.get_type('int [5]')
        self.assertEqual(type.dimension, 1)

    def test_dimension_of_three_dimensional_array_is_three(self):
        type = self.get_type('int [5][5][5]')
        self.assertEqual(type.dimension, 3)

    def test_two_identical_types_are_equal(self):
        type = self.get_type('int [10]')
        self.assertEqual(type, type)

    def test_two_same_types_are_equal(self):
        type1 = self.get_type('int [10]')
        type2 = self.get_type('int [10]')
        self.assertEqual(type1, type2)

    def test_two_different_types_are_not_equal(self):
        type1 = self.get_type('int [10]')
        type2 = self.get_type('void')
        self.assertNotEqual(type1, type2)

    def test_two_arrays_of_different_element_type_are_not_equal(self):
        type1 = self.get_type('int [10]')
        type2 = self.get_type('float [10]')
        self.assertNotEqual(type1, type2)

    def test_two_arrays_of_different_element_count_are_not_equal(self):
        type1 = self.get_type('int [5]')
        type2 = self.get_type('int [10]')
        self.assertNotEqual(type1, type2)

    def test_two_equal_arrays_have_same_hash(self):
        type1 = self.get_type('int [10]')
        type2 = self.get_type('int [10]')
        self.assertEqual(type1, type2)
        self.assertEqual(hash(type1), hash(type2))

    def test_repr_returns_correct_repr_for_simple_array(self):
        type = self.get_type('int [5]')
        self.assertEqual(repr(type), '<ArrayType element_type=int element_count=5 dimension=1>')

    def test_repr_returns_correct_repr_for_multidimensional_array(self):
        type = self.get_type('int [5][10]')
        self.assertEqual(repr(type), '<ArrayType element_type=int element_count=(5, 10) dimension=2>')

    def test_str_returns_correct_str(self):
        type = self.get_type('int [5]')
        self.assertEqual(str(type), 'int []')
