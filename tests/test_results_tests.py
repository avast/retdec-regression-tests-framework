"""
    Tests for the :mod:`regression_tests.test_results` module.
"""

from datetime import datetime
import unittest

from regression_tests.test_case import TestCaseName
from regression_tests.test_results import NoTestResults
from regression_tests.test_results import TestResults
from regression_tests.test_results import TestsResults


def create_test_results(module_name='module', case_name='Test (input.exe)',
                        start_date=datetime.now(), end_date=datetime.now(),
                        run_tests=1, failed_tests=0, skipped_tests=0, output=''):
    """Creates a TestResults object from the given parameters."""
    return TestResults(
        module_name,
        case_name,
        start_date,
        end_date,
        run_tests,
        failed_tests,
        skipped_tests,
        output,
    )


class TestResultsTests(unittest.TestCase):
    """Tests for `TestResults`."""

    def test_module_name_returns_correct_value(self):
        MODULE_NAME = 'my_module'
        test_results = create_test_results(module_name=MODULE_NAME)
        self.assertEqual(test_results.module_name, MODULE_NAME)

    def test_case_name_returns_correct_value(self):
        CASE_NAME = 'TestCase'
        test_results = create_test_results(case_name=CASE_NAME)
        self.assertEqual(test_results.case_name, CASE_NAME)

    def test_case_name_returns_instance_of_TestCaseName(self):
        test_results = create_test_results()
        self.assertIsInstance(test_results.case_name, TestCaseName)

    def test_full_name_returns_correct_value(self):
        test_results = create_test_results(module_name='module', case_name='Case')
        self.assertEqual(test_results.full_name, 'module.Case')

    def test_start_date_returns_correct_value(self):
        START_DATE = datetime.now()
        test_results = create_test_results(start_date=START_DATE)
        self.assertEqual(test_results.start_date, START_DATE)

    def test_end_date_returns_correct_value(self):
        END_DATE = datetime.now()
        test_results = create_test_results(end_date=END_DATE)
        self.assertEqual(test_results.end_date, END_DATE)

    def test_runtime_returns_correct_value_when_test_ended(self):
        START_DATE = datetime(2014, 9, 16, 11, 23, 20)
        END_DATE = datetime(2014, 9, 16, 11, 23, 30)
        test_results = create_test_results(start_date=START_DATE, end_date=END_DATE)
        self.assertEqual(test_results.runtime, 10)

    def test_runtime_returns_correct_value_when_test_not_started(self):
        END_DATE = datetime.now()
        test_results = create_test_results(start_date=None, end_date=END_DATE)
        self.assertIsNone(test_results.runtime, None)

    def test_runtime_returns_correct_value_when_test_not_ended(self):
        START_DATE = datetime.now()
        test_results = create_test_results(start_date=START_DATE, end_date=None)
        self.assertIsNone(test_results.runtime)

    def test_run_tests_returns_correct_value(self):
        RUN_TESTS = 5
        test_results = create_test_results(run_tests=RUN_TESTS)
        self.assertEqual(test_results.run_tests, RUN_TESTS)

    def test_failed_tests_returns_correct_value(self):
        FAILED_TESTS = 5
        test_results = create_test_results(failed_tests=FAILED_TESTS)
        self.assertEqual(test_results.failed_tests, FAILED_TESTS)

    def test_skipped_tests_returns_correct_value(self):
        SKIPPED_TESTS = 5
        test_results = create_test_results(skipped_tests=SKIPPED_TESTS)
        self.assertEqual(test_results.skipped_tests, SKIPPED_TESTS)

    def test_succeeded_tests_returns_correct_value(self):
        test_results = create_test_results(run_tests=10, failed_tests=4)
        self.assertEqual(test_results.succeeded_tests, 6)

    def test_succeeded_returns_true_when_there_are_no_run_tests(self):
        test_results = create_test_results(run_tests=0, failed_tests=0)
        self.assertTrue(test_results.succeeded)

    def test_succeeded_returns_true_when_there_are_no_failed_tests(self):
        test_results = create_test_results(run_tests=10, failed_tests=0)
        self.assertTrue(test_results.succeeded)

    def test_succeeded_returns_false_when_there_are_failed_tests(self):
        test_results = create_test_results(run_tests=10, failed_tests=2)
        self.assertFalse(test_results.succeeded)

    def test_failed_returns_false_when_there_are_no_run_tests(self):
        test_results = create_test_results(run_tests=0, failed_tests=0)
        self.assertFalse(test_results.failed)

    def test_failed_returns_false_when_there_are_no_failed_tests(self):
        test_results = create_test_results(run_tests=10, failed_tests=0)
        self.assertFalse(test_results.failed)

    def test_failed_returns_true_when_there_are_failed_tests(self):
        test_results = create_test_results(run_tests=10, failed_tests=2)
        self.assertTrue(test_results.failed)

    def test_skipped_returns_false_when_there_are_no_skipped_tests(self):
        test_results = create_test_results(run_tests=10, skipped_tests=0)
        self.assertFalse(test_results.skipped)

    def test_skipped_returns_true_when_there_are_skipped_tests(self):
        test_results = create_test_results(run_tests=10, skipped_tests=2)
        self.assertTrue(test_results.skipped)

    def test_output_returns_correct_value(self):
        OUTPUT = 'test output'
        test_results = create_test_results(output=OUTPUT)
        self.assertEqual(test_results.output, OUTPUT)

    def test_module_names_returns_correct_value(self):
        MODULE_NAME = 'my_module'
        test_results = create_test_results(module_name=MODULE_NAME)
        self.assertEqual(test_results.module_names, [MODULE_NAME])

    def test_case_names_returns_correct_value(self):
        CASE_NAME = 'TestCase'
        test_results = create_test_results(case_name=CASE_NAME)
        self.assertEqual(test_results.case_names, [CASE_NAME])

    def test_failed_module_names_returns_empty_list_when_no_tests_failed(self):
        test_results = create_test_results(failed_tests=0)
        self.assertEqual(test_results.failed_module_names, [])

    def test_failed_module_names_returns_list_with_module_name_when_some_tests_failed(self):
        test_results = create_test_results(
            module_name='module',
            run_tests=3,
            failed_tests=2
        )
        self.assertEqual(test_results.failed_module_names, ['module'])

    def test_has_run_returns_false_when_no_tests_run(self):
        test_results = create_test_results(run_tests=0)
        self.assertFalse(test_results.has_run())

    def test_has_run_returns_true_when_some_tests_run(self):
        test_results = create_test_results(run_tests=1)
        self.assertTrue(test_results.has_run())


class NoTestResultsTests(unittest.TestCase):
    """Tests for `NoTestResults`."""

    def test_properties_return_correct_values(self):
        MODULE_NAME = 'module'
        CASE_NAME = 'case'
        test_results = NoTestResults(MODULE_NAME, CASE_NAME)
        self.assertEqual(test_results.module_name, MODULE_NAME)
        self.assertEqual(test_results.case_name, CASE_NAME)
        self.assertEqual(test_results.runtime, 0)
        self.assertEqual(test_results.run_tests, 0)
        self.assertEqual(test_results.failed_tests, 0)
        self.assertEqual(test_results.skipped_tests, 0)
        self.assertEqual(test_results.output, '')


class TestsResultsTests(unittest.TestCase):
    """Tests for `TestsResults`."""

    def test_tests_results_represent_correct_test_results(self):
        TESTS_RESULTS = [create_test_results()]
        tests_results = TestsResults(TESTS_RESULTS)
        self.assertEqual(tests_results, TESTS_RESULTS)

    def test_module_names_returns_ordered_list_without_duplicates(self):
        tests_results = TestsResults([
            create_test_results(module_name='module2'),
            create_test_results(module_name='module1'),
            create_test_results(module_name='module2')  # same as the first name
        ])
        self.assertEqual(tests_results.module_names, ['module1', 'module2'])

    def test_module_names_sorts_them_so_external_and_integration_tests_are_put_first(self):
        tests_results = TestsResults([
            create_test_results(module_name='bugs.1537'),
            create_test_results(module_name='tools.fileinfo.sample'),
            create_test_results(module_name='integration.current.ack'),
            create_test_results(module_name='integration.2015-03-30.ack'),
            create_test_results(module_name='external.unit-tests'),
        ])
        self.assertEqual(
            tests_results.module_names,
            [
                'external.unit-tests',
                'integration.current.ack',
                'integration.2015-03-30.ack',
                'bugs.1537',
                'tools.fileinfo.sample'
            ]
        )

    def test_test_case_names_returns_ordered_list_without_duplicates(self):
        tests_results = TestsResults([
            create_test_results(case_name='case1'),
            create_test_results(case_name='case2'),
            create_test_results(case_name='case1')  # same as the first name
        ])
        self.assertEqual(tests_results.case_names, ['case1', 'case2'])

    def test_failed_module_names_returns_correct_list_when_some_tests_failed(self):
        tests_results = TestsResults([
            create_test_results(
                module_name='module1',
                run_tests=3,
                failed_tests=2
            ),
            create_test_results(
                module_name='module2',
                run_tests=1,
                failed_tests=1
            )
        ])
        self.assertEqual(
            tests_results.failed_module_names,
            ['module1', 'module2']
        )

    def test_run_tests_returns_correct_value(self):
        tests_results = TestsResults([
            create_test_results(run_tests=5),
            create_test_results(run_tests=2)
        ])
        self.assertEqual(tests_results.run_tests, 7)

    def test_run_multiple_tests_returns_true_if_two_tests_run(self):
        tests_results = TestsResults([
            create_test_results(run_tests=2)
        ])
        self.assertTrue(tests_results.run_multiple_tests)

    def test_run_multiple_tests_returns_false_if_one_test_run(self):
        tests_results = TestsResults([
            create_test_results(run_tests=1),
        ])
        self.assertFalse(tests_results.run_multiple_tests)

    def test_run_multiple_tests_returns_false_if_no_tests_run(self):
        tests_results = TestsResults([])
        self.assertFalse(tests_results.run_multiple_tests)

    def test_failed_tests_returns_correct_value(self):
        tests_results = TestsResults([
            create_test_results(run_tests=5, failed_tests=0),
            create_test_results(run_tests=5, failed_tests=1),
            create_test_results(run_tests=5, failed_tests=2)
        ])
        self.assertEqual(tests_results.failed_tests, 3)

    def test_skipped_tests_returns_correct_value(self):
        tests_results = TestsResults([
            create_test_results(run_tests=5, skipped_tests=0),
            create_test_results(run_tests=5, skipped_tests=1),
            create_test_results(run_tests=5, skipped_tests=2)
        ])
        self.assertEqual(tests_results.skipped_tests, 3)

    def test_succeeded_tests_returns_correct_value(self):
        tests_results = TestsResults([
            create_test_results(run_tests=5, failed_tests=0),
            create_test_results(run_tests=5, failed_tests=1),
            create_test_results(run_tests=5, failed_tests=2)
        ])
        self.assertEqual(tests_results.succeeded_tests, 12)

    def test_succeeded_returns_true_when_all_tests_succeeded(self):
        tests_results = TestsResults([
            create_test_results(run_tests=5, failed_tests=0),
            create_test_results(run_tests=5, failed_tests=0),
            create_test_results(run_tests=5, failed_tests=0)
        ])
        self.assertTrue(tests_results.succeeded)

    def test_succeeded_returns_false_when_not_all_tests_succeeded(self):
        tests_results = TestsResults([
            create_test_results(run_tests=5, failed_tests=0),
            create_test_results(run_tests=5, failed_tests=0),
            create_test_results(run_tests=5, failed_tests=1)
        ])
        self.assertFalse(tests_results.succeeded)

    def test_failed_returns_true_when_one_test_failed(self):
        tests_results = TestsResults([
            create_test_results(run_tests=5, failed_tests=0),
            create_test_results(run_tests=5, failed_tests=2),
            create_test_results(run_tests=5, failed_tests=0)
        ])
        self.assertTrue(tests_results.failed)

    def test_failed_returns_false_when_all_tests_succeeded(self):
        tests_results = TestsResults([
            create_test_results(run_tests=5, failed_tests=0),
            create_test_results(run_tests=5, failed_tests=0),
            create_test_results(run_tests=5, failed_tests=0)
        ])
        self.assertFalse(tests_results.failed)

    def test_skipped_returns_true_when_one_test_skipped(self):
        tests_results = TestsResults([
            create_test_results(run_tests=5, skipped_tests=0),
            create_test_results(run_tests=5, skipped_tests=2),
            create_test_results(run_tests=5, skipped_tests=0)
        ])
        self.assertTrue(tests_results.skipped)

    def test_skipped_returns_false_when_no_test_skipped(self):
        tests_results = TestsResults([
            create_test_results(run_tests=5, skipped_tests=0),
            create_test_results(run_tests=5, skipped_tests=0),
            create_test_results(run_tests=5, skipped_tests=0)
        ])
        self.assertFalse(tests_results.skipped)

    def test_start_date_returns_none_if_no_test_started(self):
        tests_results = TestsResults([
            create_test_results(start_date=None),
            create_test_results(start_date=None)
        ])
        self.assertFalse(tests_results.start_date)

    def test_start_date_returns_correct_date_if_one_test_started(self):
        START_DATE = datetime.now()
        tests_results = TestsResults([
            create_test_results(start_date=None),
            create_test_results(start_date=START_DATE)
        ])
        self.assertEqual(tests_results.start_date, START_DATE)

    def test_start_date_returns_correct_date_if_two_tests_started(self):
        START_DATE_FIRST = datetime(2014, 9, 16, 11, 28, 10)
        START_DATE_LAST = datetime(2014, 9, 16, 11, 28, 40)
        tests_results = TestsResults([
            create_test_results(start_date=None),
            create_test_results(start_date=START_DATE_FIRST),
            create_test_results(start_date=START_DATE_LAST)
        ])
        self.assertEqual(tests_results.start_date, START_DATE_FIRST)

    def test_end_date_returns_none_if_one_test_not_ended(self):
        tests_results = TestsResults([
            create_test_results(end_date=None),
            create_test_results(end_date=datetime.now())
        ])
        self.assertFalse(tests_results.end_date)

    def test_end_date_returns_correct_date_if_one_all_tests_ended(self):
        END_DATE_FIRST = datetime(2014, 9, 16, 11, 28, 10)
        END_DATE_LAST = datetime(2014, 9, 16, 11, 28, 40)
        tests_results = TestsResults([
            create_test_results(end_date=END_DATE_FIRST),
            create_test_results(end_date=END_DATE_LAST)
        ])
        self.assertEqual(tests_results.end_date, END_DATE_LAST)

    def test_runtime_returns_correct_value_when_all_tests_ended(self):
        tests_results = TestsResults([
            create_test_results(
                start_date=datetime(2014, 9, 16, 11, 28, 10),
                end_date=datetime(2014, 9, 16, 11, 28, 20)
            ),
            create_test_results(
                start_date=datetime(2014, 9, 16, 11, 28, 30),
                end_date=datetime(2014, 9, 16, 11, 28, 40)
            ),
        ])
        self.assertEqual(tests_results.runtime, 20)

    def test_runtime_returns_correct_value_when_test_not_started(self):
        tests_results = TestsResults([
            create_test_results(
                start_date=None,
                end_date=datetime(2014, 9, 16, 11, 28, 20)
            ),
            create_test_results(
                start_date=datetime(2014, 9, 16, 11, 28, 30),
                end_date=datetime(2014, 9, 16, 11, 28, 40)
            ),
        ])
        self.assertIsNone(tests_results.runtime)

    def test_runtime_returns_correct_value_when_test_not_ended(self):
        tests_results = TestsResults([
            create_test_results(
                start_date=datetime(2014, 9, 16, 11, 28, 20),
                end_date=None
            ),
            create_test_results(
                start_date=datetime(2014, 9, 16, 11, 28, 30),
                end_date=datetime(2014, 9, 16, 11, 28, 40)
            ),
        ])
        self.assertIsNone(tests_results.runtime)

    def test_has_run_returns_false_when_no_results(self):
        tests_results = TestsResults()
        self.assertFalse(tests_results.has_run())

    def test_has_run_returns_true_when_some_results(self):
        tests_results = TestsResults([create_test_results(run_tests=1)])
        self.assertTrue(tests_results.has_run())
