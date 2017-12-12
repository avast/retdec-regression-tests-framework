"""
    A representation of a ``goto`` statement.
"""

from regression_tests.parsers.c_parser.stmts.statement import Statement
from regression_tests.utils import memoize


class GotoStmt(Statement):
    """A representation of a ``goto`` statement."""

    def is_goto_stmt(self):
        """Returns ``True``."""
        return True

    @property
    @memoize
    def target(self):
        """Name of targeted label."""
        return next(self._node.get_children()).spelling

    def __eq__(self, other):
        return id(self) == id(other)

    def __hash__(self):
        return hash(id(self))

    def __repr__(self):
        return '<{} target={}>'.format(
            self.__class__.__name__,
            self.target
        )

    def __str__(self):
        return 'goto {}'.format(self.target)


class Label:
    """A representation of a ``label``."""

    def __init__(self, node):
        """
        :param node: Internal node representing the label.
        """
        self._node = node

    @property
    def identification(self):
        """Returns string identifying the label."""
        return str(self)[:-1]

    @property
    @memoize
    def name(self):
        """Name of the label."""
        return self._node.spelling

    def __repr__(self):
        return '<{} name={}>'.format(
            self.__class__.__name__,
            self.name
        )

    def __str__(self):
        return '{}:'.format(self.name)
