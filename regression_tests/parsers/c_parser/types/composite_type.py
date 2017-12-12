"""
    A base class for composite types (``struct``, ``union``).
"""

import re
from abc import abstractmethod

from regression_tests.parsers.c_parser.exprs.variable import Variable
from regression_tests.parsers.c_parser.types.type import Type
from regression_tests.parsers.c_parser.utils import INDENT
from regression_tests.utils import memoize
from regression_tests.utils.list import NamedObjectList
from regression_tests.utils.list import names_of


class CompositeType(Type):
    """A base class for composite types (``struct``, ``union``)."""

    def is_composite_type(self):
        """Returns ``True``."""
        return True

    @property
    @abstractmethod
    def _type_name(self):
        raise NotImplementedError

    @property
    def members(self):
        """Members of the composite type (list of :class:`.Variable`).

        The returned list can be indexed by either positions (0, 1, ...) or
        names. For example, consider the following structure:

        .. code-block:: c

            struct {
                int a;
                int b;
            };

        We may index the list as follows:

        .. code-block:: python

            type.members[0]    # Returns 'a'.
            type.members['b']  # Returns the member named 'b'.

        When there is no such member, it raises ``IndexError``.
        """
        members = NamedObjectList()
        for node in self._type.get_declaration().get_children():
            members.append(Variable(node))
        return members

    @property
    @memoize
    def member_names(self):
        """Names of the members (list of `str`)."""
        return names_of(self.members)

    @property
    def member_count(self):
        """Number of members."""
        return len(self.members)

    def has_any_members(self):
        """Are there any members (at least one)?"""
        return self.member_count > 0

    @property
    def name(self):
        """Name of the composite type (`str`).

        If the composite type has no name, it returns ``None``.
        """
        if not self.has_name():
            return None

        return re.sub(
            r'{} (.*)'.format(self._type_name),
            r'\1',
            self._type.spelling
        )

    def has_name(self):
        """Has the composite type a name?"""
        return not self._type.spelling.startswith(
            '{} (anonymous'.format(self._type_name))

    @property
    def whole_name(self):
        """String representing whole name of this composite type.

        Example: ``struct s``.
        """
        whole_name = self._type_name
        if self.has_name():
            whole_name += ' {}'.format(self.name)
        return whole_name

    def __eq__(self, other):
        return (isinstance(other, CompositeType) and
                type(self) is type(other) and
                self.members == other.members)

    def __hash__(self):
        return hash(self._type_name) + hash(tuple(self.members))

    def __repr__(self):
        return '<{} name={}>'.format(
            self.__class__.__name__,
            self.name
        )

    def __str__(self):
        s = []
        s.append('{} {}'.format(
            self._type_name, self.name + ' {' if self.name else '{'))
        s.extend(map(lambda m: INDENT + m.str_with_type() + ';', self.members))
        s.append('}')
        return '\n'.join(s)
