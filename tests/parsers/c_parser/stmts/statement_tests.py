"""
    Tests for the :module`regression_tests.parsers.c_parser.statement` module.
"""

from unittest import mock

from regression_tests.parsers.c_parser.stmts.break_stmt import BreakStmt
from regression_tests.parsers.c_parser.stmts.continue_stmt import ContinueStmt
from regression_tests.parsers.c_parser.stmts.do_while_loop import DoWhileLoop
from regression_tests.parsers.c_parser.stmts.empty_stmt import EmptyStmt
from regression_tests.parsers.c_parser.stmts.for_loop import ForLoop
from regression_tests.parsers.c_parser.stmts.goto_stmt import GotoStmt
from regression_tests.parsers.c_parser.stmts.if_stmt import IfStmt
from regression_tests.parsers.c_parser.stmts.return_stmt import ReturnStmt
from regression_tests.parsers.c_parser.stmts.statement import Statement
from regression_tests.parsers.c_parser.stmts.switch_stmt import SwitchStmt
from regression_tests.parsers.c_parser.stmts.while_loop import WhileLoop
from tests.parsers.c_parser import WithModuleTests


class StatementTests(WithModuleTests):
    """Tests for `Statement`."""

    def insert_into_function_body(self, code):
        """Returns function containing given code."""
        return self.get_func("""
            void func() {
                %s
            }
        """ % code, 'func')

    def get_for_loop(self, code):
        """Returns the first for loop in the given code."""
        func = self.insert_into_function_body(code)
        return func.for_loops[0]

    def get_while_loop(self, code):
        """Returns the first while loop in the given code."""
        func = self.insert_into_function_body(code)
        return func.while_loops[0]

    def get_do_while_loop(self, code):
        """Returns the first do while loop in the given code."""
        func = self.insert_into_function_body(code)
        return func.do_while_loops[0]

    def get_if_stmt(self, code):
        """Returns the first if stmt in the given code."""
        func = self.insert_into_function_body(code)
        return func.if_stmts[0]

    def get_return_stmt(self, code):
        """Returns the first return stmt in the given code."""
        func = self.insert_into_function_body(code)
        return func.return_stmts[0]

    def get_empty_stmt(self, code):
        """Returns the first empty stmt in the given code."""
        func = self.insert_into_function_body(code)
        return func.empty_stmts[0]

    def get_switch_stmt(self, code):
        """Returns the first switch stmt in the given code."""
        func = self.insert_into_function_body(code)
        return func.switch_stmts[0]

    def get_goto_stmt(self, code):
        """Returns the first goto stmt in the given code."""
        func = self.insert_into_function_body(code)
        return func.goto_stmts[0]

    def test_from_clang_node_returns_for_loop_stmt_for_for_loop(self):
        code = """
            for (int i = 10; i > 0; i--) {
                printf("Hello %d", i);
            }
        """
        stmt = self.get_for_loop(code)
        self.assertIsInstance(stmt, ForLoop)

    def test_from_clang_node_returns_if_stmt_for_if_statement(self):
        code = 'if (1) foo();'
        stmt = self.get_if_stmt(code)
        self.assertIsInstance(stmt, IfStmt)

    def test_from_clang_node_returns_while_loop_for_while_loop(self):
        code = 'while (1) {}'
        stmt = self.get_while_loop(code)
        self.assertIsInstance(stmt, WhileLoop)

    def test_from_clang_node_returns_do_while_loop_for_do_while_loop(self):
        code = 'do {} while (1)'
        stmt = self.get_do_while_loop(code)
        self.assertIsInstance(stmt, DoWhileLoop)

    def test_from_clang_node_returns_return_stmt_for_return_statement(self):
        code = 'return;'
        stmt = self.get_return_stmt(code)
        self.assertIsInstance(stmt, ReturnStmt)

    def test_from_clang_node_returns_empty_stmt_for_empty_statement(self):
        code = ';'
        stmt = self.get_empty_stmt(code)
        self.assertIsInstance(stmt, EmptyStmt)

    def test_from_clang_node_returns_break_stmt_for_break_statement(self):
        code = 'while (1) break;'
        while_loop = self.get_while_loop(code)
        break_node = list(while_loop._node.get_children())[1]
        stmt = Statement._from_clang_node(break_node)
        self.assertIsInstance(stmt, BreakStmt)

    def test_from_clang_node_returns_continue_stmt_for_continue_statement(self):
        code = 'while (1) continue;'
        while_loop = self.get_while_loop(code)
        continue_node = list(while_loop._node.get_children())[1]
        stmt = Statement._from_clang_node(continue_node)
        self.assertIsInstance(stmt, ContinueStmt)

    def test_from_clang_node_returns_switch_stmt_for_switch_statement(self):
        code = 'int a; switch (a) {}'
        stmt = self.get_switch_stmt(code)
        self.assertIsInstance(stmt, SwitchStmt)

    def test_from_clang_node_returns_goto_stmt_for_goto_statement(self):
        code = 'goto abc; abc: ;'
        stmt = self.get_goto_stmt(code)
        self.assertIsInstance(stmt, GotoStmt)

    def test_from_clang_node_raises_assertion_error_upon_unsupported_stmt(self):
        unsupported_node = mock.Mock()
        with self.assertRaisesRegex(AssertionError, r'.*unsupported.*'):
            Statement._from_clang_node(unsupported_node)
