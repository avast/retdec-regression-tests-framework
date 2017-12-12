"""
    Tests for the :module`regression_tests.parsers.c_parser.composite_type` module.
"""

from regression_tests.utils.list import NamedObjectList
from tests.parsers.c_parser import WithModuleTests


class CompositeTypeTests(WithModuleTests):
    """Tests for `CompositeType`."""

    def test_members_returns_named_object_list(self):
        type = self.get_type('struct {}')
        self.assertIsInstance(type.members, NamedObjectList)

    def test_members_returns_empty_list_when_no_members(self):
        type = self.get_type('union {}')
        self.assertEqual(type.members, [])

    def test_members_returns_correct_list_when_two_members(self):
        type = self.get_type('union { int a; int b; }')
        self.assertEqual(type.members, [
            self.get_var('int', 'a'),
            self.get_var('int', 'b')
        ])

    def test_member_names_returns_empty_list_when_no_members(self):
        type = self.get_type('struct {}')
        self.assertEqual(type.member_names, [])

    def test_member_names_returns_correct_list_when_two_members(self):
        type = self.get_type('struct { int a; int b; }')
        self.assertEqual(type.member_names, ['a', 'b'])

    def test_member_count_returns_zero_for_empty_struct(self):
        type = self.get_type('union {}')
        self.assertEqual(type.member_count, 0)

    def test_member_count_returns_correct_value_for_nonempty_struct(self):
        type = self.get_type('struct { int a; int b; }')
        self.assertEqual(type.member_count, 2)

    def test_has_any_members_returns_false_when_no_members(self):
        type = self.get_type('struct {}')
        self.assertFalse(type.has_any_members())

    def test_has_any_members_returns_true_when_has_members(self):
        type = self.get_type('union { int a; }')
        self.assertTrue(type.has_any_members())

    def test_name_returns_correct_name_when_has_name(self):
        type = self.get_type('struct X {}')
        self.assertEqual(type.name, 'X')

    def test_name_returns_none_when_no_name(self):
        type = self.get_type('union {}')
        self.assertIsNone(type.name)

    def test_has_name_returns_true_when_struct_has_name(self):
        type = self.get_type('union X {}')
        self.assertTrue(type.has_name())

    def test_has_name_returns_false_when_struct_has_no_name(self):
        type = self.get_type('struct {}')
        self.assertFalse(type.has_name())

    def test_whole_name_returns_correct_whole_when_has_name(self):
        type = self.get_type('struct X {}')
        self.assertEqual(type.whole_name, 'struct X')

    def test_whole_name_returns_correct_whole_name_when_no_name(self):
        type = self.get_type('union {}')
        self.assertEqual(type.whole_name, 'union')

    def test_two_identical_types_are_equal(self):
        type = self.get_type('struct { int a; }')
        self.assertEqual(type, type)

    def test_two_same_types_are_equal(self):
        type1 = self.get_type('struct { int a; }')
        type2 = self.get_type('struct { int a; }')
        self.assertEqual(type1, type2)

    def test_two_different_types_are_not_equal(self):
        type1 = self.get_type('void')
        type2 = self.get_type('union { int a; }')
        self.assertNotEqual(type1, type2)

    def test_repr_returns_correct_repr_for_struct_without_name(self):
        type = self.get_type('struct { int a; }')
        self.assertEqual(repr(type), '<StructType name=None>')

    def test_repr_returns_correct_repr_for_struct_with_name(self):
        type = self.get_type('union u { int a; }')
        self.assertEqual(repr(type), '<UnionType name=u>')

    def test_str_returns_correct_str_for_struct_without_name(self):
        type = self.get_type('union { int a; }')
        self.assertEqual(str(type), 'union {\n    int a;\n}')

    def test_str_returns_correct_str_for_struct_with_name(self):
        type = self.get_type('struct s { int a; }')
        self.assertEqual(str(type), 'struct s {\n    int a;\n}')
