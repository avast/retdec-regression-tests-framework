"""
    A representation of an empty statement.
"""

from regression_tests.parsers.c_parser.stmts.statement import Statement


class EmptyStmt(Statement):
    """A representation of an empty statement."""

    def is_empty_stmt(self):
        """Returns ``True``."""
        return True

    def __repr__(self):
        return '<{}>'.format(self.__class__.__name__)

    def __str__(self):
        return ''
