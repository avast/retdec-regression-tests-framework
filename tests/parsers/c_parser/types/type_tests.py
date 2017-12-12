"""
    Tests for the :module`regression_tests.parsers.c_parser.type` module.
"""

from unittest import mock

from regression_tests.parsers.c_parser.types.array_type import ArrayType
from regression_tests.parsers.c_parser.types.bool_type import BoolType
from regression_tests.parsers.c_parser.types.char_type import CharType
from regression_tests.parsers.c_parser.types.double_type import DoubleType
from regression_tests.parsers.c_parser.types.float_type import FloatType
from regression_tests.parsers.c_parser.types.int_type import IntType
from regression_tests.parsers.c_parser.types.pointer_type import PointerType
from regression_tests.parsers.c_parser.types.struct_type import StructType
from regression_tests.parsers.c_parser.types.type import Type
from regression_tests.parsers.c_parser.types.union_type import UnionType
from regression_tests.parsers.c_parser.types.void_type import VoidType
from tests.parsers.c_parser import WithModuleTests


class TypeTests(WithModuleTests):
    """Tests for `Type`."""

    def test_from_clang_type_returns_void_type_for_void_type(self):
        type = self.get_type('void')
        self.assertIsInstance(type, VoidType)

    def test_from_clang_type_returns_char_type_for_char_type(self):
        type = self.get_type('char')
        self.assertIsInstance(type, CharType)

    def test_from_clang_type_returns_int_type_for_int_type(self):
        type = self.get_type('int')
        self.assertIsInstance(type, IntType)

    def test_from_clang_type_returns_int_type_for_unsigned_int_type(self):
        # Currently, we do not distinguish between signed and unsigned
        # integers.
        type = self.get_type('unsigned int')
        self.assertIsInstance(type, IntType)

    def scenario_is_int_type_of_size(self, type, ref_size):
        type = self.get_type(type)
        self.assertIsInstance(type, IntType)
        self.assertEqual(type.size, ref_size)

    def test_from_clang_type_returns_integral_type_with_size_for_typedefed_int_types(self):
        # Signed.
        self.scenario_is_int_type_of_size('int8_t', 8)
        self.scenario_is_int_type_of_size('int16_t', 16)
        self.scenario_is_int_type_of_size('int32_t', 32)
        self.scenario_is_int_type_of_size('int64_t', 64)
        # Unsigned.
        self.scenario_is_int_type_of_size('uint8_t', 8)
        self.scenario_is_int_type_of_size('uint16_t', 16)
        self.scenario_is_int_type_of_size('uint32_t', 32)
        self.scenario_is_int_type_of_size('uint64_t', 64)

    def test_from_clang_type_returns_float_type_for_float_type(self):
        type = self.get_type('float')
        self.assertIsInstance(type, FloatType)

    def test_from_clang_type_returns_double_type_for_double_type(self):
        type = self.get_type('double')
        self.assertIsInstance(type, DoubleType)

    def test_from_clang_type_returns_float_type_with_size_for_typedefed_float_type(self):
        module = self.parse("""
            typedef float float32_t;

            float32_t g;
        """)
        g_type = module.global_vars['g'].type
        self.assertTrue(g_type.is_float())
        self.assertEqual(g_type.size, 32)

    def test_from_clang_type_returns_double_type_with_size_for_typedefed_double_type(self):
        module = self.parse("""
            typedef double float64_t;

            float64_t g;
        """)
        g_type = module.global_vars['g'].type
        self.assertTrue(g_type.is_double())
        self.assertEqual(g_type.size, 64)

    def test_from_clang_type_returns_pointer_type_for_pointer_to_char_type(self):
        type = self.get_type('char *')
        self.assertIsInstance(type, PointerType)

    def test_from_clang_type_returns_struct_type_for_anonymous_structure(self):
        type = self.get_type('struct { int a; }')
        self.assertIsInstance(type, StructType)

    def test_from_clang_type_returns_union_type_for_anonymous_union(self):
        type = self.get_type('union { int a; }')
        self.assertIsInstance(type, UnionType)

    def test_from_clang_type_returns_array_type_for_complete_array(self):
        type = self.get_type('int [10]')
        self.assertIsInstance(type, ArrayType)

    def test_from_clang_type_returns_array_type_for_incomplete_array(self):
        type = self.get_type('int []')
        self.assertIsInstance(type, ArrayType)

    def test_from_clang_type_returns_bool_type_for_bool(self):
        type = self.get_type('bool')
        self.assertIsInstance(type, BoolType)

    def test_from_clang_type_raises_assertion_error_upon_unsupported_type(self):
        unsupported_type = mock.Mock()
        with self.assertRaisesRegex(AssertionError, r'.*unsupported.*'):
            Type._from_clang_type(unsupported_type)

    def test_is_same_as_returns_true_for_void_type_and_void(self):
        type = self.get_type('void')
        self.assertTrue(type.is_same_as('void'))

    def test_is_same_as_returns_true_for_int_type_and_int(self):
        type = self.get_type('int')
        self.assertTrue(type.is_same_as('int'))
