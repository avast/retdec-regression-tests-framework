"""
    A representation of a ``for`` loop.
"""

import itertools
import re

from regression_tests.parsers.c_parser.stmts.loop import Loop
from regression_tests.utils import memoize


class ForLoop(Loop):
    """A representation of a ``for`` loop."""

    def is_for_loop(self):
        """Returns ``True``."""
        return True

    @property
    @memoize
    def header(self):
        """Textual representation of the header of the loop.

        For example, the header of the following loop is ``'int i = 0; i < 10;
        ++i'``.

        .. code-block:: c

            for (int i = 0; i < 10; ++i) {
                printf("Hello %d", i);
            }

        Note that the whitespace may not 100% correspond to the original loop
        (the header is reconstructed from tokens).
        """
        parts = self._node.get_children()
        decl = next(parts)
        cond = next(parts)
        step = next(parts)

        decl_tokens = self._tokens_until(decl.get_tokens(), ';')
        cond_tokens = self._tokens_until(cond.get_tokens(), ';')
        step_tokens = list(step.get_tokens())[:-1]  # All but ending ')'.

        return '{}; {}; {}'.format(
            self._join_tokens(decl_tokens),
            self._join_tokens(cond_tokens),
            self._join_tokens(step_tokens)
        )

    def _tokens_until(self, tokens, sentinel):
        return list(itertools.takewhile(
            lambda t: t.spelling != sentinel,
            tokens
        ))

    def _join_tokens(self, tokens):
        joined = ' '.join(t.spelling for t in tokens)

        # "++ id" -> "++id"
        joined = re.sub(r'\+\+ ', '++', joined)

        # "id ++" -> "id++"
        joined = re.sub(r' \+\+', '++', joined)

        # "-- id" -> "--id"
        joined = re.sub(r'-- ', '--', joined)

        # "id --" -> "id--"
        joined = re.sub(r' --', '--', joined)

        # "( )" -> "()"
        joined = re.sub(r'\( \)', '()', joined)

        # "func ()" -> "func()"
        joined = re.sub(r'(\w) \(', r'\1(', joined)

        return joined

    def __repr__(self):
        return '<{} header=({})>'.format(self.__class__.__name__, self.header)

    def __str__(self):
        return 'for ({})'.format(self.header)
