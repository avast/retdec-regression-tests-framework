"""
    Tests for the :module`regression_tests.parsers.c_parser.stmts.loop` module.
"""

from tests.parsers.c_parser import WithModuleTests


class SwitchStmtTests(WithModuleTests):
    """Tests for `Loop`."""

    def get_for_loop(self, code):
        """Returns the first for loop in the given code."""
        func = self.get_func("""
            void foo(void) {
                %s
            }
        """ % code, 'foo')
        return func.for_loops[0]

    def get_while_loop(self, code):
        """Returns the first while loop in the given code."""
        func = self.get_func("""
            void foo(void) {
                %s
            }
        """ % code, 'foo')
        return func.while_loops[0]

    def get_do_while_loop(self, code):
        """Returns the first do while loop in the given code."""
        func = self.get_func("""
            void foo(void) {
                %s
            }
        """ % code, 'foo')
        return func.do_while_loops[0]

    def test_has_any_break_stmts_returns_false_if_loop_has_none(self):
        loop = self.get_while_loop('while(1) {}')
        self.assertFalse(loop.has_any_break_stmts())

    def test_has_any_break_stmts_returns_true_if_loop_has_some(self):
        loop = self.get_do_while_loop('do { break; } while(1);')
        self.assertTrue(loop.has_any_break_stmts())

    def test_all_break_stmts_are_found(self):
        loop = self.get_for_loop("""
            for (int i=0; i<10; i++) {
                break;
                if(1);
                break;
            }
        """)
        self.assertEqual(len(loop.break_stmts), 2)

    def test_break_stmts_inside_nested_loop_do_not_belong_to_enclosing_loop(self):
        func = self.get_func("""
            void foo() {
                while(1) {
                    do {
                        break;
                    } while(1)
                }
            }
        """, 'foo')
        self.assertFalse(func.while_loops[0].has_any_break_stmts())
        self.assertTrue(func.do_while_loops[0].has_any_break_stmts())

    def test_has_any_continue_stmts_returns_false_if_loop_has_none(self):
        loop = self.get_while_loop('while(1) {}')
        self.assertFalse(loop.has_any_continue_stmts())

    def test_has_any_continue_stmts_returns_true_if_loop_has_some(self):
        loop = self.get_do_while_loop('do { continue; } while(1);')
        self.assertTrue(loop.has_any_continue_stmts())

    def test_all_continue_stmts_are_found(self):
        loop = self.get_for_loop("""
            for (int i=0; i<10; i++) {
                continue;
                if(1);
                continue;
            }
        """)
        self.assertEqual(len(loop.continue_stmts), 2)

    def test_continue_stmts_inside_nested_loop_do_not_belong_to_enclosing_loop(self):
        func = self.get_func("""
            void foo() {
                while(1) {
                    do {
                        continue;
                    } while(1)
                }
            }
        """, 'foo')
        self.assertFalse(func.while_loops[0].has_any_continue_stmts())
        self.assertTrue(func.do_while_loops[0].has_any_continue_stmts())
