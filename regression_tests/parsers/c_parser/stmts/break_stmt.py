"""
    A representation of a ``break`` statement.
"""

from regression_tests.parsers.c_parser.stmts.statement import Statement


class BreakStmt(Statement):
    """A representation of a ``break`` statement."""

    def is_break_stmt(self):
        """Returns ``True``."""
        return True

    def __repr__(self):
        return '<{}>'.format(self.__class__.__name__)
