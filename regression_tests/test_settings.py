"""
    Settings for regression tests.
"""

import copy

from regression_tests.utils.list import as_list
from regression_tests.utils.list import merge_duplicates


class InvalidTestSettingsError(Exception):
    """An exception raised when
    :class:`~regression_tests.test_settings.TestSettings` are invalid.

    An example of invalid test settings may be one without inputs when the tool
    requires it.
    """
    pass


class TestSettings:
    """Settings for regression tests."""

    #: Name of a directory in which outputs should be placed.
    outputs_dir_name = 'outputs'

    # Prevent nosetests from considering this class as a class containing unit
    # tests.
    __test__ = False

    #: A list of all registered test settings classes.
    _registered_test_settings = []

    @classmethod
    def register_test_settings(cls, test_settings_cls):
        """Registers the given test settings class."""
        cls._registered_test_settings.append(test_settings_cls)

    @classmethod
    def _create_test_settings_from_arguments(cls, **kwargs):
        """Instantiates the first test settings that should be created from the
        given arguments.
        """
        for test_settings_cls in cls._registered_test_settings:
            if test_settings_cls.should_be_created_from(**kwargs):
                return test_settings_cls(**kwargs)

        return cls._handle_no_viable_test_settings_to_be_created(**kwargs)

    @classmethod
    def _handle_no_viable_test_settings_to_be_created(cls, **kwargs):
        """Handles the situation when there are not viable test settings to be
        created from the given arguments.
        """
        raise InvalidTestSettingsError(
            ('there are no viable test settings to be created '
             'from the given arguments: {}').format(cls._format_kwargs(kwargs))
        )

    def __new__(cls, **kwargs):
        if cls is TestSettings:
            return cls._create_test_settings_from_arguments(**kwargs)
        return super().__new__(cls)

    def __init__(self, **kwargs):
        """See the description of subclasses for a list of supported
        parameters.
        """
        self._verify_no_arguments_are_left(kwargs)

    @property
    def combinations(self):
        """All single-test-settings combinations that can be created from the
        test settings.

        :returns: A list of :class:`~regression_tests.settings.TestSettings`
            instances.

        For example, when two different input files are specified and all the
        other options are single (i.e. not lists), it returns a list of two
        :class:`~regression_tests.settings.TestSettings` instances, one of them
        having the first input file set and the second one having the second
        input file set.
        """
        combinations = [self.clone()]
        for attr_name in self._supported_attr_names():
            self._extend_cobminations_by_attr(combinations, attr_name)
        return combinations

    def clone(self):
        """Clones the settings.

        :returns: :class:`~regression_tests.settings.TestSettings` that are
            equal to `self` but not identical.
        """
        return copy.deepcopy(self)

    def clone_but(self, **kwargs):
        """Clones the settings but sets different values for the specified
        attributes.

        :returns: :class:`~regression_tests.settings.TestSettings` that are
            equal to `self` up to the specified attributes.

        See the constructor for a list of available attributes.
        """
        clone = self.clone()
        for attr, value in kwargs.items():
            setattr(clone, attr, value)
        return clone

    @classmethod
    def from_settings(cls, base_settings, **kwargs):
        """Creates new test settings by overriding the given base settings.

        Example:

        >>> base_settings = TestSettings(input='file.exe', arch='x86')
        >>> settings = TestSettings.from_settings(base_settings, arch='arm')
        >>> print(settings.input)
        file.exe
        >>> print(settings.arch)
        arm

        The type of the settings returned from this object depends on `cls`,
        i.e. on the class on which this method is called. It can be
        :class:`~regression_tests.settings.TestSettings` or its subclass.
        """
        settings = base_settings.clone_but(**kwargs)
        # We need to ensure that type(settings) == cls.
        return cls(**settings.__dict__)

    def _supported_attr_names(self, without=[]):
        """A list of supported attribute names, possibly without the given
        attribute(s).

        The list is alphabetically ordered.
        """
        attr_names = [attr for attr in self.__dict__ if not attr.startswith('_')]
        # It is VERY important to order the attributes by their name. The
        # reason is that settings combinations are generated based on the order
        # of attributes that this method returns. If the list is not ordered,
        # the list of combinations may differ between interpret instance runs,
        # which causes severe problems on Windows (there, the multiprocessing
        # module uses the 'spawn' method, as opposed to Linux, which uses
        # 'fork'). The reason is that the order in which 'dict' in Python
        # stores the items may differ between interpreter runs. As we use
        # self.__dict__ in the above list comprehension, we have to sort the
        # attributes afterwards.
        attr_names.sort()
        excluded = [without] if isinstance(without, str) else without
        return [attr_name for attr_name in attr_names if attr_name not in excluded]

    def _verify_no_arguments_are_left(self, kwargs):
        """Verifies that there are no arguments in `kwargs`."""
        if kwargs:
            raise InvalidTestSettingsError(
                'unsupported arguments: {}'.format(self._format_kwargs(kwargs))
            )

    def _merge_duplicates(self, setting):
        """Merges duplicates from the given setting."""
        # Duplicates can be removed only from lists. This prevents removal of
        # "duplicates" from strings or tuples.
        if not isinstance(setting, list):
            return setting

        # Do NOT use `if not setting:` because False can be a valid value for
        # some settings.
        if setting is None or setting == []:
            return setting

        no_duplicates = merge_duplicates(as_list(setting))
        return no_duplicates if len(no_duplicates) != 1 else no_duplicates[0]

    def _has_multiple_values_for_attr(self, attr):
        """Checks if the given attribute has multiple values."""
        try:
            return len(getattr(self, attr + '_as_list')) > 1
        except AttributeError:
            # There is no '${attr}_as_list()' method, so the attribute cannot
            # have multiple values.
            return False

    def _extend_cobminations_by_attr(self, combinations, attr_name):
        """Extends `combinations` based on the given attribute."""
        def all_values(settings):
            return getattr(settings, attr_name + '_as_list')

        for settings in copy.copy(combinations):
            if settings._has_multiple_values_for_attr(attr_name):
                combinations.remove(settings)
                for attr in all_values(settings):
                    combinations.append(settings.clone_but(**{attr_name: attr}))

    def _verify_not_empty_list(self, setting, setting_name):
        """Verifies that the given setting is not an empty list."""
        if isinstance(setting, list) and not setting:
            raise InvalidTestSettingsError(
                "'{}' cannot be an empty list".format(setting_name)
            )

    def _verify_has_type(self, setting, setting_name, expected_type):
        """Verifies that the given setting is a value of the expected type."""
        if not isinstance(setting, expected_type):
            raise InvalidTestSettingsError(
                "'{}' has to be {}, not {}".format(
                    setting_name,
                    expected_type.__name__,
                    type(setting).__name__
                )
            )

    @staticmethod
    def _format_kwargs(kwargs):
        """Formats the given arguments so they can be shown to the user."""
        return ', '.join(
            '{}={!r}'.format(key, value) for key, value in kwargs.items()
        )

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        attrs = ''
        for attr_name in self._supported_attr_names():
            attr_value = getattr(self, attr_name)
            if attr_value is not None:
                if attrs:
                    attrs += ', '
                attrs += '{}={!r}'.format(attr_name, attr_value)
        return '{}({})'.format(self.__class__.__name__, attrs)
