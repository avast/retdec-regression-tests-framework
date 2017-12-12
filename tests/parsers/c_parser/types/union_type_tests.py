"""
    Tests for the :module`regression_tests.parsers.c_parser.union_type` module.
"""

from tests.parsers.c_parser import WithModuleTests


class UnionTypeTests(WithModuleTests):
    """Tests for `UnionType`."""

    def test_union_type_is_union(self):
        type = self.get_type('union { int a; }')
        self.assertTrue(type.is_union())

    def test_union_type_is_composite_type(self):
        type = self.get_type('union { int a; }')
        self.assertTrue(type.is_composite_type())

    def test_union_type_is_no_other_type(self):
        type = self.get_type('union { int a; }')
        self.assertFalse(type.is_void())
        self.assertFalse(type.is_char())
        self.assertFalse(type.is_integral())
        self.assertFalse(type.is_int())
        self.assertFalse(type.is_floating_point())
        self.assertFalse(type.is_float())
        self.assertFalse(type.is_double())
        self.assertFalse(type.is_pointer())
        self.assertFalse(type.is_struct())
        self.assertFalse(type.is_array())
        self.assertFalse(type.is_enum())
        self.assertFalse(type.is_function())
        self.assertFalse(type.is_bool())
