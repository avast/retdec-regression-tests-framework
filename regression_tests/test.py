"""
    A base class for all regression tests.
"""

import inspect
import unittest

from regression_tests.test_settings import TestSettings


class Test(unittest.TestCase):
    """A base class for all regression tests."""

    # Prevent nosetests from considering this class as a class containing unit
    # tests.
    __test__ = False

    # Do not limit diffs in the output from asserts. The name is in camelCase
    # because it is an attribute of unittest.TestCase.
    maxDiff = None

    def __init__(self, settings, **kwargs):
        """
        :param ~regression_tests.test_settings.TestSettings settings: The
            settings of the test.

        All the other arguments are passed directly into the
        ``unittest.TestCase``'s constructor.

        All the values in `settings` have to be single values, not lists. The
        reason is that `settings` correspond to the single settings for the
        actual test that is being run.
        """
        self._store_settings(settings)
        super().__init__(**kwargs)

    @property
    def settings(self):
        """The settings of the test."""
        return self.__dict__['settings']

    @classmethod
    def settings_combinations(cls, only_critical=False, only_for_tool=None):
        """Returns all single-test-settings combinations that can be created
        from all the specified test settings.

        :param bool only_critical: Include only critical settings.
        :param str only_for_tool: When given, include only tests for the given
                                  tool.

        :returns: A list of
            :class:`~regression_tests.test_settings.TestSettings` instances.

        For example, when two different settings are specified in the class
        (e.g. ``settings1`` and ``settings2``), where each setting yields two
        combinations (see the description of
        :func:`~regression_tests.test_settings.TestSettings.combinations()`),
        this function returns a list of four
        :class:`~regression_tests.test_settings.TestSettings` instances.

        Critical settings are settings that are instances of
        :class:`~regression_tests.test_settings.CriticalTestSettings`.
        Instances of just :class:`~regression_tests.test_settings.TestSettings`
        are not considered to be critical settings.

        When `only_critical` is ``False`` (the default), critical settings are
        considered to be normal settings, and are included in the combinations.
        """
        def are_settings_to_consider(attr):
            if not isinstance(attr, TestSettings):
                return False

            if (only_for_tool is not None and hasattr(attr, 'tool') and
                    attr.tool != only_for_tool):
                return False

            if not only_critical:
                return True
            return attr.critical

        combinations = []
        for _, settings in inspect.getmembers(cls, are_settings_to_consider):
            combinations.extend(settings.combinations)
        return combinations

    def _store_settings(self, settings):
        """Stores the given settings."""
        # We need to store the settings into the object's dictionary to
        # override the use of the class variable when it is also named
        # 'settings'. Consider the following test:
        #
        #     class SomeTest(Test):
        #         settings = TestSettings(  # Store into SomeTest.settings.
        #             arch=['x86', 'arm']
        #         )
        #
        #         def test_something(self):
        #             print(self.settings)
        #
        # If we didn't override SomeTest.settings, the above test would print
        #
        #     ['x86', 'arm']
        #
        # When we override it, the test correctly prints a single architecture.
        self.__dict__['settings'] = settings
