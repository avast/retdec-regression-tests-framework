"""
    Tests for the
    :module`regression_tests.parsers.c_parser.exprs.init_list_expr` module.
"""

from tests.parsers.c_parser import WithModuleTests


class InitListExprTests(WithModuleTests):
    """Tests for `InitListExpr`."""

    def get_init_list_expr(self, type, init_list):
        code = '{} a[] = {};'.format(type, init_list)
        module = self.parse(code)
        return module.global_vars[0].initializer

    def test_values_returns_correct_values(self):
        initializer = self.get_array_initializer('{1, 2.0, 3}', 'float')
        self.assertEqual(len(initializer.values), 3)
        self.assertEqual(initializer.values[0], 1)
        self.assertEqual(initializer.values[1], 2.0)
        self.assertEqual(initializer.values[2], 3)

    def test_values_returns_expressions(self):
        module = self.parse("""
            int a = 2;
            int *p = &a;
            int array[2] = {*p, 42};
        """)
        array = module.global_vars['array']
        self.assertEqual(array.initializer, ['*p', 42])

    def test_type_returns_correct_type(self):
        initializer = self.get_array_initializer('{1, 2, 3}', 'int')
        self.assertTrue(initializer.type.is_array())
        self.assertTrue(initializer.type.element_type.is_int())
        self.assertEqual(initializer.type.element_count, 3)

    def test_two_identical_initializers_are_equal(self):
        initializer = self.get_array_initializer('{1, 2, 3}', 'int')
        self.assertEqual(initializer, initializer)

    def test_two_differnt_initializers_are_not_equal(self):
        initializer1 = self.get_array_initializer('{1, 2, 3}', 'int')
        initializer2 = self.get_array_initializer('{1.0, 2.1, 3.0}', 'double')
        self.assertNotEqual(initializer1, initializer2)

    def test_brackets_operator_works_returns_correct_values(self):
        init_list = self.get_init_list_expr('float', '{2.5, 5, 42}')
        self.assertEqual(init_list[0], 2.5)
        self.assertEqual(init_list[1], 5)
        self.assertEqual(init_list[2], 42)

    def test_it_is_possible_to_access_expression_using_brackets_operator(self):
        module = self.parse("""
            int a = 2;
            int *p = &a;
            int array[1] = {*p};
        """)
        array = module.global_vars['array']
        self.assertTrue(array.initializer[0].is_deref_op())

    def test_brackets_operator_raises_index_error_when_empty_initializer(self):
        init_list = self.get_init_list_expr('int', '{}')
        with self.assertRaises(IndexError):
            init_list[0]

    def test_len_returns_correct_value(self):
        init_list = self.get_init_list_expr('int', '{2, 5, 42}')
        self.assertEqual(len(init_list), 3)

    def test_repr_returns_correct_repr(self):
        init_list = self.get_init_list_expr('int', '{2, 5, 42}')
        self.assertEqual(repr(init_list), '<InitListExpr {2, 5, 42}>')

    def test_str_returns_correct_str(self):
        init_list = self.get_init_list_expr('float', '{2, 5.0, 42}')
        self.assertEqual(str(init_list), '{2, 5.0, 42}')

    def test_two_equal_initializers_have_same_hash(self):
        initializer1 = self.get_array_initializer('{1, 2, 3}', 'int')
        initializer2 = self.get_array_initializer('{1, 2, 3}', 'int')
        self.assertEqual(initializer1, initializer2)
        self.assertEqual(hash(initializer1), hash(initializer2))
