"""
    A representation of a ``do while`` loop.
"""

from regression_tests.parsers.c_parser.exprs.expression import Expression
from regression_tests.parsers.c_parser.stmts.loop import Loop
from regression_tests.parsers.c_parser.utils import nth_item
from regression_tests.utils import memoize


class DoWhileLoop(Loop):
    """A representation of a ``do while`` loop."""

    def is_do_while_loop(self):
        """Returns ``True``."""
        return True

    @property
    @memoize
    def condition(self):
        """Condition of the statement (:class:`.Expression`)."""
        cond = nth_item(1, self._node.get_children())
        return Expression._from_clang_node(cond)

    def __repr__(self):
        return '<{} condition={}>'.format(
            self.__class__.__name__,
            self.condition
        )

    def __str__(self):
        return 'do while ({})'.format(self.condition)
