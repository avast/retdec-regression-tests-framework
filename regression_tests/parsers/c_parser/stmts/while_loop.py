"""
    A representation of a ``while`` loop.
"""

from regression_tests.parsers.c_parser.exprs.expression import Expression
from regression_tests.parsers.c_parser.stmts.loop import Loop
from regression_tests.utils import memoize


class WhileLoop(Loop):
    """A representation of a ``while`` loop."""

    def is_while_loop(self):
        """Returns ``True``."""
        return True

    @property
    @memoize
    def condition(self):
        """Condition of the statement (:class:`.Expression`)."""
        cond = next(self._node.get_children())
        return Expression._from_clang_node(cond)

    def __repr__(self):
        return '<{} condition={}>'.format(
            self.__class__.__name__,
            self.condition
        )

    def __str__(self):
        return 'while ({})'.format(self.condition)
