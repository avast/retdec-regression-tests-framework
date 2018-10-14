"""
    A module containing regression tests.
"""

import importlib
import inspect
import os
import re

from regression_tests.test import Test
from regression_tests.test_case import TestCase
from regression_tests.utils import copy_class


class TestModule:
    """A module containing regression tests."""

    # Prevent nosetests from considering this class as a class containing unit
    # tests.
    __test__ = False

    def __init__(self, file, root_dir):
        """
        :param File file: The module (a ``.py`` file).
        :param Directory root_dir: The root directory containing all
                                   the tests.
        """
        self._file = file
        self._root_dir = root_dir

    @property
    def file(self):
        """The file representing the module
        (:class:`~regression_tests.filesystem.file.File`).
        """
        return self._file

    @property
    def root_dir(self):
        """The root directory containing all the tests
        (:class:`~regression_tests.filesystem.directory.Directory`).
        """
        return self._root_dir

    @property
    def dir(self):
        """Directory containing the module."""
        return self.file.dir

    @property
    def name(self):
        """Name of the module.

        For example, if the module path is ``'/root_dir/dir/subdir/test.py'``
        and the root directory is ``'/root_dir'``, it returns ``'dir.subdir'``.
        """
        rel_module_path = os.path.relpath(
            os.path.splitext(self.file.path)[0],
            self.root_dir.path
        )
        return re.sub(r'\.?[^.]*$', '', rel_module_path.replace(os.path.sep, '.'))

    def test_cases(self, only_for_tool=None, only_matching=None):
        """A list of test cases in the module.

        :param str only_for_tool: When given, include only tests for the given
                                  tool.
        :param str only_matching: When given, include only tests matching the
                                  given regular expression.

        :returns: A list of :class:`.TestCase` instances contained in the module.
        """
        test_cases = []
        for test_class in self._test_classes:
            for test_settings in test_class.settings_combinations(only_for_tool):
                test_case = self._test_case_for(test_class, test_settings)
                if self._should_be_included(test_case, only_matching):
                    test_cases.append(test_case)
        return test_cases

    def _load(self):
        """Loads the module and returns it."""
        # Warning: If a module with the same name has already been loaded, it
        #          uses that module instead of loading the new one.
        loader = importlib.machinery.SourceFileLoader(self.name, self.file.path)
        return loader.load_module()

    @property
    def _test_classes(self):
        """A list of test classes in the module."""
        def is_regression_test_class(obj):
            # Do not consider the Test class as a test class (we only want its
            # subclasses).
            return (
                inspect.isclass(obj) and
                issubclass(obj, Test) and
                obj is not Test
            )

        loaded_module = self._load()
        return [cls for name, cls in inspect.getmembers(
            loaded_module, is_regression_test_class)]

    def _test_case_for(self, test_class, test_settings):
        """Returns a test case for the given class and settings."""
        # We have to update the base class of the test class, depending on the
        # tool that is being tested. For example, if the tested tool is the
        # decompiler, we use DecompilerTest as the base class. The reason is
        # that the default base class, Test, is pretty abstract. In this way,
        # proper attributes and methods are provided to users (e.g.
        # self.decompiler will be available in DecompilerTest, but not in a
        # general ToolTest).

        # We have to copy the test class because a single test may contain
        # settings for different tools. If we did not copy it, a change to a
        # class with one of the settings would also affect the same class with
        # different settings.
        test_class = copy_class(test_class)

        # Instead of changing Test to a proper tool-test class, we make the
        # appropriate tool-test class the first base class of the test class.
        # The reason is that it would be very hard to change the base class
        # because the test class may inherit from another class, which then
        # inherits from Test. Putting the appropriate class as the first base
        # class represents a much simpler solution.
        test_class.__bases__ = (test_settings.tool_test_class,) +\
            test_class.__bases__

        return TestCase(self, test_class, test_settings)

    def _should_be_included(self, test_case, only_matching):
        """Should the given test case be included into the list of test cases?
        """
        if only_matching is not None:
            return self._matches(test_case, regexp=only_matching)
        return True

    def _matches(self, test_case, regexp):
        """Checks if the given test case matches the given regular expression."""
        # Use re.search() instead of re.match() so that the user does not have
        # to type the complete regular expression, just a part of it.
        return re.search(regexp, test_case.full_name)
