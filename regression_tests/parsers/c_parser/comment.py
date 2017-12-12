"""
    A comment.
"""

import re


class Comment(str):
    """A comment."""

    def matches(self, regexp):
        """Matches the comment the given regular expression?

        `regexp` can be either a string or a compiled regular expression. The
        standard function ``re.fullmatch()`` is used to perform the matching,
        so include ``'.*'`` before and after the regular expression to match
        the leading ``'//'`` or ``'/*'`` and the ending ``'*/'``.
        """
        return re.fullmatch(regexp, self) is not None

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, super().__repr__())
