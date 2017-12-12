"""
    A call expression.
"""

from regression_tests.parsers.c_parser.exprs.expression import Expression
from regression_tests.parsers.c_parser.utils import remove_whitespace
from regression_tests.parsers.c_parser.utils import string_from_tokens


class CallExpr(Expression):
    """A call expression."""

    def is_call(self):
        """Returns ``True``."""
        return True

    @property
    def name(self):
        """Name of the called function."""
        return self._node.spelling

    def has_args(self):
        """Does the call expression have arguments?"""
        return bool(self.args)

    @property
    def args(self):
        """Arguments of the call expression (tuple of :class:`.Expression`)."""
        children = self._node.get_children()
        next(children)  # Advance to the second child.
        return tuple(map(Expression._from_clang_node, children))

    def __eq__(self, other):
        if isinstance(other, str):
            return string_from_tokens(self._node) == remove_whitespace(other)
        else:
            return (
                type(self) is type(other) and
                self.name == other.name and
                self.args == other.args
            )

    def __hash__(self):
        return hash(self.name) + hash(self.args)

    def __repr__(self):
        return '<{} name={} args=({})>'.format(
            self.__class__.__name__,
            self.name,
            ', '.join(map(str, self.args))
        )

    def __str__(self):
        return '{}({})'.format(
            self.name,
            ', '.join(map(str, self.args))
        )
