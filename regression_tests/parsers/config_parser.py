"""
    Parsing of configuration files used by RetDec.
"""

import json

from regression_tests.parsers.text_parser import Text
from regression_tests.utils import memoize
from regression_tests.utils.list import NamedObjectList
from regression_tests.utils.list import names_of
from regression_tests.utils.list import names_to_set


def parse(config):
    """Parses the given text representation of a config used by RetDec.
    (`str`).

    :returns: Parsed representation of the config (:class:`Config`).

    :raises ValueError: When the configuration cannot be parsed.
    """
    return Config(config)


class Config(Text):
    """Configuration file used by RetDec.

    Instances of this class behave like strings with additional properties and
    methods.
    """

    def __new__(cls, config):
        """Constructs a new parsed config.

        :param str config: Text representation of the config.
        """
        return Text.__new__(cls, config)

    def __init__(self, config):
        """
        :param str config: Text representation of the config.

        :raises ValueError: When the configuration cannot be parsed.
        """
        self._json = json.loads(config)

    @property
    def json(self):
        """The underlying JSON representation of the config (`json`)."""
        return self._json

    def is_statically_linked(self, func, address=None):
        """Checks that the given function is marked as statically linked.

        :param str func: Name of the function.
        :param int address: Optional address of the function.

        :returns: ``True`` if the function is marked as statically linked,
                  ``False`` otherwise.

        :raises AssertionError: If there is no such function in the config.

        When `address` is not ``None``, it is also checked that the function
        was detected on the given address.
        """
        # Find a function with the given name.
        for config_func in self.json.get('functions', []):
            if config_func['name'] == func:
                break
        else:  # nobreak
            raise AssertionError('no such function: {}'.format(func))

        if config_func['fncType'] != 'staticallyLinked':
            return False

        if address is not None and _string_to_int(config_func.get('startAddr')) != address:
            return False

        return True

    @property
    @memoize
    def vtables(self):
        """Virtual tables (list of :class:`Vtable`).

        The returned list can be indexed by either positions (0, 1, ...) or
        vtable names. Example:

        .. code-block:: python

            module.vtables[0]       # Returns the first vtable.
            module.vtables['vt1']   # Returns the vtable named 'vt1'.

        """
        vtables = NamedObjectList()
        for vt in self.json.get('vtables', []):
            vtables.append(Vtable(vt))
        return vtables

    @property
    @memoize
    def vtable_names(self):
        """Names of the vtables (list of `str`)."""
        return names_of(self.vtables)

    @property
    def vtable_count(self):
        """Number of vtables."""
        return len(self.vtables)

    def has_vtables(self, *names):
        """Are there vtables of the given names?

        Example:

        .. code-block:: python

            module.has_vtables('vt1', 'vt2')

        The order is irrelevant. If you want to check that only the given
        vtable appear in the module and no other vtables, use
        :func:`has_just_vtables()` instead.

        If you call this method without any arguments, it checks whether there
        is at least one vtable in the module:

        .. code-block:: python

            module.has_vtables()
        """
        names = names_to_set(names)
        if not names:
            return self.vtable_count > 0
        return names.issubset(set(self.vtable_names))

    def has_no_vtables(self):
        """Are there no vtables?"""
        return self.vtable_count == 0

    def has_just_vtables(self, *names):
        """Are there only vtables of the given names?

        Example:

        .. code-block:: python

            module.has_just_vtables('vt1', 'vt2')

        The order is irrelevant.
        """
        return set(self.vtable_names) == names_to_set(names)

    def has_vtable(self, name):
        """Is there a vtable with the given name (`str`)?"""
        return name in self.vtable_names

    def has_vtable_on_address(self, address):
        """Is there a vtable with the given address (`int`)?"""
        return self.vtable_on_address(address) is not None

    def vtable_on_address(self, address):
        """Find vtable by address.

        If there is no vtable on the given address, it returns ``None``.
        """
        for vt in self.vtables:
            if vt.address == address:
                return vt
        return None

    @property
    @memoize
    def classes(self):
        """C++ classes (list of :class:`Class`).

        The returned list can be indexed by either positions (0, 1, ...) or
        classes' names. Example:

        .. code-block:: python

            module.classes[0]        # Returns the first class.
            module.classes['class1'] # Returns the class named 'class1'.

        """
        classes = NamedObjectList()
        for c in self.json.get('classes', []):
            classes.append(Class(c))
        return classes

    @property
    @memoize
    def classes_names(self):
        """Names of the classes (list of `str`)."""
        return names_of(self.classes)

    @property
    def classes_count(self):
        """Number of classes."""
        return len(self.classes)


class Vtable:
    """C++ virtual table (vtable) representation."""

    def __init__(self, json):
        self.json = json
        self.name = json.get('name')
        self.address = _string_to_int(json.get('address'))
        self.items = [VtableItem(d) for d in json.get('items', []) or []]

    @property
    def item_count(self):
        """Number of items."""
        return len(self.items)

    @property
    def item_target_names(self):
        """List of target names from all vtable items."""
        names = []
        for i in self.items:
            names.append(i.target_name)
        return names


class VtableItem:
    """C++ virtual table (vtable) item."""

    def __init__(self, json):
        self.json = json
        self.address = _string_to_int(json.get('address'))
        self.target_address = _string_to_int(json.get('targetAddress'))
        self.target_name = json.get('targetName')


class Class:
    """C++ Class."""

    def __init__(self, json):
        self.json = json
        self.name = json.get('name')
        self.constructors = json.get('constructors', [])
        self.destructors = json.get('destructors', [])
        self.methods = json.get('methods', [])
        self.superClasses = json.get('superClasses', [])
        self.virtualMethods = json.get('virtualMethods', [])
        self.virtualTables = json.get('virtualTables', [])


def _string_to_int(val):
    return int(str(val), 0) if val else None
