"""
    A floating-point literal.

    It represents literals of all floating-point types.
"""

import re

from regression_tests.parsers.c_parser.exprs.literals.literal import Literal
from regression_tests.parsers.c_parser.utils import first_token


class FloatingPointLiteral(Literal):
    """A floating-point literal.

    It represents literals of all floating-point types.
    """

    @property
    def value(self):
        """Value of the literal (`float`)."""
        float_str = first_token(self._node).spelling

        # Remove any C-specific suffix (f, F, l, L) so we can use Python's
        # float constructor to parse the string.
        float_str = re.sub(r'^(.*)[fFlL]$', r'\1', float_str)

        return float(float_str)
