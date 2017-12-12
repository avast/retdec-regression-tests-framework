"""
    An integral literal.

    It represents literals of all integral types.
"""

import re

from regression_tests.parsers.c_parser.exprs.literals.literal import Literal
from regression_tests.parsers.c_parser.utils import first_token


class IntegralLiteral(Literal):
    """An integral literal.

    It represents literals of all integral types.
    """

    @property
    def value(self):
        """Value of the literal (`int`)."""
        if not any(self._node.get_tokens()):
            return None

        int_str = first_token(self._node).spelling

        # Remove any C-specific suffix (u, U, l, L, ll, LL) so we can use
        # Python's int constructor to parse the string.
        int_str = re.sub(r'^(.*?)(ll|LL|[uUlL])$', r'\1', int_str)

        if int_str.lower().startswith('0x'):
            return int(int_str, 16)
        return int(int_str)
