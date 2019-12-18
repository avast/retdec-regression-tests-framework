"""
    Regression tests results.
"""

from datetime import datetime

from regression_tests.test_case import TestCaseName


class TestResults:
    """Results of a single test."""

    # Prevent nosetests from considering this class as a class containing unit
    # tests.
    __test__ = False

    def __init__(self, module_name, case_name, start_date, end_date, run_tests,
                 failed_tests, skipped_tests, output):
        """
        :param str module_name: Name of the module to which the test correspond.
        :param str case_name: Name of the case to which the test correspond.
        :param datetime start_date: Date and time the test started.
        :param datetime end_date: Date and time the test ended.
        :param int run_tests: Total number of tests that were run.
        :param int failed_tests: Number of failed tests.
        :param int skipped_tests: Number of skipped tests.
        :param str output: Output from the tests.
        """
        self._module_name = module_name
        self._case_name = TestCaseName(case_name)
        self._start_date = start_date
        self._end_date = end_date
        self._run_tests = run_tests
        self._failed_tests = failed_tests
        self._skipped_tests = skipped_tests
        self._output = output

    @property
    def module_name(self):
        """Name of the module to which the test correspond (`str`)."""
        return self._module_name

    @property
    def case_name(self):
        """Name of the case to which the test correspond
        (:class:`~regression_tests.test_case.TestCaseName`).
        """
        return self._case_name

    @property
    def start_date(self):
        """Date and time the test started (`datetime`)."""
        return self._start_date

    @property
    def end_date(self):
        """Date and time the test ended (`datetime`)."""
        return self._end_date

    @property
    def run_tests(self):
        """Total number of tests that were run (`int`)."""
        return self._run_tests

    @property
    def failed_tests(self):
        """Number of failed tests (`int`)."""
        return self._failed_tests

    @property
    def output(self):
        """Output from the tests (`str`)."""
        return self._output

    @property
    def full_name(self):
        """Full name."""
        return '{}.{}'.format(self.module_name, self.case_name)

    @property
    def succeeded_tests(self):
        """Number of succeeded tests."""
        return self.run_tests - self.failed_tests

    @property
    def succeeded(self):
        """Have all the tests succeeded?"""
        return self.failed_tests == 0

    @property
    def failed(self):
        """Have some of the tests failed?"""
        return self.failed_tests > 0

    @property
    def skipped_tests(self):
        """Number of skipped tests."""
        return self._skipped_tests

    @property
    def skipped(self):
        """Have some of the tests been skipped?"""
        return self.skipped_tests > 0

    @property
    def runtime(self):
        """Runtime of the test (real time, in seconds).

        If the test has not started or ended, it returns ``None``.
        """
        if self.start_date is None or self.end_date is None:
            return None
        return (self.end_date - self.start_date).total_seconds()

    @property
    def module_names(self):
        """A singleton list with ``self.module_name``.

        This method exists for the compatibility with :class:`.TestsResults`.
        """
        return [self.module_name]

    @property
    def case_names(self):
        """A singleton list with ``self.case_name``.

        This method exists for the compatibility with :class:`.TestsResults`.
        """
        return [self.case_name]

    @property
    def failed_module_names(self):
        """A singleton list with ``self.module_name`` when a test has failed,
        the empty list otherwise.

        This method exists for the compatibility with :class:`.TestsResults`.
        """
        return [self.module_name] if self.failed else []

    def has_run(self):
        """Has at least one test run?"""
        return self.run_tests > 0


class NoTestResults(TestResults):
    """No test results.

    Implements the Null object design pattern.
    """

    # Prevent nosetests from considering this class as a class containing unit
    # tests.
    __test__ = False

    def __init__(self, module_name, case_name):
        super().__init__(
            module_name,
            case_name,
            start_date=datetime.min,
            end_date=datetime.min,
            run_tests=0,
            failed_tests=0,
            skipped_tests=0,
            output='',
        )


class TestsResults(list):
    """Results of multiple tests.

    Instances of this class behave like the standard `list` with additional
    methods.

    >>> tests_results = TestsResults([test_results1, test_results2])
    >>> tests_results == [test_results1, test_results2]
    True
    """

    # Prevent nosetests from considering this class as a class containing unit
    # tests.
    __test__ = False

    @property
    def module_names(self):
        """An ordered list of module names of the test results.

        Duplicates are not included in the list.
        """
        return sort_module_names(set(result.module_name for result in self))

    @property
    def case_names(self):
        """An ordered list of test case names in the test results.

        Duplicates are not included in the list.
        """
        return sorted(set(result.case_name for result in self))

    @property
    def failed_module_names(self):
        """An ordered list of module names in which tests failed.

        Duplicates are not included in the list.
        """
        module_names = set()
        for result in self:
            module_names.update(result.failed_module_names)
        return sort_module_names(module_names)

    @property
    def run_tests(self):
        """Number of run tests."""
        return sum(result.run_tests for result in self)

    @property
    def run_multiple_tests(self):
        """Has more than one test run?"""
        return self.run_tests > 1

    @property
    def failed_tests(self):
        """Number of failed tests."""
        return self.run_tests - self.succeeded_tests

    @property
    def skipped_tests(self):
        """Number of skipped tests."""
        return sum(result.skipped_tests for result in self)

    @property
    def succeeded_tests(self):
        """Number of succeeded tests."""
        return sum(result.succeeded_tests for result in self)

    @property
    def succeeded(self):
        """Have all the tests succeeded?"""
        return self.failed_tests == 0

    @property
    def failed(self):
        """Have some of the tests failed?"""
        return self.failed_tests > 0

    @property
    def skipped(self):
        """Have some of the tests been skipped?"""
        return self.skipped_tests > 0

    @property
    def start_date(self):
        """Start date of the earliest started test.

        If no test has started, it returns ``None``.
        """
        min_start_date = None
        for result in self:
            if (result.start_date is not None and
                    (min_start_date is None or result.start_date < min_start_date)):
                min_start_date = result.start_date
        return min_start_date

    @property
    def end_date(self):
        """End date of the lastly ended test.

        If not all the tests have ended, it returns ``None``.
        """
        max_end_date = None
        for result in self:
            if result.end_date is None:
                return None
            if max_end_date is None or result.end_date > max_end_date:
                max_end_date = result.end_date
        return max_end_date

    @property
    def runtime(self):
        """Runtime of all the tests (real time, in seconds).

        If one of the tests has not started or ended, it returns ``None``.
        """
        runtime = 0
        for result in self:
            if result.runtime is None:
                return None
            runtime += result.runtime
        return runtime

    def has_run(self):
        """Has at least one test run?"""
        return self.run_tests > 0


def sort_module_names(names):
    """Returns a list of the given module names in a sorted order."""
    # We want external and integration tests to appear first. Moreover, we want
    # the current integration tests to appear before older integration tests.
    def sort_key(name):
        if name.startswith('external.'):
            return '0.' + name
        elif name.startswith('integration.current.'):
            return name.replace('integration.current.', '1.integration.0.current.')
        elif name.startswith('integration.'):
            return name.replace('integration.', '1.integration.')
        return name

    return sorted(names, key=sort_key)
