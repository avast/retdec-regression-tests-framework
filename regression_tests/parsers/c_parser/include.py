"""
    An include.
"""

import re


class Include(str):
    """An include."""

    def __new__(cls, include):
        """Constructs an include.

        :param str include: Text of the include (e.g. ``#include <stdio.h>``).

        If there are spaces before/after the include itself, they are removed.
        """
        return str.__new__(cls, include.strip())

    @property
    def file(self):
        """Included file (`str`).

        For example, for ``#include <stdio.h>``, it returns ``"stdio.h"``.
        """
        return re.sub(r'^#include ["<](.+)[">]$', r'\1', self)

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, super().__repr__())
