"""
    Tests for the :module`regression_tests.parsers.c_parser.include` module.
"""

import unittest

from regression_tests.parsers.c_parser.include import Include


class IncludeTests(unittest.TestCase):
    """Tests for `Include`."""

    def test_whitespace_before_and_after_include_is_stripped(self):
        include = Include('   #include <stdio.h>   ')
        self.assertEqual(include, '#include <stdio.h>')

    def test_file_returns_file_for_include_with_angle_brackets(self):
        include = Include('#include <stdio.h>')
        self.assertEqual(include.file, 'stdio.h')

    def test_file_returns_file_for_include_with_quotes(self):
        include = Include('#include "stdio.h"')
        self.assertEqual(include.file, 'stdio.h')

    def test_repr_returns_correct_value(self):
        include = Include('#include <stdio.h>')
        self.assertEqual(repr(include), "Include('#include <stdio.h>')")

    def test_two_includes_with_same_text_are_equal(self):
        include1 = Include('#include <stdio.h>')
        include2 = Include('#include <stdio.h>')
        self.assertEqual(include1, include2)

    def test_two_different_includes_are_not_equal(self):
        include1 = Include('#include <stdio.h>')
        include2 = Include('#include "stdio.h"')
        self.assertNotEqual(include1, include2)
