"""
    A character literal.
"""

from regression_tests.parsers.c_parser.exprs.literals.literal import Literal
from regression_tests.parsers.c_parser.utils import first_token


class CharacterLiteral(Literal):
    """A character literal."""

    @property
    def value(self):
        """Value of the literal (`str`)."""
        # Strip the leading and ending quotes (').
        return first_token(self._node).spelling[1:-1]
