"""
    Tests for the :mod:`regression_tests.db` module.
"""

import unittest
from datetime import datetime

from regression_tests.db import DB
from regression_tests.db import InvalidBuildError
from regression_tests.db import InvalidCommitError
from tests.email_tests import create_email
from tests.git_tests import create_commit
from tests.retdec_builder_tests import create_build_info
from tests.test_results_tests import create_test_results


class DBTests(unittest.TestCase):
    """Tests for `DB`."""

    def setUp(self):
        # To use a SQLite :memory: database, we have to specify an empty URL.
        self.db = DB('sqlite://')

    def test_get_date_of_last_update_returns_minimal_date_when_no_results(self):
        self.assertEqual(self.db.get_date_of_last_update(), datetime.min)

    def test_get_unprocessed_commits_returns_empty_list_if_no_commits(self):
        commits = self.db.get_unprocessed_commits()
        self.assertEqual(commits, [])

    def test_get_unprocessed_commits_returns_empty_list_if_all_commits_with_build_info(self):
        commit1 = create_commit()
        self.db.insert_commit(commit1)
        self.db.insert_build_started_info(commit1, datetime.now())

        commit2 = create_commit()
        self.db.insert_commit(commit2)
        self.db.insert_build_started_info(commit2, datetime.now())

        commits = self.db.get_unprocessed_commits()
        self.assertEqual(commits, [])

    def test_get_unprocessed_commits_returns_commits_without_build_info(self):
        commit1 = create_commit()
        self.db.insert_commit(commit1)
        commit2 = create_commit()
        self.db.insert_commit(commit2)

        commits = self.db.get_unprocessed_commits()
        self.assertEqual(commits, [commit1, commit2])

    def test_get_topmost_commit_returns_none_when_no_commits(self):
        self.assertIsNone(self.db.get_topmost_commit())

    def test_get_topmost_commit_returns_topmost_commit_when_there_are_commits(self):
        commit1 = create_commit()
        self.db.insert_commit(commit1)
        commit2 = create_commit()
        self.db.insert_commit(commit2)

        self.assertEqual(self.db.get_topmost_commit(), commit2)

    def test_topmost_commit_has_succeeded_returns_true_if_succeeded(self):
        commit1 = create_commit()
        self.db.insert_commit(commit1)
        build_id = self.db.insert_build_started_info(commit1, datetime.now())
        self.db.insert_build_ended_info(build_id, create_build_info())
        test_results1 = create_test_results(
            module_name='module', run_tests=1, failed_tests=1)
        self.db.insert_test_results(test_results1, commit1)

        # Topmost commit.
        commit2 = create_commit()
        self.db.insert_commit(commit2)
        build_id = self.db.insert_build_started_info(commit2, datetime.now())
        self.db.insert_build_ended_info(build_id, create_build_info())
        test_results2 = create_test_results(
            module_name='module', run_tests=1, failed_tests=0)
        self.db.insert_test_results(test_results2, commit2)

        self.assertTrue(self.db.topmost_commit_has_succeeded())

    def test_topmost_commit_has_succeeded_returns_false_if_build_failed(self):
        commit = create_commit()
        self.db.insert_commit(commit)
        build_id = self.db.insert_build_started_info(commit, datetime.now())
        self.db.insert_build_ended_info(build_id, create_build_info(succeeded=False))

        self.assertFalse(self.db.topmost_commit_has_succeeded())

    def test_topmost_commit_has_succeeded_returns_false_if_test_failed(self):
        commit = create_commit()
        self.db.insert_commit(commit)
        build_id = self.db.insert_build_started_info(commit, datetime.now())
        self.db.insert_build_ended_info(build_id, create_build_info())
        test_results = create_test_results(
            module_name='module', run_tests=2, failed_tests=1)
        self.db.insert_test_results(test_results, commit)

        self.assertFalse(self.db.topmost_commit_has_succeeded())

    def test_topmost_commit_has_succeeded_returns_false_if_no_commit(self):
        self.assertFalse(self.db.topmost_commit_has_succeeded())

    def test_initialize_commit_records_inserts_commit_when_not_exists(self):
        commit = create_commit()

        self.db.initialize_commit_records(commit)

        self.assertEqual(len(self.db.get_results_for_recent_commits(2).results), 1)

    def test_initialize_commit_records_does_nothing_when_commit_already_exists_and_no_results(self):
        commit = create_commit()
        self.db.insert_commit(commit)

        self.db.initialize_commit_records(commit)

        self.assertEqual(len(self.db.get_results_for_recent_commits(2).results), 1)

    def test_initialize_commit_records_clears_build_records_when_build_info_is_present(self):
        commit = create_commit()
        self.db.insert_commit(commit)
        build_id = self.db.insert_build_started_info(commit, datetime.now())
        self.db.insert_build_ended_info(build_id, create_build_info())

        self.db.initialize_commit_records(commit)

        commit_results = self.db.get_results_for_commit(commit)
        self.assertFalse(commit_results.has_build_info())

    def test_initialize_commit_records_clears_results_when_results_are_present(self):
        commit = create_commit()
        self.db.insert_commit(commit)
        test_results = create_test_results(module_name='module', run_tests=1)
        self.db.insert_test_results(test_results, commit)

        self.db.initialize_commit_records(commit)

        commit_results = self.db.get_results_for_commit(commit)
        self.assertFalse(commit_results.has_results())

    def test_initialize_commit_records_clears_emails_when_email_is_present(self):
        commit = create_commit()
        self.db.insert_commit(commit)
        self.db.insert_email_for_commit(create_email(), commit)

        self.db.initialize_commit_records(commit)

        self.assertFalse(self.db.email_sent_for_commit(commit))

    def test_initialize_commit_records_does_not_clear_build_records_when_forced_not_to(self):
        commit = create_commit()
        self.db.insert_commit(commit)
        build_id = self.db.insert_build_started_info(commit, datetime.now())
        self.db.insert_build_ended_info(build_id, create_build_info())

        self.db.initialize_commit_records(commit, remove_build_infos=False)

        commit_results = self.db.get_results_for_commit(commit)
        self.assertTrue(commit_results.has_build_info())

    def test_initialize_commit_records_does_not_clear_results_when_forced_not_to(self):
        commit = create_commit()
        self.db.insert_commit(commit)
        test_results = create_test_results(module_name='module', run_tests=1)
        self.db.insert_test_results(test_results, commit)

        self.db.initialize_commit_records(commit, remove_test_results=False)

        commit_results = self.db.get_results_for_commit(commit)
        self.assertTrue(commit_results.has_results())

    def test_initialize_commit_records_does_not_clear_emails_when_forced_not_to(self):
        commit = create_commit()
        self.db.insert_commit(commit)
        self.db.insert_email_for_commit(create_email(), commit)

        self.db.initialize_commit_records(commit, remove_emails=False)

        self.assertTrue(self.db.email_sent_for_commit(commit))

    def test_insert_commit_does_nothing_when_commit_already_exists(self):
        commit = create_commit()
        self.db.insert_commit(commit)
        self.db.insert_commit(commit)
        self.assertEqual(len(self.db.get_results_for_recent_commits(2).results), 1)

    def test_insert_commits_inserts_commits(self):
        commit1 = create_commit()
        commit2 = create_commit()
        commit3 = create_commit()
        commits = [commit1, commit2, commit3]
        self.db.insert_commits(commits)
        self.assertEqual(self.db.get_results_for_recent_commits(3).commits, commits)

    def test_get_commits_count_returns_correct_count(self):
        self.assertEqual(self.db.get_commits_count(), 0)
        self.db.insert_commit(create_commit())
        self.assertEqual(self.db.get_commits_count(), 1)
        self.db.insert_commit(create_commit())
        self.assertEqual(self.db.get_commits_count(), 2)

    def test_insert_build_started_info_returns_correct_id(self):
        commit = create_commit()
        self.db.insert_commit(commit)
        build1_id = self.db.insert_build_started_info(commit, datetime.now())
        self.assertEqual(build1_id, 1)
        build2_id = self.db.insert_build_started_info(commit, datetime.now())
        self.assertEqual(build2_id, 2)

    def test_insert_build_started_info_raises_invalid_commit_error_when_no_such_commit(self):
        commit = create_commit()
        with self.assertRaises(InvalidCommitError):
            self.db.insert_build_started_info(commit, datetime.now())

    def test_insert_build_ended_info_passes_when_build_exists(self):
        commit = create_commit()
        self.db.insert_commit(commit)
        build_id = self.db.insert_build_started_info(commit, datetime.now())
        build_info = create_build_info()
        self.db.insert_build_ended_info(build_id, build_info)

    def test_insert_build_ended_info_raises_invalid_build_error_when_no_such_build(self):
        build_info = create_build_info()
        with self.assertRaises(InvalidBuildError):
            self.db.insert_build_ended_info(1, build_info)

    def test_insert_test_results_raises_invalid_commit_error_when_no_such_commit(self):
        commit = create_commit()
        with self.assertRaises(InvalidCommitError):
            self.db.insert_test_results(create_test_results(), commit)

    def test_insert_email_for_commit_inserts_commit_if_not_already_sent(self):
        commit = create_commit()
        self.db.insert_commit(commit)
        email = create_email()
        self.db.insert_email_for_commit(email, commit)
        self.assertTrue(self.db.email_sent_for_commit(commit))

    def test_insert_email_for_commit_does_nothing_if_email_already_sent(self):
        commit = create_commit()
        self.db.insert_commit(commit)
        email = create_email()
        self.db.insert_email_for_commit(email, commit)
        # This should do nothing, i.e. not raising an error regarding the
        # UNIQUE constraint of commit_id in the emails table.
        self.db.insert_email_for_commit(email, commit)

    def test_insert_email_for_commit_raises_invalid_commit_error_when_no_such_commit(self):
        with self.assertRaises(InvalidCommitError):
            self.db.insert_email_for_commit(create_email(), create_commit())

    def test_email_sent_for_commit_returns_true_if_email_sent(self):
        commit = create_commit()
        self.db.insert_commit(commit)
        self.db.insert_email_for_commit(create_email(), commit)
        self.assertTrue(self.db.email_sent_for_commit(commit))

    def test_email_sent_for_commit_returns_false_if_email_not_sent(self):
        commit = create_commit()
        self.assertFalse(self.db.email_sent_for_commit(commit))

    def test_has_test_run_for_commit_returns_true_if_has_run(self):
        commit = create_commit()
        self.db.insert_commit(commit)
        test_results = create_test_results(module_name='module', case_name='case')
        self.db.insert_test_results(test_results, commit)
        self.assertTrue(self.db.has_test_run_for_commit('module', 'case', commit))

    def test_has_test_run_for_commit_returns_false_if_case_has_not_run_module_name_does_not_match(self):
        commit = create_commit()
        self.db.insert_commit(commit)
        test_results = create_test_results(module_name='module', case_name='case')
        self.db.insert_test_results(test_results, commit)
        self.assertFalse(self.db.has_test_run_for_commit('xxx', 'case', commit))

    def test_has_test_run_for_commit_returns_false_if_case_has_not_run_case_name_does_not_match(self):
        commit = create_commit()
        self.db.insert_commit(commit)
        test_results = create_test_results(module_name='module', case_name='case')
        self.db.insert_test_results(test_results, commit)
        self.assertFalse(self.db.has_test_run_for_commit('module', 'xxx', commit))

    def test_has_test_run_for_commit_returns_false_if_case_has_not_run_commit_does_not_match(self):
        commit1 = create_commit()
        self.db.insert_commit(commit1)
        test_results = create_test_results(module_name='module', case_name='case')
        self.db.insert_test_results(test_results, commit1)
        commit2 = create_commit()
        self.db.insert_commit(commit2)
        self.assertFalse(self.db.has_test_run_for_commit('module', 'case', commit2))

    def test_has_test_run_for_commit_raises_invalid_commit_error_when_no_such_commit(self):
        with self.assertRaises(InvalidCommitError):
            self.assertFalse(self.db.has_test_run_for_commit(
                'module', 'case', create_commit()))

    def test_get_results_for_commit_returns_correct_results_when_there_are_results(self):
        commit = create_commit()
        self.db.insert_commit(commit)
        test_results1 = create_test_results(module_name='module1', run_tests=1)
        self.db.insert_test_results(test_results1, commit)
        test_results2 = create_test_results(module_name='module2', run_tests=3)
        self.db.insert_test_results(test_results2, commit)

        commit_results = self.db.get_results_for_commit(commit)

        self.assertEqual(commit_results.commit, commit)
        self.assertEqual(commit_results.results.run_tests, 4)
        self.assertEqual(commit_results.results.module_names, ['module1', 'module2'])

    def test_get_results_for_commit_returns_correct_results_when_there_are_no_results(self):
        commit = create_commit()
        self.db.insert_commit(commit)

        commit_results = self.db.get_results_for_commit(commit)

        self.assertEqual(commit_results.commit, commit)
        self.assertEqual(commit_results.results.run_tests, 0)
        self.assertEqual(commit_results.results.module_names, [])

    def test_get_results_for_commit_returns_correct_results_when_there_is_no_build_info(self):
        commit = create_commit()
        self.db.insert_commit(commit)

        commit_results = self.db.get_results_for_commit(commit)

        self.assertFalse(commit_results.has_build_info())

    def test_get_results_for_commit_returns_correct_results_when_there_is_build_info(self):
        commit = create_commit()
        self.db.insert_commit(commit)
        START_DATE = datetime.now()
        build_id = self.db.insert_build_started_info(commit, START_DATE)
        LOG = 'build log'
        END_DATE = datetime.now()
        SUCCEEDED = True
        self.db.insert_build_ended_info(
            build_id,
            create_build_info(
                start_date=START_DATE,
                end_date=END_DATE,
                succeeded=SUCCEEDED,
                log=LOG
            )
        )

        commit_results = self.db.get_results_for_commit(commit)

        self.assertTrue(commit_results.has_build_info())
        self.assertEqual(commit_results.build_info.start_date, START_DATE)
        self.assertEqual(commit_results.build_info.end_date, END_DATE)
        self.assertEqual(commit_results.build_info.succeeded, SUCCEEDED)
        self.assertEqual(commit_results.build_info.log, LOG)

    def test_get_results_raises_invalid_commit_error_when_no_such_commit(self):
        commit = create_commit()
        with self.assertRaises(InvalidCommitError):
            self.db.get_results_for_commit(commit)

    def test_get_results_for_recent_commits_returns_empty_list_when_no_commits(self):
        commit_results = self.db.get_results_for_recent_commits()
        self.assertEqual(len(commit_results), 0)

    def test_get_results_for_recent_commits_returns_correct_results_when_more_commits(self):
        commit1 = create_commit()
        self.db.insert_commit(commit1)
        commit2 = create_commit()
        self.db.insert_commit(commit2)
        commit3 = create_commit()
        self.db.insert_commit(commit3)

        COUNT = 2
        commits_results = self.db.get_results_for_recent_commits(COUNT)
        self.assertEqual(len(commits_results), COUNT)
        # Also check that the results are properly sorted, starting from the
        # "oldest" commit.
        self.assertEqual(commits_results[0].commit, commit2)
        self.assertEqual(commits_results[1].commit, commit3)
