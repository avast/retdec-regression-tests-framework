"""
    Tests for the
    :module`regression_tests.parsers.c_parser.exprs.literals.string_literal`
    module.
"""

from tests.parsers.c_parser import WithModuleTests


class StringLiteralTests(WithModuleTests):
    """Tests for `StringLiteral`."""

    # TODO At the moment, the following test fails because the type is not
    #      parsed as a pointer.
    # def test_type_returns_correct_type(self):
    #     literal = self.get_literal('"hello"', 'const char *')
    #     self.assertTrue(literal.type.is_pointer())

    def test_value_returns_correct_value_for_8bit_string_literal(self):
        literal = self.get_literal('"hello"', 'const char *')
        self.assertEqual(literal.value, "hello")

    def test_value_returns_correct_value_for_wide_string_literal(self):
        literal = self.get_literal('L"hello"', 'const wchar_t *')
        self.assertEqual(literal.value, "hello")

    def test_two_identical_literals_are_equal(self):
        literal = self.get_literal('"hello"', 'const char *')
        self.assertEqual(literal, literal)

    def test_two_same_literals_are_equal(self):
        literal1 = self.get_literal('"hello"', 'const char *')
        literal2 = self.get_literal('"hello"', 'const char *')
        self.assertEqual(literal1, literal2)

    def test_literal_is_equal_to_its_value(self):
        literal = self.get_literal('"hello"', 'const char *')
        self.assertEqual(literal, 'hello')

    def test_literal_is_not_equal_to_different_value(self):
        literal = self.get_literal('"hello"', 'const char *')
        self.assertNotEqual(literal, 'other string')

    def test_two_literals_with_different_value_are_different(self):
        literal1 = self.get_literal('"first"', 'const char *')
        literal2 = self.get_literal('"second"', 'const char *')
        self.assertNotEqual(literal1, literal2)

    def test_str_returns_correct_str(self):
        literal = self.get_literal('"first"', 'const char *')
        self.assertEqual(str(literal), 'first')

    def test_repr_returns_correct_repr(self):
        literal = self.get_literal('"first"', 'const char *')
        self.assertEqual(repr(literal), '<StringLiteral value="first">')
