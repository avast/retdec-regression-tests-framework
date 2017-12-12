"""
    A string literal.
"""

import re

from regression_tests.parsers.c_parser.exprs.literals.literal import Literal
from regression_tests.parsers.c_parser.utils import first_token


class StringLiteral(Literal):
    """A string literal."""

    @property
    def value(self):
        """Value of the literal (`str`)."""
        # Remove a wide-string-literal prefix (L, if any) and strip the leading
        # and ending quotes (").
        return re.sub(r'L?"(.*)"', r'\1', first_token(self._node).spelling)
