"""
    Tests for the :module`regression_tests.parsers.c_parser.comment` module.
"""

import re
import unittest

from regression_tests.parsers.c_parser.comment import Comment


class CommentTests(unittest.TestCase):
    """Tests for `Comment`."""

    def test_matches_returns_true_if_comment_matches_regexp_str(self):
        comment = Comment('// test')
        self.assertTrue(comment.matches(r'// test'))

    def test_matches_returns_true_if_comment_matches_compiled_regexp(self):
        comment = Comment('// test')
        self.assertTrue(comment.matches(re.compile(r'// test')))

    def test_matches_returns_false_if_comment_does_not_match_regexp(self):
        comment = Comment('// test')
        self.assertFalse(comment.matches(r'// Hello'))

    def test_matches_checks_whole_comment(self):
        comment = Comment('// test')
        self.assertFalse(comment.matches(r'//'))
        self.assertFalse(comment.matches(r'// tes'))
        self.assertTrue(comment.matches(r'// test'))

    def test_repr_returns_correct_value(self):
        comment = Comment('// test')
        self.assertEqual(repr(comment), "Comment('// test')")

    def test_two_comments_with_same_text_are_equal(self):
        comment1 = Comment('// test')
        comment2 = Comment('// test')
        self.assertEqual(comment1, comment2)

    def test_two_different_comments_are_not_equal(self):
        comment1 = Comment('// Hello Peter ')
        comment2 = Comment('// test')
        self.assertNotEqual(comment1, comment2)
