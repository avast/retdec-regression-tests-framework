"""
    Tests for the
    :module`regression_tests.parsers.c_parser.exprs.literals.character_literal`
    module.
"""

from tests.parsers.c_parser import WithModuleTests


class CharacterLiteralTests(WithModuleTests):
    """Tests for `CharacterLiteral`."""

    def test_type_returns_correct_type(self):
        literal = self.get_literal("'a'", 'int')
        self.assertTrue(literal.type.is_int())

    def test_value_returns_correct_value(self):
        literal = self.get_literal("'a'", 'int')
        self.assertEqual(literal.value, 'a')

    def test_two_identical_literals_are_equal(self):
        literal = self.get_literal("'a'", 'int')
        self.assertEqual(literal, literal)

    def test_two_same_literals_are_equal(self):
        literal1 = self.get_literal("'a'", 'int')
        literal2 = self.get_literal("'a'", 'int')
        self.assertEqual(literal1, literal2)

    def test_literal_is_equal_to_its_value(self):
        literal = self.get_literal("'a'", 'int')
        self.assertEqual(literal, 'a')

    def test_literal_is_not_equal_to_different_value(self):
        literal = self.get_literal("'a'", 'int')
        self.assertNotEqual(literal, 'b')

    def test_two_literals_with_different_value_are_different(self):
        literal1 = self.get_literal("'a'", 'int')
        literal2 = self.get_literal("'b'", 'int')
        self.assertNotEqual(literal1, literal2)

    def test_str_returns_correct_str(self):
        literal = self.get_literal("'a'", 'int')
        self.assertEqual(str(literal), 'a')

    def test_repr_returns_correct_repr(self):
        literal = self.get_literal("'a'", 'int')
        self.assertEqual(repr(literal), '<CharacterLiteral value="a">')
