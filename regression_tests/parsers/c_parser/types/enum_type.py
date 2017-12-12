"""
    A representation of an ``enum``.
"""

import collections

from regression_tests.parsers.c_parser.types.type import Type
from regression_tests.parsers.c_parser.utils import INDENT
from regression_tests.utils import memoize


class EnumType(Type):
    """A representation of an ``enum``."""

    def is_enum(self):
        """Returns ``True``."""
        return True

    @property
    def name(self):
        """Name of the enum (`str`).

        If the enum has no name, it returns ``None``.
        """
        name = self._node.spelling
        return name if (name != '') else None

    def has_name(self):
        """Has the enum a name?"""
        return bool(self.name)

    @property
    @memoize
    def items(self):
        """Constants declared in the enum and their values (`dict`)."""
        return collections.OrderedDict(
            (node.spelling, node.enum_value) for node in self._node.get_children()
        )

    @property
    @memoize
    def item_names(self):
        """Names of constants declared in the enum (`list`)."""
        return list(self.items.keys())

    @property
    def item_count(self):
        """Count of items of the enum."""
        return len(self.items)

    def is_empty(self):
        """Is the enum empty?"""
        return self.item_count == 0

    def __eq__(self, other):
        return (isinstance(other, EnumType) and
                self.items == other.items)

    def __hash__(self):
        return hash(id(self))

    def __repr__(self):
        return '<{} name={}>'.format(
            self.__class__.__name__,
            self.name,
        )

    def __str__(self):
        s = []
        s.append('enum {}'.format(self.name + ' {' if self.name else '{'))
        s.append(',\n'.join(map(lambda i: '{}{}'.format(INDENT, i), self.items)))
        s.append('}')
        return '\n'.join(s)
