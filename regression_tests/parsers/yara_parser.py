"""
    Parsing of YARA files.
"""

import collections

import plyara.interp

from regression_tests.parsers.text_parser import Text


def parse(yara_rules):
    """Parses the given YARA rules (`str`).

    :returns: Parsed representation of the rules (:class:`Yara`).

    :raises ValueError: When the YARA rules cannot be parsed.
    """
    return Yara(yara_rules)


class Yara(Text):
    """Parsed YARA rules.

    Instances of this class behave like strings with additional properties and
    methods.
    """

    def __new__(cls, yara_rules):
        """Constructs new parsed YARA rules.

        :param str yara_rules: Text representation of the YARA rules.
        """
        return Text.__new__(cls, yara_rules)

    def __init__(self, yara_rules):
        """
        :param str yara_rules: Text representation of the YARA rules.

        :raises ValueError: When the rules cannot be parsed.
        """
        self._rules = self._parse(yara_rules)

    @property
    def rules(self):
        """The underlying parsed representation of the rules
        (`collections.OrderedDict`).

        For example, assume that `yara_rules` contains the following rule:

        .. code-block:: text

            rule A {
                meta:
                    name = "func"
                strings:
                    $1 = { B0 8D E2 00 D0 8B E2 00 08 BD E8 0E F0 A0 E1 }
                condition:
                    $1
            }

        This rule can be checked as follows:

        .. code-block:: python

            rule = rules['A']
            self.assertEqual(rule['meta']['name'], '"func"')
            self.assertEqual(rule['strings']['$1'], '{ B0 8D E2 [..] }')
            self.assertEqual(rule['conditions'], ['$1'])
        """
        return self._rules

    def _parse(self, yara_rules):
        """Parses the given YARA rules and returns the parsed representation.
        """
        # Parse the rules using a 3rd party library called 'plyara'
        # (https://github.com/8u1a/plyara).
        try:
            parsed_rules = plyara.interp.parseString(yara_rules)
        except Exception as ex:
            raise ValueError('Failed to parse the given YARA rules') from ex

        # The rules are in a list, but for our tests, it is better if they are
        # in a dictionary that can be accessed via rule names.
        parsed_rules = collections.OrderedDict(
            (r['rule_name'], r) for r in parsed_rules
        )

        # Rename the 'condition_terms' key to 'conditions' in all rules (it is
        # shorter and, more importantly, corresponds to the name used by YARA
        # rules.
        for rule in parsed_rules.values():
            if 'condition_terms' in rule:
                rule['conditions'] = rule.pop('condition_terms')

        # Rename the 'metadata' key to 'meta' in all rules (it is shorter and,
        # more importantly, corresponds to the name used by YARA rules.
        for rule in parsed_rules.values():
            if 'metadata' in rule:
                rule['meta'] = rule.pop('metadata')

        # The strings are in a list, but for our tests, it is better if they
        # are in a dictionary that can be accessed via names.
        for rule in parsed_rules.values():
            if 'strings' in rule:
                rule['strings'] = collections.OrderedDict(
                    (s['name'], s['value']) for s in rule['strings']
                )

        return parsed_rules
