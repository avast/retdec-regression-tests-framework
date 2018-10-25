"""
    Results for a commit.
"""

import itertools

from regression_tests.retdec_builder import NoBuildInfo
from regression_tests.test_results import NoTestResults
from regression_tests.test_results import TestsResults
from regression_tests.test_results import sort_module_names


class CommitResults:
    """Results for a commit."""

    def __init__(self, commit, results, build_info=NoBuildInfo()):
        """
        :param Commit commit: Tested commit.
        :param TestResults/TestsResults results: Test(s) results for the commit.
        :param BuildInfo build_info: Information about the corresponding build
                                     (if any).
        """
        self._commit = commit
        self._results = results
        self._build_info = build_info

    @property
    def commit(self):
        """Tested commit
        (:class:`~regression_tests.commit_results.CommitResults`).
        """
        return self._commit

    @property
    def results(self):
        """Test(s) results for the commit
        (:class:`~regression_tests.test_results.TestResults` or
        :class:`~regression_tests.test_results.TestsResults`).
        """
        return self._results

    @property
    def build_info(self):
        """Information about the corresponding build, if any
        (:class:`~regression_tests.retdec_builder.BuildInfo`).
        """
        return self._build_info

    @property
    def module_names(self):
        """An ordered list of module names of all the test results.

        Duplicates are not included in the list.
        """
        return self.results.module_names

    def has_results(self):
        """Are there any results?"""
        return self.results.has_run()

    def has_failed_tests(self):
        """Has any of the tests failed?"""
        return self.results.failed

    @property
    def failed_tests(self):
        """Number of failed tests."""
        return self.results.failed_tests

    @property
    def failed_module_names(self):
        """An ordered list of module names in which tests failed.

        Duplicates are not included in the list.
        """
        return self.results.failed_module_names

    def has_build_info(self):
        """Is there a build info?"""
        return self.build_info.has_started()

    def build_has_succeeded(self):
        """Checks if the build has succeeded."""
        return self.build_info.succeeded

    def build_has_failed(self):
        """Checks if the build has failed."""
        return not self.build_info.succeeded


class CommitsResults(list):
    """A list of :class:`.CommitResults` for multiple commits.

    Instances of this class behave like the standard `list` with additional
    methods.
    """

    @property
    def commits(self):
        """A list of commits (:class:`.Commit`)."""
        return [commit_results.commit for commit_results in self]

    @property
    def results(self):
        """A list of results (:class:`.TestsResults`, one for each commit)."""
        return [commit_results.results for commit_results in self]

    @property
    def build_infos(self):
        """A list of build infos (:class:`.BuildInfo`, one for each commit)."""
        return [commit_results.build_info for commit_results in self]

    def has_results(self):
        """Are there any results?"""
        return len(self.results) > 0

    def results_for_module(self, module_name):
        """A list of :class:`.CommitResults` for the given module.
        """
        def get_proper_results(commit_results):
            tests_results = []
            for result in commit_results.results:
                if result.module_name == module_name:
                    tests_results.append(result)
            return CommitResults(
                commit_results.commit,
                TestsResults(tests_results)
            )
        return list(map(get_proper_results, self))

    def results_for_case(self, module_name, case_name):
        """A list of :class:`.CommitResults` for the given case in the given module.
        """
        def get_proper_results(commit_results):
            for result in commit_results.results:
                if result.case_name == case_name:
                    return CommitResults(commit_results.commit, result)
            return CommitResults(
                commit_results.commit,
                NoTestResults(module_name=module_name, case_name=case_name)
            )
        return list(map(get_proper_results, self.results_for_module(module_name)))

    @property
    def module_names(self):
        """An ordered list of module names of all the test results.

        Duplicates are not included in the list.
        """
        return sort_module_names(set(itertools.chain.from_iterable(
            commit_results.module_names for commit_results in self
        )))

    def case_names_for_module(self, module_name):
        """An ordered list of all test case names for the given module.

        Duplicates are not included in the list.
        """
        case_names = []
        for commit_results in self.results_for_module(module_name):
            case_names += commit_results.results.case_names
        return sorted(set(case_names))
