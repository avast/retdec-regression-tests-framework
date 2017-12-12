"""
    Tests for the :mod:`regression_tests.tools.unpacker_test` module.
"""

import unittest
from unittest import mock

from regression_tests.tools.unpacker import Unpacker
from regression_tests.tools.unpacker_test import UnpackerTest
from regression_tests.tools.unpacker_test_settings import UnpackerTestSettings


class UnpackerTestTests(unittest.TestCase):
    """Tests for `UnpackerTest`."""

    def setUp(self):
        self.unpacker = mock.Mock(spec_set=Unpacker)
        self.test_settings = mock.Mock(spec_set=UnpackerTestSettings)

    # The method cannot be named 'create_test' because unittest then treats it
    # as a test method.
    def create(self, **kwargs):
        """Creates an instance of `UnpackerTest`."""
        return UnpackerTest(self.unpacker, self.test_settings)

    def test_fileinfo_delegates_to_unpacker_fileinfo(self):
        test = self.create()
        self.assertEqual(test.fileinfo, self.unpacker.fileinfo)
