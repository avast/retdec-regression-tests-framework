"""
    List utilities.
"""

import collections
from abc import abstractmethod


# The implementation of NamedObjectList is based on
# http://petrzemek.net/blog/2014/10/11/indexing-python-lists-with-integer-or-object-name/

class StrPropertyList(list):
    """A base class for lists of objects indexable with an integer or object's
    property specified by ``property_name``.

    It provides support for a list of objects that have a specified attribute
    or property that can be indexed with an integer or the specified object's
    property.

    For an example of a subclass, see :class:`.NamedObjectList`.
    """

    def __getitem__(self, key):
        return self._delegate_to_list('__getitem__', key)

    def __setitem__(self, key, value):
        return self._delegate_to_list('__setitem__', key, value)

    def __delitem__(self, key):
        return self._delegate_to_list('__delitem__', key)

    def _delegate_to_list(self, method, key, *args):
        """Delegates the given indexing method to the list, possibly after
        converting the key into an integral index.
        """
        if isinstance(key, str):
            key = self._index_of(self.modify_key(key))
        return getattr(super(), method)(key, *args)

    def modify_key(self, key):
        """This method can be overridden in subclasses to enable key
        modifications.
        """
        return key

    @property
    @abstractmethod
    def property_name(self):
        """Returns the name of the property to be used when looking up objects
        by `str`.
        """
        raise NotImplementedError

    def _index_of(self, value):
        for index, item in enumerate(self):
            if getattr(item, self.property_name) == value:
                return index
        raise IndexError('no object with {!r} equal to {!r}'.format(
            self.property_name,
            value
        ))


class NamedObjectList(StrPropertyList):
    """A list of objects indexable with an integer or object's name.

    It provides support for a list of objects that have a ``name`` attribute or
    property that can be indexed with an integer or object's name.

    For example, consider a ``Variable`` class with a ``name`` attribute:

    .. code-block:: python

        class Variable:
            def __init__(self, name):
                self.name = name

            # Other useful methods.

            def __str__(self):
                return self.name

    Then, the present class can be used to do the following:

    >>> vars = NamedObjectList([Variable('a'), Variable('b'), Variable('c')])
    >>> print(vars[1])
    b
    >>> print(vars['b'])
    b

    That is, you can index the list with integers or variable names. And, as it
    subclasses the built-in class `list`, it provides all the methods of the
    standard `list` class.
    """

    @property
    def property_name(self):
        return 'name'


def merge_duplicates(seq):
    """Merges duplicates from the given sequence.

    :returns: `seq` without duplicates.

    Items in `seq` have to be hashable. The first occurrences are kept in the
    sequence while any latter occurrences are removed.
    """
    return seq.__class__(collections.OrderedDict.fromkeys(seq))


def move_to_end(item, list):
    """Moves `item` to the end of `list`.

    When `item` is not in `list`, it does nothing.
    """
    if item in list:
        list.remove(item)
        list.append(item)


def as_list(obj):
    """Returns the given object as a list.

    Strings and tuples are treated as single values, even though they are
    sequential.
    """
    if obj is None:
        return []

    if isinstance(obj, collections.abc.Iterable) and \
            not isinstance(obj, str) and \
            not isinstance(obj, tuple):
        return list(obj)
    return [obj]


def names_of(seq):
    """Returns a list of names of objects in the given sequence.

    All objects in `seq` are assumed to have the ``name`` property.
    """
    return [obj.name for obj in seq]


def names_to_set(names):
    """Extracts names from the given sequence of names and returns them in a
    set.

    When `names` is a singleton list containing a sequence of names, the names
    are taken from this nested sequence. Otherwise, when `names` contains
    directly names, `names` is simply converted into a set and returned.
    """
    return items_to_set(names)


def items_to_set(items):
    """Extracts items from the given sequence of items and returns them in a
    set.

    When `items` is a singleton list containing a sequence of items, the items
    are taken from this nested sequence. Otherwise, when `items` contains
    directly items, `items` is simply converted into a set and returned.
    """
    if (len(items) == 1 and
            isinstance(items[0], collections.abc.Iterable) and
            not isinstance(items[0], str)):
        return set(items[0])
    return set(items)
