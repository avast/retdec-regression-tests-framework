"""
    A function.
"""

import sys
from functools import partial

from clang import cindex

from regression_tests.parsers.c_parser.exprs.expression import Expression
from regression_tests.parsers.c_parser.exprs.variable import Variable
from regression_tests.parsers.c_parser.stmts.statement import Statement
from regression_tests.parsers.c_parser.types.type import Type
from regression_tests.parsers.c_parser.utils import IdentifiedObjectList
from regression_tests.parsers.c_parser.utils import from_same_file
from regression_tests.parsers.c_parser.utils import get_set_of_names
from regression_tests.parsers.c_parser.utils import remove_whitespace
from regression_tests.parsers.c_parser.utils import underline
from regression_tests.parsers.c_parser.utils import visit_node
from regression_tests.utils import memoize
from regression_tests.utils.list import NamedObjectList
from regression_tests.utils.list import items_to_set
from regression_tests.utils.list import names_of
from regression_tests.utils.list import names_to_set


class Function:
    """A function."""

    def __init__(self, node):
        """
        :param node: Internal node representing the function.
        """
        self._node = node
        self._assignments = []
        self._for_loops = []
        self._while_loops = []
        self._do_while_loops = []
        self._if_stmts = []
        self._var_def_stmts = []
        self._return_stmts = []
        self._empty_stmts = []
        self._switch_stmts = []
        self._goto_stmts = []
        self._labels = []

    @property
    def name(self):
        """Name of the function (`str`)."""
        return self._node.spelling

    @property
    def type(self):
        """Type of the function (:class:`.FunctionType`)."""
        return Type._from_clang_type(self._node.type)

    @property
    def return_type(self):
        """Return type of the function (:class:`.Type`)."""
        return Type._from_clang_type(self._node.result_type)

    @property
    @memoize
    def params(self):
        """Function parameters (list of :class:`.Variable`).

        The returned list can be indexed by either positions (0, 1, ...) or
        names. Example:

        .. code-block:: python

            func.params[0]    # Returns the first parameter.
            func.params['p']  # Returns the parameter named 'p'.

        When there is no such parameter, it raises ``IndexError``.
        """
        params = NamedObjectList()
        for node in self._node.get_arguments():
            params.append(Variable(node))
        return params

    @property
    @memoize
    def param_names(self):
        """Names of the parameters (list of `str`)."""
        return names_of(self.params)

    @property
    def param_count(self):
        """Number of parameters."""
        return len(self.params)

    def has_params(self, *names):
        """Are there parameters of the given names?

        Example:

        .. code-block:: python

            func.has_params('p1', 'p2')

        The order is irrelevant. If you want to check that the function has
        only the given parameters and no other parameters, use
        :func:`has_just_params()` instead.

        If you call this method without any arguments, it checks whether the
        function has at least one parameter:

        .. code-block:: python

            func.has_params()
        """
        names = names_to_set(names)
        if not names:
            return self.param_count > 0
        return names.issubset(set(self.param_names))

    def has_no_params(self):
        """Has the function no parameters?"""
        return self.param_count == 0

    def has_just_params(self, *names):
        """Are there only parameters of the given names?

        Example:

        .. code-block:: python

            func.has_just_params('p1', 'p2')

        The order is irrelevant.
        """
        return set(self.param_names) == names_to_set(names)

    def has_param(self, name):
        """Has the function any parameter named `name`?"""
        for param in self.params:
            if param.name == name:
                return True
        return False

    def calls(self, *functions):
        """Are the given functions called inside the function's body?

        Names as strings or objects of :class:`.Function` can be used.

        Examples:

        .. code-block:: python

            func.calls('other_func')
            func.calls('rand', 'printf')
            func.calls(function1, function2)

        The order is irrelevant. At least one name has to be provided.
        """
        names = get_set_of_names(functions)
        if not names:
            raise AssertionError('at least one function name has to be given')
        return names.issubset(self.called_func_names)

    @property
    @memoize
    def called_func_names(self):
        """A set of names of all called functions.

        If you want to check that the function calls the given functions, use
        :func:`calls()`.
        """
        calls = set()

        def add_to_calls_if_call(node):
            if node.kind == cindex.CursorKind.CALL_EXPR:
                # There may be empty function names in the presence of errors.
                # We do not want to consider these as calls, so ensure that the
                # spelling (= function name) is non-empty.
                if node.spelling:
                    calls.add(self._unify_called_func_name(node.spelling))

        visit_node(self._node, add_to_calls_if_call)

        return calls

    def has_any_for_loops(self):
        """Does the function's body contain any for loops?"""
        return bool(self.for_loops)

    def has_for_loops(self, *for_loops):
        """Are the given for loops inside the function's body?
        Names as strings or objects of :class:`.ForLoop` can be used.

        Examples:

        .. code-block:: python

            func.has_for_loops('for (int x=0; x<10; x++)')
            func.has_for_loops(for_loop1, for_loop2)

        The order is irrelevant. At least one for loop has to be provided.
        """
        return self._search(for_loops, self.for_loops, 'for loop')

    @property
    def for_loops(self):
        """A list of for loops (:class:`.ForLoop`) that the function contains.

        The returned list can be indexed by either positions (0, 1, ...) or
        identification of for loop. Example:

        .. code-block:: python

            # Returns the first for loop:
            function.for_loops[0]
            # Returns the for loop corresponding to the given string:
            function.for_loops['for(int i=0; i<10; i++)']

        When there is no such item, it raises ``IndexError``.
        """
        self._parse_function_body()
        return IdentifiedObjectList(self._for_loops)

    def has_any_while_loops(self):
        """Does the function's body contain any while loops?"""
        return bool(self.while_loops)

    def has_while_loops(self, *while_loops):
        """Are the given while loops inside the function's body?
        Names as strings or objects of :class:`.WhileLoop` can be used.

        Examples:

        .. code-block:: python

            func.has_while_loops('while (1)')
            func.has_while_loops(while_loop1)

        The order is irrelevant. At least one while loop has to be provided.
        """
        return self._search(while_loops, self.while_loops, 'while loop')

    @property
    def while_loops(self):
        """A list of while loops (:class:`.WhileLoop`) that the function contains.

        The returned list can be indexed by either positions (0, 1, ...) or
        identification of while loop. Example:

        .. code-block:: python

            # Returns the first while loop:
            function.while_loops[0]
            # Returns the while loop corresponding to the given string:
            function.while_loops['while(1)']

        When there is no such item, it raises ``IndexError``.
        """
        self._parse_function_body()
        return IdentifiedObjectList(self._while_loops)

    def has_any_do_while_loops(self):
        """Does the function's body contain any do while loops?"""
        return bool(self.do_while_loops)

    def has_do_while_loops(self, *do_while_loops):
        """Are the given do while loops inside the function's body?
        Names as strings or objects of :class:`.DoWhileLoop` can be used.

        Examples:

        .. code-block:: python

            func.has_do_while_loops('do while (1)')
            func.has_do_while_loops(do_while_loop1)

        The order is irrelevant. At least one do while loop has to be provided.
        """
        return self._search(do_while_loops, self.do_while_loops, 'do while loop')

    @property
    def do_while_loops(self):
        """A list of do while loops (:class:`.DoWhileLoop`) that the function contains.

        The returned list can be indexed by either positions (0, 1, ...) or
        identification of do while loop. Example:

        .. code-block:: python

            # Returns the first do while loop:
            function.do_while_loops[0]
            # Returns the while loop corresponding to the given string:
            function.do_while_loops['do while(1)']

        When there is no such item, it raises ``IndexError``.
        """
        self._parse_function_body()
        return IdentifiedObjectList(self._do_while_loops)

    def has_any_assignments(self):
        """Does the function's body contain any assignments?"""
        return bool(self.assignments)

    def has_assignments(self, *assignments):
        """Are the given assignments inside the function's body?
        Names as strings or objects of :class:`.AssignOpExpr`
        and :class:`.CompoundAssignOpExpr` can be used.

        Assignment that are parts of variable definitions are not included.

        Examples:

        .. code-block:: python

            func.has_assignments('a = 3')
            func.has_assignments(assign_op, compound_assign_op)

        The order is irrelevant. At least one assignment has to be provided.
        """
        return self._search(assignments, self.assignments, 'assignment')

    @property
    def assignments(self):
        """A list of assignments (:class:`.AssignOpExpr`,
        :class:`.CompoundAssignOpExpr`) that the function contains.

        The returned list can be indexed by either positions (0, 1, ...) or
        identification of assignment. Example:

        .. code-block:: python

            # Returns the first assignment:
            function.assignments[0]
            # Returns the assignment corresponding to the given string:
            function.assignments['a = 4']

        When there is no such item, it raises ``IndexError``.
        """
        self._parse_function_body()
        return IdentifiedObjectList(self._assignments)

    def has_any_if_stmts(self):
        """Does the function's body contain any if statements?"""
        return bool(self.if_stmts)

    def has_if_stmts(self, *if_stmts):
        """Are the given if statements inside the function's body?
        Names as strings or objects of :class:`.IfStmt` can be used.

        Examples:

        .. code-block:: python

            func.has_if_stmts('if (1)')
            func.has_if_stmts(if_stmt)

        The order is irrelevant. At least one if_stmt has to be provided.
        """
        return self._search(if_stmts, self.if_stmts, 'if stmt')

    @property
    def if_stmts(self):
        """A list of if statements (:class:`.IfStmt`) that the function
        contains.

        The returned list can be indexed by either positions (0, 1, ...) or
        identification of if statement. Example:

        .. code-block:: python

            # Returns the first if statement:
            function.if_stmts[0]
            # Returns the if statement corresponding to the given string:
            function.if_stmts['if(1)']

        When there is no such item, it raises ``IndexError``.
        """
        self._parse_function_body()
        return IdentifiedObjectList(self._if_stmts)

    def has_any_var_def_stmts(self):
        """Does the function's body contain any var definition statements?"""
        return bool(self.var_def_stmts)

    def has_var_def_stmts(self, *var_def_stmts):
        """Are the given variable definition statements inside
        the function's body?
        Names as strings or objects of :class:`.VarDefStmt` can be used.

        Examples:

        .. code-block:: python

            func.has_var_def_stmts('int i = 5')
            func.has_var_def_stmts(var_def_stmt)

        The order is irrelevant. At least one var_def_stmt has to be provided.
        """
        return self._search(var_def_stmts, self.var_def_stmts, 'var def stmt')

    @property
    def var_def_stmts(self):
        """A list of var definition statements (:class:`.VarDefStmt`)
        that the function contains.

        The returned list can be indexed by either positions (0, 1, ...) or
        identification of var definition statement. Example:

        .. code-block:: python

            # Returns the first var definition:
            function.var_def_stmts[0]
            # Returns the var definition corresponding to the given string:
            function.var_def_stmts['int a = 5']

        When there is no such item, it raises ``IndexError``.
        """
        self._parse_function_body()
        return IdentifiedObjectList(self._var_def_stmts)

    def has_any_return_stmts(self):
        """Does the function's body contain any return statements?"""
        return bool(self.return_stmts)

    def has_return_stmts(self, *return_stmts):
        """Are the given return statements inside the function's body?
        Names as strings or objects of :class:`.ReturnStmt` can be used.

        Examples:

        .. code-block:: python

            func.has_return_stmts('return 5')
            func.has_return_stmts(return_stmt)

        The order is irrelevant. At least one return_stmt has to be provided.
        """
        return self._search(return_stmts, self.return_stmts, 'return')

    @property
    def return_stmts(self):
        """A list of return statements (:class:`.ReturnStmt`) that the function
        contains.

        The returned list can be indexed by either positions (0, 1, ...) or
        identification of return statement. Example:

        .. code-block:: python

            # Returns the first return statement:
            function.return_stmts[0]
            # Returns the return statement corresponding to the given string:
            function.return_stmts['return 2']

        When there is no such item, it raises ``IndexError``.
        """
        self._parse_function_body()
        return IdentifiedObjectList(self._return_stmts)

    def has_any_empty_stmts(self):
        """Does the function's body contain any empty statements?"""
        return bool(self.empty_stmts)

    @property
    def empty_stmts(self):
        """A list of empty statements (:class:`.EmptyStmt`) that the function
        contains.
        """
        self._parse_function_body()
        return self._empty_stmts

    def has_any_switch_stmts(self):
        """Does the function's body contain any switch statements?"""
        return bool(self.switch_stmts)

    def has_switch_stmts(self, *switch_stmts):
        """Are the given switch statements inside the function's body?
        Names as strings or objects of :class:`.SwitchStmt` can be used.

        Examples:

        .. code-block:: python

            func.has_switch_stmts('switch (a) { default: break;}')
            func.has_switch_stmts(switch_stmt)

        The order is irrelevant. At least one switch_stmt has to be provided.
        """
        return self._search(switch_stmts, self.switch_stmts, 'switch stmt')

    @property
    def switch_stmts(self):
        """A list of switch statements (:class:`.SwitchStmt`) that the function
        contains.

        The returned list can be indexed by either positions (0, 1, ...) or
        identification of switch statement. Example:

        .. code-block:: python

            # Returns the first switch statement:
            function.switch_stmts[0]
            # Returns the switch statement corresponding to the given string:
            function.switch_stmts['switch(a){case 1}']

        When there is no such item, it raises ``IndexError``.
        """
        self._parse_function_body()
        return IdentifiedObjectList(self._switch_stmts)

    def has_any_goto_stmts(self):
        """Does the function's body contain any goto statements?"""
        return bool(self.goto_stmts)

    def has_goto_stmts(self, *goto_stmts):
        """Are the given goto statements inside the function's body?
        Names as strings or objects of :class:`.GotoStmt` can be used.

        Examples:

        .. code-block:: python

            func.has_goto_stmts('goto label')
            func.has_goto_stmts(goto_stmt)

        The order is irrelevant. At least one goto_stmt has to be provided.
        """
        return self._search(goto_stmts, self.goto_stmts, 'goto stmt')

    @property
    def goto_stmts(self):
        """A list of goto statements (:class:`.GotoStmt`) that the function
        contains.

        The returned list can be indexed by either positions (0, 1, ...) or
        identification of goto statement. Example:

        .. code-block:: python

            # Returns the first goto statement:
            function.goto_stmts[0]
            # Returns the goto statement corresponding to the given string:
            function.goto_stmts['goto xyz']

        When there is no such item, it raises ``IndexError``.
        """
        self._parse_function_body()
        return IdentifiedObjectList(self._goto_stmts)

    def has_any_labels(self):
        """Does the function's body contain any labels?"""
        return bool(self.labels)

    def has_labels(self, *labels):
        """Are the given labels inside the function's body?
        Names as strings or objects of :class:`.Label` can be used.

        Examples:

        .. code-block:: python

            func.has_labels('label')
            func.has_labels(label_obj)

        The order is irrelevant. At least one label has to be provided.
        """
        return self._search(labels, self.labels, 'label')

    @property
    def labels(self):
        """A list of labels (:class:`.Label`) that the function
        contains.

        The returned list can be indexed by either positions (0, 1, ...) or
        identification of label. Example:

        .. code-block:: python

            # Returns the first label:
            function.labels[0]
            # Returns the label corresponding to the given string:
            function.labels['xyz']

        When there is no such item, it raises ``IndexError``.
        """
        self._parse_function_body()
        return IdentifiedObjectList(self._labels)

    def dump(self):
        """Dumps information about the function to ``stdout``.

        The dumped content is same as for :func:`dump_to()`.
        """
        self.dump_to(sys.stdout)

    def dump_to(self, stream):
        """Dumps information about the function to `stream`.

        Contains function prototype and information about body of the function,
        specifically:

        * names of called functions
        * for loops
        * while loops
        * assignments
        * variable definitions
        * if statements
        * return statements
        * switch statements
        * goto statements
        * labels
        * count of empty statements
        """
        s = []
        s.append(str(self))
        s.append('')
        s.append(underline('Called functions:'))
        s.extend(self.called_func_names)
        s.append('')
        s.append(underline('For loops:'))
        s.extend(map(str, self.for_loops))
        s.append('')
        s.append(underline('While loops:'))
        s.extend(map(str, self.while_loops))
        s.append('')
        s.append(underline('Do while loops:'))
        s.extend(map(str, self.do_while_loops))
        s.append('')
        s.append(underline('Assignments:'))
        s.extend(map(str, self.assignments))
        s.append('')
        s.append(underline('Variable definitions:'))
        s.extend(map(str, self.var_def_stmts))
        s.append('')
        s.append(underline('If statements:'))
        s.extend(map(str, self.if_stmts))
        s.append('')
        s.append(underline('Return statements:'))
        s.extend(map(str, self.return_stmts))
        s.append('')
        s.append(underline('Switch statements:'))
        s.extend(map(str, self.switch_stmts))
        s.append('')
        s.append(underline('Goto statements:'))
        s.extend(map(str, self.goto_stmts))
        s.append('')
        s.append(underline('Labels:'))
        s.extend(map(str, self.labels))
        s.append('')
        s.append(underline('Empty statement count:'))
        s.append(str(len(self.empty_stmts)))
        s.append('')

        stream.write('\n'.join(s))

    @memoize
    def _parse_function_body(self):
        def get_statement(node):
            try:
                return Statement._from_clang_node(node)
            except AssertionError:
                return None

        def save_statement(node):
            statement = get_statement(node)
            if statement:
                if statement.is_var_def():
                    self._var_def_stmts.append(statement)
                    if statement.is_assign():
                        self._assignments.append(statement)
                elif statement.is_for_loop():
                    self._for_loops.append(statement)
                elif statement.is_while_loop():
                    self._while_loops.append(statement)
                elif statement.is_do_while_loop():
                    self._do_while_loops.append(statement)
                elif statement.is_if_stmt():
                    self._if_stmts.append(statement)
                elif statement.is_return_stmt():
                    self._return_stmts.append(statement)
                elif statement.is_empty_stmt():
                    self._empty_stmts.append(statement)
                elif statement.is_switch_stmt():
                    self._switch_stmts.append(statement)
                elif statement.is_goto_stmt():
                    self._goto_stmts.append(statement)
            return statement

        def get_children_from_same_file(node):
            same_file_as_node = partial(from_same_file, node)
            children = filter(same_file_as_node, node.get_children())
            return list(children)

        def link_items(items_list):
            if len(items_list) > 1:
                for i, stmt in enumerate(items_list[:-1]):
                    if stmt:
                        stmt.next_stmt = items_list[i + 1]

        def visit_children(parent_node):
            this_level_items = []
            for node in get_children_from_same_file(parent_node):
                item = None
                if node.kind == cindex.CursorKind.LABEL_STMT:
                    item = Label(node)
                    self._labels.append(item)
                elif node.kind == cindex.CursorKind.BINARY_OPERATOR:
                    op = Expression._from_clang_node(node)
                    if op.is_assign_op():
                        self._assignments.append(op)
                elif node.kind == cindex.CursorKind.COMPOUND_ASSIGNMENT_OPERATOR:
                    op = Expression._from_clang_node(node)
                    self._assignments.append(op)
                else:
                    item = save_statement(node)
                this_level_items.append(item)
                visit_children(node)
            link_items(this_level_items)

        # Visit nodes from same file and link the statements together.
        visit_children(self._node)

    @property
    @memoize
    def _params_as_str(self):
        return ', '.join(map(lambda p: p.str_with_type(), self.params))

    def _unify_called_func_name(self, name):
        # We have to unify names of builtins, such as memset(). For example,
        # memset() is sometimes parsed as memset() but sometimes as
        # __builtin___memset_chk(). This makes our regression tests easier to
        # write and read as we can assume that e.g. memset() is always memset()
        # and not __builtin___memset_chk().
        BUILTINS = {
            '__builtin___memset_chk': 'memset',
            '__builtin___memcpy_chk': 'memcpy',
            '__builtin___memmove_chk': 'memmove',
        }
        return BUILTINS.get(name, name)

    def _search(self, items, property, items_name):
        if not items:
            raise AssertionError(
                'at least one {} has to be given'.format(items_name)
            )

        searched_items = items_to_set(items)
        searched_items = map(str, searched_items)
        searched_items = set(map(remove_whitespace, searched_items))
        items = map(str, property)
        items = set(map(remove_whitespace, items))
        return searched_items.issubset(items)

    def __repr__(self):
        return '<{} name={} return_type={} params=[{}]>'.format(
            self.__class__.__name__,
            self.name,
            self.return_type,
            self._params_as_str
        )

    def __str__(self):
        return '{} {}({})'.format(
            self.return_type, self.name, self._params_as_str
        )


from regression_tests.parsers.c_parser.stmts.goto_stmt import Label
