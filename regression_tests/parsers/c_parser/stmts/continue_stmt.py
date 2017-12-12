"""
    A representation of a ``continue`` statement.
"""

from regression_tests.parsers.c_parser.stmts.statement import Statement


class ContinueStmt(Statement):
    """A representation of a ``continue`` statement."""

    def is_continue_stmt(self):
        """Returns ``True``."""
        return True

    def __repr__(self):
        return '<{}>'.format(self.__class__.__name__)
