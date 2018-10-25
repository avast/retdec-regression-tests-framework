"""
    A single regression test case.
"""

import unittest

from regression_tests.test_case_name import TestCaseName
from regression_tests.utils.os import make_dir_name_valid


class TestCase:
    """A single regression test case."""

    # Prevent nosetests from considering this class as a class containing unit
    # tests.
    __test__ = False

    def __init__(self, test_module, test_class, test_settings):
        """
        :param ~regression_tests.test_module.TestModule test_module: Testing
            module.
        :param ~regression_tests.test.Test test_class: Testing class.
        :param ~regression_tests.test_settings.TestSettings: Settings for the
            test.
        """
        self._test_module = test_module
        self._test_class = test_class
        self._test_settings = test_settings

    @property
    def test_module(self):
        """The testing module
        (:class:`~regression_tests.test_module.TestModule`).
        """
        return self._test_module

    @property
    def test_class(self):
        """The testing class (:class:`~regression_tests.test.Test`).
        """
        return self._test_class

    @property
    def test_settings(self):
        """The test settings
        (:class:`~regression_tests.test_settings.TestSettings`).
        """
        return self._test_settings

    @property
    def name(self):
        """Name of the test case (:class:`.TestCaseName`)."""
        return TestCaseName.from_tool_arguments(
            self.test_class.__name__,
            self._tool_arguments
        )

    @property
    def module_name(self):
        """Name of the module in which the test case is located (`str`)."""
        return self.test_module.name

    @property
    def full_name(self):
        """Full name of the test case (`str`), including module name."""
        return '{}.{}'.format(
            self.test_module.name,
            self.name
        )

    @property
    def dir(self):
        """Directory containing the test."""
        return self.test_module.dir

    @property
    def tool(self):
        """Name of the tested tool."""
        return self.test_settings.tool

    @property
    def tool_arguments(self):
        """Tool arguments for the test case."""
        return self._tool_arguments.with_rebased_files(
            inputs_dir=self.test_module.dir,
            outputs_dir=self.tool_dir
        )

    @property
    def tool_dir(self):
        """Directory for the outputs of the tool."""
        outputs_dir = self.test_module.dir.get_dir(
            self.test_settings.outputs_dir_name
        )
        return outputs_dir.get_dir(
            make_dir_name_valid(
                self.name,
                path_to_dir=outputs_dir.path,
                max_nested_file_length=self._max_file_length_in_tool_dir
            )
        )

    @property
    def tool_timeout(self):
        """Timeout for the tool."""
        return self.test_settings.timeout

    def create_test_suite(self, tool):
        """Creates a test suite for the given tool.

        :param Tool tool: The tool for the suite.
        """
        suite = unittest.TestSuite()
        test_names = unittest.defaultTestLoader.getTestCaseNames(
            self.test_class
        )
        for test_name in test_names:
            suite.addTest(
                self.test_class(
                    tool,
                    self.test_settings,
                    methodName=test_name
                )
            )
        return suite

    @property
    def _tool_arguments(self):
        """Tool arguments."""
        return self.test_settings.tool_arguments

    @property
    def _max_file_length_in_tool_dir(self):
        """Maximal length of a file in the tool directory."""
        # We use a heuristic because we cannot foresee what file names may be
        # generated in the future.
        if not self.test_settings.input:
            return 0

        # When the 'input' contains multiple files in a tuple, we have to check
        # all of them. To handle this uniformly, get an iterable of input files
        # and iterate over this iterable. When there is a single input file,
        # this iterable will be a singleton list.
        if isinstance(self.test_settings.input, tuple):
            input_files = self.test_settings.input
        else:
            input_files = [self.test_settings.input]

        max_length = 0
        for input_file in input_files:
            # Reserve sufficient space for suffixes (e.g. "-unpacked" or
            # ".c.backend.bc").
            max_length += len(input_file) + 30
        return max_length
