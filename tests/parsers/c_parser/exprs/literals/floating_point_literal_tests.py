"""
    Tests for the
    :module`regression_tests.parsers.c_parser.exprs.literals.floating_point_literal`
    module.
"""

from tests.parsers.c_parser import WithModuleTests


class FloatingPointLiteralTests(WithModuleTests):
    """Tests for `FloatingPointLiteral`."""

    def test_type_returns_correct_type(self):
        literal = self.get_literal('1.0f', 'float')
        self.assertTrue(literal.type.is_float())

    def test_value_returns_correct_value(self):
        literal = self.get_literal('1.0f', 'float')
        self.assertEqual(literal.value, 1.0)

    def test_two_identical_literals_are_equal(self):
        literal = self.get_literal('1.0f', 'float')
        self.assertEqual(literal, literal)

    def test_two_same_literals_are_equal(self):
        literal1 = self.get_literal('1.0f', 'float')
        literal2 = self.get_literal('1.0f', 'float')
        self.assertEqual(literal1, literal2)

    def test_literal_is_equal_to_its_value(self):
        literal = self.get_literal('1.0f', 'float')
        self.assertEqual(literal, 1.0)

    def test_literal_is_not_equal_to_different_value(self):
        literal = self.get_literal('1.0f', 'float')
        self.assertNotEqual(literal, 2.0)

    def test_two_literals_with_different_value_are_different(self):
        literal1 = self.get_literal('1.0f', 'float')
        literal2 = self.get_literal('2.0f', 'float')
        self.assertNotEqual(literal1, literal2)

    def test_str_returns_correct_str(self):
        literal = self.get_literal('1.0f', 'float')
        self.assertEqual(str(literal), '1.0')

    def test_repr_returns_correct_repr(self):
        literal = self.get_literal('1.0f', 'float')
        self.assertEqual(repr(literal), '<FloatingPointLiteral value="1.0">')
