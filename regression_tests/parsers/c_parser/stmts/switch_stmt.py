"""
    A representation of a ``switch`` statement.
"""

from clang import cindex

from regression_tests.parsers.c_parser.exprs.expression import Expression
from regression_tests.parsers.c_parser.stmts.statement import Statement
from regression_tests.parsers.c_parser.utils import INDENT
from regression_tests.parsers.c_parser.utils import first_child_node
from regression_tests.parsers.c_parser.utils import nth_item
from regression_tests.utils import memoize


class SwitchStmt(Statement):
    """A representation of a ``switch`` statement."""

    def __init__(self, node):
        """
        :param node: Internal node representing the switch.
        """
        super().__init__(node)
        self._cases = []
        self._default_case = None

    def is_switch_stmt(self):
        """Returns ``True``."""
        return True

    def has_cases(self):
        """Does the switch contain some cases?"""
        return bool(self.cases)

    @property
    @memoize
    def switch_expr(self):
        """Expression directing the switch."""
        node = first_child_node(self._node)
        while node.kind == cindex.CursorKind.UNEXPOSED_EXPR:
            node = first_child_node(node)
        return node.spelling

    @property
    def cases(self):
        """A list of cases (:class:`.Case`) that the switch contains.

        Default case is not included.
        """
        self._parse_switch_body()
        return self._cases

    def has_default_case(self):
        """Does the switch contain default case?"""
        return bool(self.default_case)

    @property
    def default_case(self):
        """Default case (:class:`.DefaultCase`) that the switch contains or
        ``None``.
        """
        self._parse_switch_body()
        return self._default_case

    @memoize
    def _parse_switch_body(self):
        body_node = nth_item(1, self._node.get_children())
        for child in body_node.get_children():
            if child.kind == cindex.CursorKind.CASE_STMT:
                self._cases.append(Case(child))
            elif child.kind == cindex.CursorKind.DEFAULT_STMT:
                self._default_case = DefaultCase(child)

    def __eq__(self, other):
        return id(self) == id(other)

    def __hash__(self):
        return hash(id(self))

    def __repr__(self):
        return '<{} switch_expr={} cases={} has_default_case={}>'.format(
            self.__class__.__name__,
            self.switch_expr,
            len(self.cases),
            self.has_default_case()
        )

    def __str__(self):
        s = []
        s.append('switch({}) '.format(self.switch_expr) + '{')
        s.extend(map(lambda c: INDENT + str(c), self.cases))
        if self.has_default_case():
            s.append(INDENT + 'default')
        s.append('}')
        return '\n'.join(s)


class Case:
    """A representation of a ``case``."""

    def __init__(self, node):
        """
        :param node: Internal node representing the case.
        """
        self._node = node

    @property
    @memoize
    def condition(self):
        """Condition of the case (:class:`.Expression`)."""
        cond = first_child_node(self._node)
        return Expression._from_clang_node(cond)

    def __repr__(self):
        return '<{}>'.format(self.__class__.__name__)

    def __str__(self):
        return 'case {}'.format(self.condition)


class DefaultCase:
    """A representation of a ``default`` case."""

    def __init__(self, node):
        """
        :param node: Internal node representing the default case.
        """
        self._node = node

    def __eq__(self, other):
        return id(self) == id(other)

    def __repr__(self):
        return '<{}>'.format(self.__class__.__name__)

    def __str__(self):
        return 'default'
