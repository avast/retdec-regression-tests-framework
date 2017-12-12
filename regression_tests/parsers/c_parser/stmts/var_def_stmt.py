"""
    A representation of a variable definition statement.
"""

from regression_tests.parsers.c_parser.exprs.variable import Variable
from regression_tests.parsers.c_parser.stmts.statement import Statement
from regression_tests.parsers.c_parser.utils import remove_whitespace


class VarDefStmt(Statement):
    """A representation of a variable definition."""

    def is_var_def(self):
        """Returns ``True``."""
        return True

    def is_assign(self):
        """Is the defined variable also assigned a value?"""
        return self.var.initializer is not None

    @property
    def identification(self):
        """Returns string identifying the statement."""
        return remove_whitespace(self.str_without_type())

    @property
    def var(self):
        """Variable defined by this statement (:class:`.Variable`)."""
        return Variable(self._node)

    @property
    def initializer(self):
        """Initializer of the variable (:class:`.Expression`).

        If the variable has no initializer, it returns ``None``. Example:

        .. code-block:: c

            int i = 1;  // The initializer is 1.
            int j;      // No initializer.
        """
        return self.var.initializer

    @property
    def lhs(self):
        """If the statement is also an assignment, this contains the name of
        the assigned variable.

        :raises AssertionError: If the statement is not an assignment.
        """
        if not self.is_assign():
            raise AssertionError('Not an assignment')
        return self.var.name

    @property
    def rhs(self):
        """If the statement is also assignment, this contains the initializer.

        :raises AssertionError: If the statement is not assignment.
        """
        if not self.is_assign():
            raise AssertionError('Not an assignment')
        return self.initializer

    def str_without_type(self):
        """Returns string representation without type."""
        str = self.var.name
        if self.is_assign():
            str += ' = {}'.format(self.initializer)
        return str

    def __repr__(self):
        return '<{} name={} type={} initializer={}>'.format(
            self.__class__.__name__,
            self.var.name,
            self.var.type,
            self.var.initializer
        )

    def __str__(self):
        return '{} {}'.format(self.var.type, self.str_without_type())
