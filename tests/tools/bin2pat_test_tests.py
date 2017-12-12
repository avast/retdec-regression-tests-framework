"""
    Tests for the :mod:`regression_tests.tools.bin2pat_test` module.
"""

import unittest
from unittest import mock

from regression_tests.tools.bin2pat import Bin2Pat
from regression_tests.tools.bin2pat_test import Bin2PatTest
from regression_tests.tools.bin2pat_test_settings import Bin2PatTestSettings


class Bin2PatTestTests(unittest.TestCase):
    """Tests for `Bin2PatTest`."""

    def setUp(self):
        self.bin2pat = mock.Mock(spec_set=Bin2Pat)
        self.bin2pat.name = 'bin2pat'
        # The following variable has to be set so that ToolTest.__getattr__()
        # works correctly.
        self.bin2pat.safe_name = self.bin2pat.name

    def test_out_yara_returns_same_result_as_bin2pat_out_yara(self):
        test = Bin2PatTest(self.bin2pat, Bin2PatTestSettings(input='mod.o'))
        self.assertEqual(test.out_yara, test.bin2pat.out_yara)
