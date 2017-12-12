"""
    A representation of a ``return`` statement.
"""

from regression_tests.parsers.c_parser.exprs.expression import Expression
from regression_tests.parsers.c_parser.stmts.statement import Statement
from regression_tests.utils import memoize


class ReturnStmt(Statement):
    """A representation of a ``return`` statement."""

    def is_return_stmt(self):
        """Returns ``True``."""
        return True

    def returns_something(self):
        """Does the return statement return something?"""
        return bool(self.return_expr)

    @property
    @memoize
    def return_expr(self):
        """Returned expression (:class:`.Expression`) or ``None``."""
        if any(self._node.get_children()):
            ret_expr = next(self._node.get_children())
            return Expression._from_clang_node(ret_expr)
        return None

    def __repr__(self):
        return '<{} return_expr={}>'.format(
            self.__class__.__name__,
            self.return_expr
        )

    def __str__(self):
        return 'return {}'.format(self.return_expr)
