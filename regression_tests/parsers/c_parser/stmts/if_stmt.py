"""
    A representation of an ``if`` statement.
"""

from regression_tests.parsers.c_parser.exprs.expression import Expression
from regression_tests.parsers.c_parser.stmts.statement import Statement
from regression_tests.utils import memoize


class IfStmt(Statement):
    """A representation of an ``if`` statement.

    .. note::

        There is no ``else if`` statement in the C language (like ``elif`` in
        Python). Indeed, the following piece of code

        .. code-block:: c

            if (x < 0) {
                foo();
            } else if (x == 0) {
                bar();
            }

        is equivalent to

        .. code-block:: c

            if (x < 0) {
                foo();
            } else
                if (x == 0) {
                    bar();
                }

        Thus, the parsing of the former code results in the creation of two
        ``if`` statements, so there is no way of checking the presence of
        ``else if`` clauses. This is why this class does not support querying
        for ``else if`` clauses.
    """

    def is_if_stmt(self):
        """Returns ``True``."""
        return True

    @property
    @memoize
    def condition(self):
        """Condition of the statement (:class:`.Expression`)."""
        cond = next(self._node.get_children())
        return Expression._from_clang_node(cond)

    def has_else_clause(self):
        """Has the statement an ``else`` clause?"""
        return len(list(self._node.get_children())) == 3

    def __repr__(self):
        return '<{} condition={}>'.format(
            self.__class__.__name__,
            self.condition
        )

    def __str__(self):
        return 'if ({})'.format(self.condition)
