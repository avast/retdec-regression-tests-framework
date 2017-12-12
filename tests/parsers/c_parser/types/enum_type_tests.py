"""
    Tests for the :module`regression_tests.parsers.c_parser.enum` module.
"""

from regression_tests.parsers.c_parser.types.enum_type import EnumType
from tests.parsers.c_parser import WithModuleTests


class EnumTypeTests(WithModuleTests):
    """Tests for `Enum`."""

    def get_enum(self, code):
        module = self.parse(code)
        enumNode = next(module._tu.cursor.get_children())
        return EnumType(None, enumNode)

    def test_enum_type_is_enum(self):
        type = self.get_enum('enum { a };')
        self.assertTrue(type.is_enum())

    def test_enum_type_is_no_other_type(self):
        type = self.get_enum('enum { a };')
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
        self.assertFalse(type.is_function())
        self.assertFalse(type.is_bool())

    def test_name_of_enum_without_name_is_none(self):
        enum = self.get_enum('enum {cat, dog};')
        self.assertIsNone(enum.name)

    def test_name_of_enum_is_correct(self):
        enum = self.get_enum('enum e {cat, dog};')
        self.assertEqual(enum.name, 'e')

    def test_has_name_returns_false_when_enum_without_name(self):
        enum = self.get_enum('enum {cat, dog};')
        self.assertFalse(enum.has_name())

    def test_has_name_returns_true_when_enum_with_name(self):
        enum = self.get_enum('enum e {cat, dog};')
        self.assertTrue(enum.has_name())

    def test_empty_enum_is_empty(self):
        enum = self.get_enum('enum {};')
        self.assertTrue(enum.is_empty())

    def test_enum_with_items_is_not_empty(self):
        enum = self.get_enum('enum {horse};')
        self.assertFalse(enum.is_empty())

    def test_enum_with_one_item_has_item_count_one(self):
        enum = self.get_enum('enum {horse};')
        self.assertEqual(enum.item_count, 1)

    def test_item_count_of_empty_enum_is_zero(self):
        enum = self.get_enum('enum {};')
        self.assertEqual(enum.item_count, 0)

    def test_enum_items_have_correct_values(self):
        enum = self.get_enum('enum {horse, cat=25, dog};')
        self.assertEqual(enum.items, {'horse': 0, 'cat': 25, 'dog': 26})

    def test_empty_enum_does_not_have_any_items(self):
        enum = self.get_enum('enum {};')
        self.assertEqual(len(enum.items), 0)

    def test_enum_items_have_correct_names(self):
        enum = self.get_enum('enum {horse, cat=25, dog};')
        self.assertEqual(enum.item_names, ['horse', 'cat', 'dog'])

    def test_empty_enum_does_not_have_any_names_of_items(self):
        enum = self.get_enum('enum {};')
        self.assertEqual(len(enum.item_names), 0)

    def test_enum_is_equal_to_itself(self):
        enum = self.get_enum('enum {};')
        self.assertEqual(enum, enum)

    def test_two_same_enums_are_equal(self):
        enum = self.get_enum('enum { a };')
        enum_twin = self.get_enum('enum { a };')
        self.assertEqual(enum, enum_twin)

    def test_two_different_enums_are_not_equal(self):
        enum = self.get_enum('enum { a };')
        enum_twin = self.get_enum('enum { b };')
        self.assertNotEqual(enum, enum_twin)

    def test_repr_returns_correct_repr_for_enum_without_name(self):
        enum = self.get_enum('enum { a };')
        self.assertEqual(repr(enum), '<EnumType name=None>')

    def test_repr_returns_correct_repr_for_enum_with_name(self):
        enum = self.get_enum('enum e { a };')
        self.assertEqual(repr(enum), '<EnumType name=e>')

    def test_str_returns_correct_str_for_enum_without_name(self):
        enum = self.get_enum('enum { a, b };')
        self.assertEqual(str(enum), 'enum {\n    a,\n    b\n}')

    def test_str_returns_correct_str_for_enum_with_name(self):
        enum = self.get_enum('enum e { a, b };')
        self.assertEqual(str(enum), 'enum e {\n    a,\n    b\n}')
