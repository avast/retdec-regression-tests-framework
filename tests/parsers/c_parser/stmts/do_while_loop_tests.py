"""
    Tests for the :module`regression_tests.parsers.c_parser.stmts.do_while_loop` module.
"""

from tests.parsers.c_parser import WithModuleTests


class DoWhileLoopTests(WithModuleTests):
    """Tests for `DoWhileLoop`."""

    def get_do_while_loop(self, code, func_name):
        """Returns the first while loop in the given code."""
        func = self.get_func("""
            int %s(void) {
                %s
            }
        """ % (func_name, code), func_name)
        return func.do_while_loops[0]

    def test_do_while_loop_is_while_loop(self):
        while_loop = self.get_do_while_loop("do {;} while(1);", 'foo')
        self.assertTrue(while_loop.is_do_while_loop())

    def test_do_while_loop_is_loop(self):
        while_loop = self.get_do_while_loop("do {;} while(1);", 'foo')
        self.assertTrue(while_loop.is_loop())

    def test_while_loop_is_no_other_kind_of_statement(self):
        while_loop = self.get_do_while_loop("do {;} while(1);", 'foo')
        self.assertFalse(while_loop.is_for_loop())
        self.assertFalse(while_loop.is_assign())
        self.assertFalse(while_loop.is_if_stmt())
        self.assertFalse(while_loop.is_var_def())
        self.assertFalse(while_loop.is_while_loop())
        self.assertFalse(while_loop.is_return_stmt())
        self.assertFalse(while_loop.is_empty_stmt())
        self.assertFalse(while_loop.is_break_stmt())
        self.assertFalse(while_loop.is_continue_stmt())
        self.assertFalse(while_loop.is_switch_stmt())
        self.assertFalse(while_loop.is_goto_stmt())

    def test_identification_returns_correct_value(self):
        while_loop = self.get_do_while_loop("do {;} while(1);", 'foo')
        self.assertEqual(while_loop.identification, 'dowhile(1)')

    def test_correct_condition_is_extracted(self):
        while_loop = self.get_do_while_loop("do {;} while(1);", 'foo')
        self.assertEqual(while_loop.condition, '1')

    def test_while_loop_is_equal_to_itself(self):
        while_loop = self.get_do_while_loop("do {;} while(1);", 'foo')
        self.assertEqual(while_loop, while_loop)

    def test_two_different_while_loops_are_not_equal(self):
        while_loop1 = self.get_do_while_loop("do {;} while(1);", 'foo')
        while_loop2 = self.get_do_while_loop("do {;} while(2);", 'foo')
        self.assertNotEqual(while_loop1, while_loop2)

    def test_two_while_loops_with_same_string_representation_are_not_equal(self):
        while_loop1 = self.get_do_while_loop("do {;} while(1);", 'foo')
        while_loop2 = self.get_do_while_loop("do {;} while(1);", 'bar')
        self.assertNotEqual(while_loop1, while_loop2)

    def test_repr_returns_correct_repr(self):
        while_loop = self.get_do_while_loop("do {;} while(1);", 'foo')
        self.assertEqual(repr(while_loop), '<DoWhileLoop condition=1>')

    def test_str_returns_correct_str(self):
        while_loop = self.get_do_while_loop("do {;} while(1);", 'foo')
        self.assertEqual(str(while_loop), 'do while (1)')
