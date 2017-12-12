"""
    A literal (a constant).
"""

from abc import abstractmethod

from regression_tests.parsers.c_parser.exprs.expression import Expression


class Literal(Expression):
    """A literal (a constant)."""

    @property
    @abstractmethod
    def value(self):
        """Value of the literal (builtin Python object, like ``10`` or
        ``"hello"``).
        """
        raise NotImplementedError

    def __eq__(self, other):
        # Allow comparing a literal directly to its value.
        if isinstance(other, Literal):
            return self.value == other.value
        # Allow comparing a literal to a string.
        elif isinstance(other, str):
            return str(self.value) == other
        return self.value == other

    def __hash__(self):
        return hash(self.value)

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return '<{} value="{}">'.format(self.__class__.__name__, self.value)
