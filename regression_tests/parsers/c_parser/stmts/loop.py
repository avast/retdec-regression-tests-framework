"""
    A base class for loops (``for``, ``while``, ``do while``).
"""

from clang import cindex

from regression_tests.parsers.c_parser.stmts.statement import Statement
from regression_tests.utils import memoize


class Loop(Statement):
    """A base class for loops (``for``, ``while``, ``do while``)."""

    def __init__(self, node):
        super().__init__(node)
        self._break_stmts = []
        self._continue_stmts = []

    def is_loop(self):
        """Returns ``True``."""
        return True

    def has_any_break_stmts(self):
        """Does the loops's body contain any break statements?"""
        return bool(self.break_stmts)

    @property
    def break_stmts(self):
        """A list of break statements (:class:`.BreakStmt`)
        that the loop contains.
        """
        self._parse_loop_body()
        return self._break_stmts

    def has_any_continue_stmts(self):
        """Does the loops's body contain any continue statements?"""
        return bool(self.continue_stmts)

    @property
    def continue_stmts(self):
        """A list of continue statements (:class:`.ContinueStmt`)
        that the loop contains.
        """
        self._parse_loop_body()
        return self._continue_stmts

    @memoize
    def _parse_loop_body(self):
        def visit_children(parent_node):
            for node in parent_node.get_children():
                if node.kind in (cindex.CursorKind.FOR_STMT,
                                 cindex.CursorKind.WHILE_STMT,
                                 cindex.CursorKind.DO_STMT):
                    continue
                elif node.kind == cindex.CursorKind.BREAK_STMT:
                    self._break_stmts.append(Statement._from_clang_node(node))
                elif node.kind == cindex.CursorKind.CONTINUE_STMT:
                    self._continue_stmts.append(
                        Statement._from_clang_node(node))
                else:
                    visit_children(node)

        visit_children(self._node)
