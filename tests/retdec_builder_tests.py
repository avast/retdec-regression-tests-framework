"""
    Tests for the :mod:`regression_tests.retdec_builder` module.
"""

import unittest
from datetime import datetime

from regression_tests.retdec_builder import BuildInfo
from regression_tests.retdec_builder import NoBuildInfo


def create_build_info(start_date=datetime.now(), end_date=datetime.now(),
                      succeeded=True, log=''):
    """Creates a new `BuildInfo` from the given parameters."""
    return BuildInfo(start_date, end_date, succeeded, log)


class BuildInfoTests(unittest.TestCase):
    """Tests for `BuildInfo`."""

    def test_runtime_returns_correct_value_when_build_ended(self):
        build_info = create_build_info(
            start_date=datetime(2014, 9, 15, 11, 20, 1),
            end_date=datetime(2014, 9, 15, 11, 20, 11)
        )
        self.assertEqual(build_info.runtime, 10)

    def test_runtime_returns_none_when_build_not_ended(self):
        build_info = create_build_info(end_date=None)
        self.assertIsNone(build_info.runtime)

    def test_has_started_returns_false_when_not_started(self):
        build_info = create_build_info(start_date=None)
        self.assertFalse(build_info.has_started())

    def test_has_started_returns_true_when_started(self):
        build_info = create_build_info(start_date=datetime.now())
        self.assertTrue(build_info.has_started())

    def test_has_ended_returns_false_when_not_ended(self):
        build_info = create_build_info(end_date=None)
        self.assertFalse(build_info.has_ended())

    def test_has_ended_returns_true_when_ended(self):
        build_info = create_build_info(end_date=datetime.now())
        self.assertTrue(build_info.has_ended())


class NoBuildInfoTests(unittest.TestCase):
    """Tests for `NoBuildInfo`."""

    def test_has_started_returns_false(self):
        build_info = NoBuildInfo()
        self.assertFalse(build_info.has_started())
