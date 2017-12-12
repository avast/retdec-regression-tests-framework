"""
    Tests for the :mod:`regression_tests.io` module.
"""

import unittest

from regression_tests.io import strip_shell_colors


class StripShellColorsTests(unittest.TestCase):
    """Tests for `strip_shell_colors()`."""

    def test_does_nothing_when_there_are_no_colors(self):
        text = 'no colors'
        self.assertEqual(strip_shell_colors(text), text)

    def test_strips_colors_when_there_are_colors(self):
        text = '\x1b[01;33mcolored text\x1b[0m'
        self.assertEqual(strip_shell_colors(text), 'colored text')
