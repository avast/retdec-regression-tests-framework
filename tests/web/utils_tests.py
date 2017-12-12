"""
    Tests for the :mod:`regression_tests.web.utils` module.
"""

import unittest

from regression_tests.test_case import TestCaseName
from regression_tests.web.utils import interactive_case_name
from regression_tests.web.utils import limit_shown_commits


class InteractiveCaseNameTests(unittest.TestCase):
    """Tests for `interactive_case_name()`."""

    def test_puts_proper_onclick_action_for_tool_with_args(self):
        self.assertEqual(
            interactive_case_name(
                TestCaseName('TestCase (file.exe -a x86)'),
                'dir.subdir'
            ),
            """TestCase (<span class="tool-args" """
            """onclick="showToolArgs('file.exe -a x86', this);" """
            """title="Show tool arguments">file.exe -a x86</span>)"""
        )

    def test_puts_proper_onclick_action_for_tool_without_args(self):
        # It checks that there is no redundant space after the input file when
        # there are no additional tool arguments.
        self.assertEqual(
            interactive_case_name(
                TestCaseName('TestCase (file.exe)'),
                'dir.subdir'
            ),
            """TestCase (<span class="tool-args" """
            """onclick="showToolArgs('file.exe', this);" """
            """title="Show tool arguments">file.exe</span>)"""
        )

    def test_shortens_long_case_name_when_limit_is_given(self):
        self.assertEqual(
            interactive_case_name(
                TestCaseName('TestCase (file.exe)'),
                'dir.subdir',
                limit=2
            ),
            """TestCase (<span class="tool-args" """
            # In the tool arguments shown on click, we want to display the
            # complete, uncut version of the arguments.
            """onclick="showToolArgs('file.exe', this);" """
            # Here, we check that the case name is properly shortened.
            """title="Show tool arguments">file[..]</span>)"""
        )


class LimitShownCommitsTests(unittest.TestCase):
    """Tests for `limit_shown_commits()`."""

    def test_returns_max_count_when_selected_count_is_zero(self):
        self.assertEqual(limit_shown_commits('0', 5), 5)

    def test_returns_selected_count_when_less_than_max_count(self):
        self.assertEqual(limit_shown_commits('4', 5), 4)

    def test_returns_max_count_when_more_than_max_count(self):
        self.assertEqual(limit_shown_commits('6', 5), 5)

    def test_returns_max_count_when_selected_count_is_invalid(self):
        self.assertEqual(limit_shown_commits('a', 5), 5)
