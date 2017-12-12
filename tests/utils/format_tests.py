"""
    Tests for the :mod:`regression_tests.utils.format` module.
"""

# The tests of format_age() and format_date() are taken from
# https://github.com/s3rvac/git-branch-viewer/blob/master/tests/format_tests.py

import datetime
import unittest

from regression_tests.utils.format import format_age
from regression_tests.utils.format import format_date
from regression_tests.utils.format import format_id
from regression_tests.utils.format import format_runtime


class FormatAgeWithNonNegativeAgesTests(unittest.TestCase):
    """Tests for `format_age()` with non-negative values."""

    def test_returns_correctly_formatted_age_zero_seconds(self):
        age = datetime.timedelta(seconds=0)
        self.assertEqual(format_age(age), '0 seconds')

    def test_returns_correctly_formatted_age_one_second(self):
        age = datetime.timedelta(seconds=1)
        self.assertEqual(format_age(age), '1 second')

    def test_returns_correctly_formatted_age_two_seconds(self):
        age = datetime.timedelta(seconds=2)
        self.assertEqual(format_age(age), '2 seconds')

    def test_returns_correctly_formatted_age_max_seconds(self):
        age = datetime.timedelta(seconds=59)
        self.assertEqual(format_age(age), '59 seconds')

    def test_returns_correctly_formatted_age_one_minute(self):
        age = datetime.timedelta(minutes=1)
        self.assertEqual(format_age(age), '1 minute')

    def test_returns_correctly_formatted_age_one_minute_and_some_seconds(self):
        age = datetime.timedelta(minutes=1, seconds=2)
        self.assertEqual(format_age(age), '1 minute')

    def test_returns_correctly_formatted_age_two_minutes(self):
        age = datetime.timedelta(minutes=2)
        self.assertEqual(format_age(age), '2 minutes')

    def test_returns_correctly_formatted_age_two_minutes_and_some_seconds(self):
        age = datetime.timedelta(minutes=2, seconds=5)
        self.assertEqual(format_age(age), '2 minutes')

    def test_returns_correctly_formatted_age_max_minutes(self):
        age = datetime.timedelta(minutes=59, seconds=59)
        self.assertEqual(format_age(age), '59 minutes')

    def test_returns_correctly_formatted_age_one_hour(self):
        age = datetime.timedelta(hours=1)
        self.assertEqual(format_age(age), '1 hour')

    def test_returns_correctly_formatted_age_one_hour_and_some_minutes(self):
        age = datetime.timedelta(hours=1, minutes=5)
        self.assertEqual(format_age(age), '1 hour')

    def test_returns_correctly_formatted_age_two_hours(self):
        age = datetime.timedelta(hours=2)
        self.assertEqual(format_age(age), '2 hours')

    def test_returns_correctly_formatted_age_two_hours_and_some_minutes(self):
        age = datetime.timedelta(hours=2, minutes=5)
        self.assertEqual(format_age(age), '2 hours')

    def test_returns_correctly_formatted_age_max_hours(self):
        age = datetime.timedelta(hours=23, minutes=59, seconds=59)
        self.assertEqual(format_age(age), '23 hours')

    def test_returns_correctly_formatted_age_one_day(self):
        age = datetime.timedelta(days=1)
        self.assertEqual(format_age(age), '1 day')

    def test_returns_correctly_formatted_age_one_day_and_some_hours(self):
        age = datetime.timedelta(days=1, hours=5)
        self.assertEqual(format_age(age), '1 day')

    def test_returns_correctly_formatted_age_two_days(self):
        age = datetime.timedelta(days=2)
        self.assertEqual(format_age(age), '2 days')

    def test_returns_correctly_formatted_age_two_days_and_some_hours(self):
        age = datetime.timedelta(days=2, hours=5)
        self.assertEqual(format_age(age), '2 days')


class FormatAgeWithNegativeAgesTests(unittest.TestCase):
    """Tests for `format_age()` with negative values."""

    def test_returns_correctly_formatted_age_minus_one_second(self):
        age = datetime.timedelta(seconds=-1)
        self.assertEqual(format_age(age), '-1 second')

    def test_returns_correctly_formatted_age_minus_two_seconds(self):
        age = datetime.timedelta(seconds=-2)
        self.assertEqual(format_age(age), '-2 seconds')

    def test_returns_correctly_formatted_age_minus_max_seconds(self):
        age = datetime.timedelta(seconds=-59)
        self.assertEqual(format_age(age), '-59 seconds')

    def test_returns_correctly_formatted_age_minus_one_minute(self):
        age = datetime.timedelta(minutes=-1)
        self.assertEqual(format_age(age), '-1 minute')

    def test_returns_correctly_formatted_age_minus_one_minute_and_some_seconds(self):
        age = datetime.timedelta(minutes=-1, seconds=-2)
        self.assertEqual(format_age(age), '-1 minute')

    def test_returns_correctly_formatted_age_minus_two_minutes(self):
        age = datetime.timedelta(minutes=-2)
        self.assertEqual(format_age(age), '-2 minutes')

    def test_returns_correctly_formatted_age_minus_two_minutes_and_some_seconds(self):
        age = datetime.timedelta(minutes=-2, seconds=-5)
        self.assertEqual(format_age(age), '-2 minutes')

    def test_returns_correctly_formatted_age_minus_max_minutes(self):
        age = datetime.timedelta(minutes=-59, seconds=-59)
        self.assertEqual(format_age(age), '-59 minutes')

    def test_returns_correctly_formatted_age_minus_one_hour(self):
        age = datetime.timedelta(hours=-1)
        self.assertEqual(format_age(age), '-1 hour')

    def test_returns_correctly_formatted_age_minus_one_hour_and_some_minutes(self):
        age = datetime.timedelta(hours=-1, minutes=-5)
        self.assertEqual(format_age(age), '-1 hour')

    def test_returns_correctly_formatted_age_minus_two_hours(self):
        age = datetime.timedelta(hours=-2)
        self.assertEqual(format_age(age), '-2 hours')

    def test_returns_correctly_formatted_age_minus_two_hours_and_some_minutes(self):
        age = datetime.timedelta(hours=-2, minutes=-5)
        self.assertEqual(format_age(age), '-2 hours')

    def test_returns_correctly_formatted_age_minus_max_hours(self):
        age = datetime.timedelta(hours=-23, minutes=-59, seconds=-59)
        self.assertEqual(format_age(age), '-23 hours')

    def test_returns_correctly_formatted_age_minus_one_day(self):
        age = datetime.timedelta(days=-1)
        self.assertEqual(format_age(age), '-1 day')

    def test_returns_correctly_formatted_age_minus_one_day_and_some_hours(self):
        age = datetime.timedelta(days=-1, hours=-5)
        self.assertEqual(format_age(age), '-1 day')

    def test_returns_correctly_formatted_age_minus_two_days(self):
        age = datetime.timedelta(days=-2)
        self.assertEqual(format_age(age), '-2 days')

    def test_returns_correctly_formatted_age_two_days_and_some_hours(self):
        age = datetime.timedelta(days=-2, hours=-5)
        self.assertEqual(format_age(age), '-2 days')


class FormatDateTests(unittest.TestCase):
    """Tests for `format_date()`."""

    def test_returns_dash_when_date_is_not_given(self):
        self.assertEqual(format_date(None), '-')

    def test_returns_correctly_formatted_date_when_date_is_given(self):
        date = datetime.datetime(2014, 6, 7, 14, 25, 2)
        self.assertEqual(format_date(date), '2014-06-07 14:25:02')


class FormatIdTests(unittest.TestCase):
    """Tests for `format_id()`."""

    def test_empty_string_is_converted_to_underscore(self):
        self.assertEqual(format_id(''), '_')

    def test_string_that_is_already_id_is_left_unchanged(self):
        STRING = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-'
        self.assertEqual(format_id(STRING), STRING)

    def test_invalid_characters_are_replaced_with_dash(self):
        self.assertEqual(format_id(' '), '-')
        self.assertEqual(format_id('%'), '-')
        self.assertEqual(format_id('@'), '-')
        # And so on...


class FormatRuntimeTests(unittest.TestCase):
    """Tests for `format_runtime()`."""

    def test_zero_seconds_is_formatted_correctly(self):
        self.assertEqual(format_runtime(0), '0.00s')

    def test_very_small_runtime_is_formatted_correctly(self):
        self.assertEqual(format_runtime(0.001), '0.00s')

    def test_half_second_is_formatted_correctly(self):
        self.assertEqual(format_runtime(0.5), '0.50s')

    def test_sixty_seconds_is_formatted_correctly(self):
        self.assertEqual(format_runtime(60), '1m 0s')

    def test_sixty_one_seconds_as_int_is_formatted_correctly(self):
        self.assertEqual(format_runtime(61), '1m 1s')

    def test_sixty_one_seconds_as_float_is_formatted_correctly(self):
        self.assertEqual(format_runtime(61.0), '1m 1s')
