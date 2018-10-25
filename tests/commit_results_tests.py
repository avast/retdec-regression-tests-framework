"""
    Tests for the :mod:`regression_tests.commit_results` module.
"""

import unittest

from regression_tests.commit_results import CommitResults
from regression_tests.commit_results import CommitsResults
from regression_tests.test_results import NoTestResults
from regression_tests.test_results import TestsResults
from tests.git_tests import create_commit
from tests.retdec_builder_tests import create_build_info
from tests.test_results_tests import create_test_results


class CommitResultsTests(unittest.TestCase):
    """Tests for `CommitResults`."""

    def test_commit_resturns_correct_commit(self):
        COMMIT = create_commit()
        commit_results = CommitResults(COMMIT, TestsResults())
        self.assertEqual(commit_results.commit, COMMIT)

    def test_results_resturns_correct_results(self):
        TESTS_RESULTS = TestsResults()
        commit_results = CommitResults(create_commit(), TESTS_RESULTS)
        self.assertEqual(commit_results.results, TESTS_RESULTS)

    def test_build_info_resturns_correct_info(self):
        BUILD_INFO = create_build_info()
        commit_results = CommitResults(create_commit(), TestsResults(), BUILD_INFO)
        self.assertEqual(commit_results.build_info, BUILD_INFO)

    def test_module_names_returns_correct_names(self):
        TESTS_RESULTS = TestsResults([
            create_test_results(module_name='module2'),
            create_test_results(module_name='module1'),
            create_test_results(module_name='module2')  # same as the first name
        ])
        commit_results = CommitResults(create_commit(), TESTS_RESULTS)
        self.assertEqual(commit_results.module_names, ['module1', 'module2'])

    def test_module_names_sorts_them_so_external_and_integration_tests_are_put_first(self):
        TESTS_RESULTS = TestsResults([
            create_test_results(module_name='bugs.1537'),
            create_test_results(module_name='tools.fileinfo.sample'),
            create_test_results(module_name='integration.current.ack'),
            create_test_results(module_name='integration.2015-03-30.ack'),
            create_test_results(module_name='external.unit-tests'),
        ])
        commit_results = CommitResults(create_commit(), TESTS_RESULTS)
        self.assertEqual(
            commit_results.module_names,
            [
                'external.unit-tests',
                'integration.current.ack',
                'integration.2015-03-30.ack',
                'bugs.1537',
                'tools.fileinfo.sample'
            ]
        )

    def test_has_results_returns_false_when_no_results(self):
        commit_results = CommitResults(create_commit(), TestsResults())
        self.assertFalse(commit_results.has_results())

    def test_has_results_returns_true_when_there_are_results(self):
        commit_results = CommitResults(
            create_commit(),
            TestsResults([create_test_results()])
        )
        self.assertTrue(commit_results.has_results())

    def test_has_failed_tests_returns_true_if_test_failed(self):
        commit_results = CommitResults(
            create_commit(),
            TestsResults([create_test_results(run_tests=1, failed_tests=1)])
        )
        self.assertTrue(commit_results.has_failed_tests())

    def test_has_failed_tests_returns_false_if_no_test_failed(self):
        commit_results = CommitResults(
            create_commit(),
            TestsResults([create_test_results(run_tests=1, failed_tests=0)])
        )
        self.assertFalse(commit_results.has_failed_tests())

    def test_failed_tests_returns_correct_value(self):
        commit_results = CommitResults(
            create_commit(),
            TestsResults([create_test_results(run_tests=3, failed_tests=2)])
        )
        self.assertEqual(commit_results.failed_tests, 2)

    def test_failed_module_names_returns_correct_value(self):
        commit_results = CommitResults(
            create_commit(),
            TestsResults([
                create_test_results(
                    module_name='module',
                    run_tests=2,
                    failed_tests=1
                )
            ])
        )
        self.assertEqual(commit_results.failed_module_names, ['module'])

    def test_has_build_info_returns_false_when_no_build_info(self):
        commit_results = CommitResults(create_commit(), TestsResults())
        self.assertFalse(commit_results.has_build_info())

    def test_has_build_info_returns_true_when_there_is_build_info(self):
        commit_results = CommitResults(
            create_commit(),
            TestsResults(),
            create_build_info()
        )
        self.assertTrue(commit_results.has_build_info())

    def test_build_has_succeeded_returns_true_if_build_has_succeeded(self):
        commit_results = CommitResults(
            create_commit(),
            TestsResults(),
            create_build_info(succeeded=True)
        )
        self.assertTrue(commit_results.build_has_succeeded())

    def test_build_has_succeeded_returns_false_if_build_has_succeeded(self):
        commit_results = CommitResults(
            create_commit(),
            TestsResults(),
            create_build_info(succeeded=False)
        )
        self.assertFalse(commit_results.build_has_succeeded())

    def test_build_has_failed_returns_true_if_build_has_failed(self):
        commit_results = CommitResults(
            create_commit(),
            TestsResults(),
            create_build_info(succeeded=False)
        )
        self.assertTrue(commit_results.build_has_failed())

    def test_build_has_failed_returns_false_if_build_has_succeeded(self):
        commit_results = CommitResults(
            create_commit(),
            TestsResults(),
            create_build_info(succeeded=True)
        )
        self.assertFalse(commit_results.build_has_failed())


class CommitsResultsTests(unittest.TestCase):
    """Tests for `CommitsResults`."""

    def test_commits_results_represent_correct_commits_results(self):
        COMMITS_RESULTS = [CommitResults(create_commit(), TestsResults())]
        commits_results = CommitsResults(COMMITS_RESULTS)
        self.assertEqual(commits_results, COMMITS_RESULTS)

    def test_commits_returns_correct_commits(self):
        COMMIT1 = create_commit()
        COMMIT2 = create_commit()
        commits_results = CommitsResults([
            CommitResults(COMMIT1, TestsResults()),
            CommitResults(COMMIT2, TestsResults())
        ])
        self.assertEqual(commits_results.commits, [COMMIT1, COMMIT2])

    def test_results_returns_correct_results(self):
        TESTS_RESULTS1 = TestsResults([
            create_test_results(module_name='module1')
        ])
        TESTS_RESULTS2 = TestsResults([
            create_test_results(module_name='module2')
        ])
        commits_results = CommitsResults([
            CommitResults(create_commit(), TESTS_RESULTS1),
            CommitResults(create_commit(), TESTS_RESULTS2)
        ])
        self.assertEqual(
            commits_results.results,
            [TESTS_RESULTS1, TESTS_RESULTS2]
        )

    def test_build_infos_returns_correct_infos(self):
        BUILD_INFO1 = create_build_info()
        BUILD_INFO2 = create_build_info()
        commits_results = CommitsResults([
            CommitResults(create_commit(), TestsResults(), BUILD_INFO1),
            CommitResults(create_commit(), TestsResults(), BUILD_INFO2)
        ])
        self.assertEqual(
            commits_results.build_infos,
            [BUILD_INFO1, BUILD_INFO2]
        )

    def test_has_results_returns_false_when_no_results(self):
        commits_results = CommitsResults()
        self.assertFalse(commits_results.has_results())

    def test_has_results_returns_true_when_there_are_results(self):
        commits_results = CommitsResults([
            CommitResults(create_commit(), create_test_results()),
        ])
        self.assertTrue(commits_results.has_results())

    def test_results_for_module_returns_correct_results(self):
        TR1_MODULE1_A = create_test_results(module_name='module1')
        TR1_MODULE1_B = create_test_results(module_name='module1')
        TESTS_RESULTS1 = TestsResults([
            TR1_MODULE1_A,
            TR1_MODULE1_B,
            create_test_results(module_name='module2'),
        ])
        TESTS_RESULTS2 = TestsResults([
            create_test_results(module_name='module3')
        ])
        TR3_MODULE1 = create_test_results(module_name='module1')
        TESTS_RESULTS3 = TestsResults([
            TR3_MODULE1
        ])
        COMMIT1 = create_commit()
        COMMIT2 = create_commit()
        COMMIT3 = create_commit()
        commits_results = CommitsResults([
            CommitResults(COMMIT1, TESTS_RESULTS1),
            CommitResults(COMMIT2, TESTS_RESULTS2),
            CommitResults(COMMIT3, TESTS_RESULTS3)
        ])
        rfm1 = commits_results.results_for_module('module1')
        self.assertEqual(len(rfm1), len(commits_results))
        self.assertEqual(len(rfm1[0].results), 2)
        self.assertEqual(rfm1[0].commit, COMMIT1)
        self.assertEqual(rfm1[0].results[0], TR1_MODULE1_A)
        self.assertEqual(rfm1[0].results[1], TR1_MODULE1_B)
        self.assertEqual(len(rfm1[1].results), 0)
        self.assertEqual(rfm1[1].commit, COMMIT2)
        self.assertEqual(len(rfm1[2].results), 1)
        self.assertEqual(rfm1[2].commit, COMMIT3)
        self.assertEqual(rfm1[2].results[0], TR3_MODULE1)

    def test_results_for_case_returns_correct_results(self):
        TR1_MODULE1_CASEA = create_test_results(
            module_name='module1', case_name='caseA')
        TESTS_RESULTS1 = TestsResults([
            TR1_MODULE1_CASEA,
            create_test_results(module_name='module1', case_name='caseB'),
            create_test_results(module_name='module2', case_name='caseC')
        ])
        TESTS_RESULTS2 = TestsResults([
            create_test_results(module_name='module2', case_name='caseD')
        ])
        TR3_MODULE1_CASEA = create_test_results(
            module_name='module1', case_name='caseA')
        TESTS_RESULTS3 = TestsResults([
            TR3_MODULE1_CASEA,
            create_test_results(module_name='module2', case_name='caseF')
        ])
        COMMIT1 = create_commit()
        COMMIT2 = create_commit()
        COMMIT3 = create_commit()
        commits_results = CommitsResults([
            CommitResults(COMMIT1, TESTS_RESULTS1),
            CommitResults(COMMIT2, TESTS_RESULTS2),
            CommitResults(COMMIT3, TESTS_RESULTS3)
        ])
        rfm1cA = commits_results.results_for_case('module1', 'caseA')
        self.assertEqual(len(rfm1cA), 3)
        self.assertEqual(rfm1cA[0].results, TR1_MODULE1_CASEA)
        self.assertEqual(rfm1cA[0].commit, COMMIT1)
        self.assertIsInstance(rfm1cA[1].results, NoTestResults)
        self.assertEqual(rfm1cA[1].commit, COMMIT2)
        self.assertEqual(rfm1cA[2].results, TR3_MODULE1_CASEA)
        self.assertEqual(rfm1cA[2].commit, COMMIT3)

    def test_module_names_returns_correct_names(self):
        commits_results = CommitsResults([
            CommitResults(create_commit(), TestsResults([
                create_test_results(module_name='module2'),
                create_test_results(module_name='module1'),
                create_test_results(module_name='module2')  # same as the first name
            ])),
            CommitResults(create_commit(), TestsResults([
                create_test_results(module_name='module3'),
                create_test_results(module_name='module1')
            ]))
        ])
        self.assertEqual(
            commits_results.module_names,
            ['module1', 'module2', 'module3']
        )

    def test_module_names_sorts_them_so_external_and_integration_tests_are_put_first(self):
        commits_results = CommitsResults([
            CommitResults(create_commit(), TestsResults([
                create_test_results(module_name='bugs.1537'),
                create_test_results(module_name='tools.fileinfo.sample')
            ])),
            CommitResults(create_commit(), TestsResults([
                create_test_results(module_name='integration.current.ack'),
                create_test_results(module_name='integration.2015-03-30.ack')
            ])),
            CommitResults(create_commit(), TestsResults([
                create_test_results(module_name='external.unit-tests'),
            ]))
        ])
        self.assertEqual(
            commits_results.module_names,
            [
                'external.unit-tests',
                'integration.current.ack',
                'integration.2015-03-30.ack',
                'bugs.1537',
                'tools.fileinfo.sample'
            ]
        )

    def test_case_names_for_module_returns_correct_names(self):
        commits_results = CommitsResults([
            CommitResults(create_commit(), TestsResults([
                create_test_results(module_name='module1', case_name='caseA'),
                create_test_results(module_name='module1', case_name='caseB'),
                create_test_results(module_name='module2', case_name='caseC')
            ])),
            CommitResults(create_commit(), TestsResults([
                create_test_results(module_name='module1', case_name='caseD'),
                create_test_results(module_name='module2', case_name='caseE')
            ]))
        ])
        self.assertEqual(
            commits_results.case_names_for_module('module1'),
            ['caseA', 'caseB', 'caseD']
        )
