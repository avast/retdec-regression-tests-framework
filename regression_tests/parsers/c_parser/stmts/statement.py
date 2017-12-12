"""
    A base class of all statements.
"""

from abc import ABCMeta

from clang import cindex

from regression_tests.parsers.c_parser.utils import remove_whitespace


class Statement(metaclass=ABCMeta):
    """A base class of all statements."""

    def __init__(self, node):
        """
        :param node: Internal node representing the statement.
        """
        self._node = node
        self._next_stmt = None
        self._children = []

    @property
    def identification(self):
        """Returns string identifying the statement."""
        return remove_whitespace(str(self))

    @property
    def next_stmt(self):
        """:class:`.Statement` following this statetement."""
        return self._next_stmt

    @next_stmt.setter
    def next_stmt(self, value):
        self._next_stmt = value

    def is_assign(self):
        """Is the statement an assignment?"""
        return False

    def is_loop(self):
        """Is the statement some kind of loop?"""
        return False

    def is_for_loop(self):
        """Is the statement a for loop?"""
        return False

    def is_while_loop(self):
        """Is the statement a while loop?"""
        return False

    def is_do_while_loop(self):
        """Is the statement a do while loop?"""
        return False

    def is_if_stmt(self):
        """Is the statement an if statement?"""
        return False

    def is_var_def(self):
        """Is the statement a variable definition?"""
        return False

    def is_return_stmt(self):
        """Is the statement a return statement?"""
        return False

    def is_empty_stmt(self):
        """Is the statement an empty statement?"""
        return False

    def is_break_stmt(self):
        """Is the statement a break statement?"""
        return False

    def is_continue_stmt(self):
        """Is the statement a continue statement?"""
        return False

    def is_switch_stmt(self):
        """Is the statement a switch statement?"""
        return False

    def is_goto_stmt(self):
        """Is the statement a goto statement?"""
        return False

    @staticmethod
    def _from_clang_node(node):
        """Creates a new statement from the given clang node.

        :param node: Internal node representing the statement.

        :raises AssertionError: If the statement is not supported.
        """
        if node.kind == cindex.CursorKind.FOR_STMT:
            return ForLoop(node)
        elif node.kind == cindex.CursorKind.WHILE_STMT:
            return WhileLoop(node)
        elif node.kind == cindex.CursorKind.DO_STMT:
            return DoWhileLoop(node)
        elif node.kind == cindex.CursorKind.IF_STMT:
            return IfStmt(node)
        elif node.kind == cindex.CursorKind.DECL_STMT:
            child = next(node.get_children())
            if child.kind == cindex.CursorKind.VAR_DECL:
                return VarDefStmt(child)
        elif node.kind == cindex.CursorKind.RETURN_STMT:
            return ReturnStmt(node)
        elif node.kind == cindex.CursorKind.NULL_STMT:
            return EmptyStmt(node)
        elif node.kind == cindex.CursorKind.BREAK_STMT:
            return BreakStmt(node)
        elif node.kind == cindex.CursorKind.CONTINUE_STMT:
            return ContinueStmt(node)
        elif node.kind == cindex.CursorKind.SWITCH_STMT:
            return SwitchStmt(node)
        elif node.kind == cindex.CursorKind.GOTO_STMT:
            return GotoStmt(node)

        raise AssertionError('unsupported statement `{}` of kind {}'.format(
            node.spelling, node.kind))


from regression_tests.parsers.c_parser.stmts.break_stmt import BreakStmt
from regression_tests.parsers.c_parser.stmts.continue_stmt import ContinueStmt
from regression_tests.parsers.c_parser.stmts.do_while_loop import DoWhileLoop
from regression_tests.parsers.c_parser.stmts.empty_stmt import EmptyStmt
from regression_tests.parsers.c_parser.stmts.for_loop import ForLoop
from regression_tests.parsers.c_parser.stmts.goto_stmt import GotoStmt
from regression_tests.parsers.c_parser.stmts.if_stmt import IfStmt
from regression_tests.parsers.c_parser.stmts.return_stmt import ReturnStmt
from regression_tests.parsers.c_parser.stmts.switch_stmt import SwitchStmt
from regression_tests.parsers.c_parser.stmts.var_def_stmt import VarDefStmt
from regression_tests.parsers.c_parser.stmts.while_loop import WhileLoop
