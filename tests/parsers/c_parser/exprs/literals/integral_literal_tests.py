"""
    Tests for the
    :module`regression_tests.parsers.c_parser.exprs.literals.integral_literal`
    module.
"""

from tests.parsers.c_parser import WithModuleTests


class IntegralLiteralTests(WithModuleTests):
    """Tests for `IntegralLiteral`."""

    def test_type_returns_correct_type(self):
        literal = self.get_literal('1', 'int')
        self.assertTrue(literal.type.is_int())

    def test_value_returns_correct_value(self):
        literal = self.get_literal('1', 'int')
        self.assertEqual(literal.value, 1)

    def test_value_returns_correct_value_when_l_suffix_used(self):
        literal = self.get_literal('5l', 'int')
        self.assertEqual(literal.value, 5)

    def test_value_returns_correct_value_when_LL_suffix_used(self):
        literal = self.get_literal('3LL', 'int')
        self.assertEqual(literal.value, 3)

    def test_value_returns_correct_value_when_u_suffix_used(self):
        literal = self.get_literal('8u', 'int')
        self.assertEqual(literal.value, 8)

    def test_value_returns_correct_value_when_hex_used(self):
        literal = self.get_literal('0x9', 'int')
        self.assertEqual(literal.value, 0x9)

    def test_value_returns_correct_value_when_oct_and_ll_suffix_used(self):
        literal = self.get_literal('06ll', 'int')
        self.assertEqual(literal.value, 0o6)

    def test_value_returns_none_if_node_has_no_tokens(self):
        literal = self.get_literal('true', 'bool')
        self.assertIsNone(literal.value)

    def test_two_identical_literals_are_equal(self):
        literal = self.get_literal('1', 'int')
        self.assertEqual(literal, literal)

    def test_two_same_literals_are_equal(self):
        literal1 = self.get_literal('1', 'int')
        literal2 = self.get_literal('1', 'int')
        self.assertEqual(literal1, literal2)

    def test_literal_is_equal_to_its_value(self):
        literal = self.get_literal('1', 'int')
        self.assertEqual(literal, 1)

    def test_literal_is_not_equal_to_different_value(self):
        literal = self.get_literal('1', 'int')
        self.assertNotEqual(literal, 2)

    def test_two_literals_with_different_value_are_different(self):
        literal1 = self.get_literal('1', 'int')
        literal2 = self.get_literal('2', 'int')
        self.assertNotEqual(literal1, literal2)

    def test_str_returns_correct_str(self):
        literal = self.get_literal('1', 'int')
        self.assertEqual(str(literal), '1')

    def test_repr_returns_correct_repr(self):
        literal = self.get_literal('1', 'int')
        self.assertEqual(repr(literal), '<IntegralLiteral value="1">')
