"""
    Tests for the :module`regression_tests.parsers.yara_parser` module.
"""

import unittest

from regression_tests.parsers.yara_parser import Yara
from regression_tests.parsers.yara_parser import parse


class ParseTests(unittest.TestCase):
    """Tests for `parse()`."""

    def test_returns_yara_from_string(self):
        yara = parse('rule X { meta: name = "func" }')
        self.assertIsInstance(yara, Yara)

    def test_returned_object_is_like_string(self):
        yara = parse('rule X { meta: name = "func" }')
        self.assertIsInstance(yara, str)


class YaraTests(unittest.TestCase):
    """Tests for `Yara`."""

    def test_contains_returns_true_if_regexp_is_found(self):
        yara = Yara('rule X { meta: name = "func" }')
        self.assertTrue(yara.contains(r'func'))

    def test_contains_returns_false_if_regexp_is_not_found(self):
        yara = Yara('rule X { meta: name = "func" }')
        self.assertFalse(yara.contains(r'xxx'))

    def test_rules_returns_parsed_rules(self):
        yara = Yara("""
            rule A {
                meta:
                    name = "func"
                strings:
                    $1 = { B0 8D E2 00 D0 8B E2 00 08 BD E8 0E F0 A0 E1 }
                condition:
                    $1
            }
        """)
        self.assertEqual(len(yara.rules), 1)
        self.assertEqual(yara.rules['A']['rule_name'], 'A')
        self.assertEqual(yara.rules['A']['meta']['name'], '"func"')
        self.assertEqual(yara.rules['A']['conditions'], ['$1'])
        self.assertEqual(
            yara.rules['A']['strings']['$1'],
            '{ B0 8D E2 00 D0 8B E2 00 08 BD E8 0E F0 A0 E1 }'
        )

    def test_exception_is_raised_when_yara_cannot_be_parsed(self):
        with self.assertRaisesRegex(ValueError, r'Failed to parse'):
            Yara('#')
