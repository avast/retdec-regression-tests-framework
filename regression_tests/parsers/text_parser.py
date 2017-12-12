"""
    Parsing of arbitrary text files.
"""

import re


def parse(text):
    """Parses the given text (`str`).

    :returns: Parsed representation of the given text (:class:`Text`).
    """
    return Text(text)


class Text(str):
    """Text.

    Instances of this class behave like strings with additional properties and
    methods.
    """

    def contains(self, regexp):
        """Checks that the given regular expression can be found in the text.

        `regexp` can be either a string or a compiled regular expression.
        ``re.search()`` is used to perform the searching.
        """
        return re.search(regexp, self) is not None
