"""
    Tests for the :mod:`regression_tests.test` module.
"""

import unittest

from regression_tests.test import Test
from regression_tests.test_settings import CriticalTestSettings
from regression_tests.test_settings import TestSettings


class TestTests(unittest.TestCase):
    """Tests for `Test`."""

    def test_settings_returns_given_test_settings(self):
        TEST_SETTINGS = TestSettings(input='file.exe')
        test = Test(TEST_SETTINGS)
        self.assertEqual(test.settings, TEST_SETTINGS)

    def test_settings_cannot_be_changed(self):
        test = Test(TestSettings(input='file.exe'))
        with self.assertRaises(AttributeError):
            test.settings = TestSettings(input='file.exe')


class TestSettingsCombinationsTests(unittest.TestCase):
    """Tests for `Test.settings_combinations()`."""

    def test_returns_empty_list_upon_no_combinations(self):
        class MyTest(Test):
            pass

        self.assertEqual(MyTest.settings_combinations(), [])

    def test_returns_single_combination_upon_single_combination(self):
        class MyTest(Test):
            settings = TestSettings(input='file.exe')

        self.assertEqual(
            MyTest.settings_combinations(),
            [TestSettings(input='file.exe')]
        )

    def test_returns_three_combinations_upon_two_settings_with_three_combinations(self):
        class MyTest(Test):
            settings1 = TestSettings(input='file.exe')
            settings2 = TestSettings(input='file.exe', arch=['x86', 'arm'])

        self.assertEqual(MyTest.settings_combinations(), [
            TestSettings(input='file.exe'),
            TestSettings(input='file.exe', arch='x86'),
            TestSettings(input='file.exe', arch='arm')
        ])

    def test_recognizes_critical_settings(self):
        class MyTest(Test):
            settings1 = TestSettings(input='file.exe')
            settings2 = CriticalTestSettings(input='file.exe', arch='x86')

        self.assertEqual(MyTest.settings_combinations(only_critical=True), [
            CriticalTestSettings(input='file.exe', arch='x86'),
        ])

    def test_recognizes_settings_for_tool(self):
        class MyTest(Test):
            settings1 = TestSettings(input='file.exe', arch='x86')
            settings2 = TestSettings(tool='fileinfo', input='file.exe')

        self.assertEqual(MyTest.settings_combinations(only_for_tool='fileinfo'), [
            TestSettings(tool='fileinfo', input='file.exe'),
        ])
