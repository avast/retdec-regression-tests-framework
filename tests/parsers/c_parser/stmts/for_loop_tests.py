"""
    Tests for the :module`regression_tests.parsers.c_parser.for_loop` module.
"""

from tests.parsers.c_parser import WithModuleTests


class ForLoopTests(WithModuleTests):
    """Tests for `ForLoop`."""

    def get_for_loop(self, code):
        """Returns the first for loop in the given code."""
        func = self.get_func("""
            void func() {
                %s
            }
        """ % code, 'func')
        return func.for_loops[0]

    def test_for_loop_is_a_for_loop(self):
        for_loop = self.get_for_loop('for (int i = 0; i < 10; ++i) {}')
        self.assertTrue(for_loop.is_for_loop())

    def test_for_loop_is_a_loop(self):
        for_loop = self.get_for_loop('for (int i = 0; i < 10; ++i) {}')
        self.assertTrue(for_loop.is_loop())

    def test_for_loop_is_no_other_kind_of_statement(self):
        for_loop = self.get_for_loop('for (int i = 0; i < 10; ++i) {}')
        self.assertFalse(for_loop.is_assign())
        self.assertFalse(for_loop.is_if_stmt())
        self.assertFalse(for_loop.is_var_def())
        self.assertFalse(for_loop.is_while_loop())
        self.assertFalse(for_loop.is_return_stmt())
        self.assertFalse(for_loop.is_empty_stmt())
        self.assertFalse(for_loop.is_break_stmt())
        self.assertFalse(for_loop.is_continue_stmt())
        self.assertFalse(for_loop.is_switch_stmt())
        self.assertFalse(for_loop.is_goto_stmt())
        self.assertFalse(for_loop.is_do_while_loop())

    def test_identification_returns_correct_value(self):
        for_loop = self.get_for_loop("""
            for (int i = 0; i < 10; ++i) {
                printf("Hello %d", i);
            }
        """)
        self.assertEqual(for_loop.identification, 'for(inti=0;i<10;++i)')

    def test_header_returns_correct_value_when_just_variables_and_numbers(self):
        for_loop = self.get_for_loop("""
            for (int i = 0; i < 10; ++i) {
                printf("Hello %d", i);
            }
        """)
        self.assertEqual(for_loop.header, 'int i = 0; i < 10; ++i')

    def test_header_returns_correct_value_when_function_call(self):
        for_loop = self.get_for_loop("""
            for (int i = 0; i < rand(); ++i) {
                printf("Hello %d", i);
            }
        """)
        self.assertEqual(for_loop.header, 'int i = 0; i < rand(); ++i')

    def test_header_returns_correct_value_when_prefix_increment_in_step(self):
        for_loop = self.get_for_loop("""
            for (int i = 0; i < 10; ++i) {
                printf("Hello %d", i);
            }
        """)
        self.assertEqual(for_loop.header, 'int i = 0; i < 10; ++i')

    def test_header_returns_correct_value_when_postfix_increment_in_step(self):
        for_loop = self.get_for_loop("""
            for (int i = 0; i < 10; i++) {
                printf("Hello %d", i);
            }
        """)
        self.assertEqual(for_loop.header, 'int i = 0; i < 10; i++')

    def test_header_returns_correct_value_when_prefix_decrement_in_step(self):
        for_loop = self.get_for_loop("""
            for (int i = 10; i > 0; --i) {
                printf("Hello %d", i);
            }
        """)
        self.assertEqual(for_loop.header, 'int i = 10; i > 0; --i')

    def test_header_returns_correct_value_when_postfix_decrement_in_step(self):
        for_loop = self.get_for_loop("""
            for (int i = 10; i > 0; i--) {
                printf("Hello %d", i);
            }
        """)
        self.assertEqual(for_loop.header, 'int i = 10; i > 0; i--')

    def test_for_loop_is_equal_to_itself(self):
        code = """
            for (int i = 10; i > 0; i--) {
                printf("Hello %d", i);
            }
        """

        for_loop_a = self.get_for_loop(code)

        self.assertEqual(for_loop_a, for_loop_a)

    def test_two_different_for_loops_are_not_equal(self):
        code = """
            for (int i = 10; i > 0; i--) {
                printf("Hello %d", i);
            }
        """

        for_loop_a = self.get_for_loop(code)

        code = """
            for (int j = 0; j < 5; i++) {
                printf("Hi %d", j);
            }
        """

        for_loop_b = self.get_for_loop(code)

        self.assertNotEqual(for_loop_a, for_loop_b)

    def test_repr_returns_correct_repr(self):
        code = """
            for (int i = 10; i > 0; i--) {
                printf("Hello %d", i);
            }
        """
        for_loop = self.get_for_loop(code)
        self.assertEqual(repr(for_loop), '<ForLoop header=(int i = 10; i > 0; i--)>')

    def test_str_returns_correct_str(self):
        code = """
            for (int i = 10; i > 0; i--) {
                printf("Hello %d", i);
            }
        """
        for_loop = self.get_for_loop(code)
        self.assertEqual(str(for_loop), 'for (int i = 10; i > 0; i--)')
