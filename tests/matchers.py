"""
    Matchers for tests.
"""

import abc
import re

# Based on https://github.com/s3rvac/retdec-python/blob/master/tests/__init__.py.


class Matcher(metaclass=abc.ABCMeta):
    """A base class of all matchers."""

    @abc.abstractmethod
    def __eq__(self, other):
        raise NotImplementedError

    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        name = self.__class__.__qualname__
        attr_list = ', '.join(
            '{}={!r}'.format(key, value) for key, value in self.__dict__.items()
        )
        return '{}({})'.format(name, attr_list)


class Anything(Matcher):
    """A matcher that matches anything."""

    def __eq__(self, other):
        return True


class AnyStrWith(Matcher):
    """Matches any `str` with a line that matches the given regular
    expression.
    """

    def __init__(self, re):
        self.re = re

    def __eq__(self, str):
        return re.search(self.re, str, re.M)


class AnyFileNamed(Matcher):
    """Matches any `File` with the given name."""

    def __init__(self, name):
        self.name = name

    def __eq__(self, name):
        return self.name == name
