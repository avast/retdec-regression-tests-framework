"""
    A module (translation unit).
"""

import io
import re
import sys

from clang import cindex

from regression_tests.parsers.c_parser.comment import Comment
from regression_tests.parsers.c_parser.include import Include
from regression_tests.parsers.c_parser.types.enum_type import EnumType
from regression_tests.parsers.c_parser.types.struct_type import StructType
from regression_tests.parsers.c_parser.types.union_type import UnionType
from regression_tests.parsers.c_parser.utils import get_name
from regression_tests.parsers.c_parser.utils import get_parse_errors
from regression_tests.parsers.c_parser.utils import get_set_of_names
from regression_tests.parsers.c_parser.utils import has_tokens
from regression_tests.parsers.c_parser.utils import underline
from regression_tests.parsers.c_parser.utils import visit_node
from regression_tests.parsers.text_parser import Text
from regression_tests.utils import memoize
from regression_tests.utils.list import NamedObjectList
from regression_tests.utils.list import names_of


class Module(Text):
    """A module (translation unit).

    The instances of this class behave like strings with additional properties
    and methods.
    """

    def __new__(cls, code, tu):
        """Constructs a new parsed C code.

        :param str code: The original C code.
        :param clang.TranslationUnit tu: The underlying translation unit.
        """
        c_code = Text.__new__(cls, code)
        return c_code

    def __init__(self, code, tu):
        """
        :param str code: The original C code.
        :param clang.TranslationUnit tu: The underlying translation unit.
        """
        self._code = code
        self._tu = tu

    @property
    def code(self):
        """The original C code (`str`)."""
        return self._code

    @property
    def file_name(self):
        """Name of the original source file (`str`)."""
        return self._tu.spelling

    def has_parse_errors(self):
        """Does the module contain some parsing errors?"""
        parse_errors = get_parse_errors(self._tu.diagnostics)
        return bool(parse_errors)

    @property
    @memoize
    def global_vars(self):
        """Global variables (list of :class:`.Variable`).

        The returned list can be indexed by either positions (0, 1, ...) or
        names. Example:

        .. code-block:: python

            module.global_vars[0]    # Returns the first global variable.
            module.global_vars['g']  # Returns the global variable named 'g'.

        When there is no such global variable, it raises ``IndexError``.
        """
        var_nodes = filter(self._is_global_var, self._tu.cursor.get_children())
        return NamedObjectList(map(Variable, var_nodes))

    @property
    @memoize
    def global_var_names(self):
        """Names of the global variables (list of `str`)."""
        return names_of(self.global_vars)

    @property
    def global_var_count(self):
        """Number of global variables."""
        return len(self.global_vars)

    def has_any_global_vars(self):
        """Are there any global variables (at least one)?"""
        return self.global_var_count > 0

    def has_global_vars(self, *vars):
        """Are there given global variables?

        :param vars: Variable names or instances of :class:`.Variable`.

        Example:

        .. code-block:: python

            module.has_global_vars('g1', 'g2')
            module.has_global_vars('g1', var1)

        The order is irrelevant. If you want to check that only the given
        global variables appear in the module and no other other global
        variables are present, use :func:`has_global_vars()` instead.

        If you call this method without any arguments, it checks whether there
        is at least one global variable in the module:

        .. code-block:: python

            module.has_global_vars()
        """
        names = get_set_of_names(vars)
        if not names:
            return self.global_var_count > 0
        return names.issubset(set(self.global_var_names))

    def has_no_global_vars(self):
        """Are there no global variables?"""
        return self.global_var_count == 0

    def has_just_global_vars(self, *vars):
        """Are there only specified global variables?

        :param vars: Variable names or instances of :class:`.Variable`.

        Example:

        .. code-block:: python

            module.has_just_global_vars('g1', 'g2')
            module.has_just_global_vars('g', var)

        The order is irrelevant.
        """
        return set(self.global_var_names) == get_set_of_names(vars)

    def has_global_var(self, var):
        """Is there specified global variable?

        :param var: Variable name or instance of :class:`.Variable`.
        """
        return get_name(var) in self.global_var_names

    @property
    @memoize
    def funcs(self):
        """Functions (list of :class:`.Function`).

        The returned list can be indexed by either positions (0, 1, ...) or
        function names. Example:

        .. code-block:: python

            module.funcs[0]       # Returns the first function.
            module.funcs['main']  # Returns the function named 'main'.

        When there is no such function, it raises ``IndexError``.
        """
        func_nodes = filter(self._is_func, self._tu.cursor.get_children())
        return NamedObjectList(map(Function, func_nodes))

    @property
    @memoize
    def func_names(self):
        """Names of the functions (list of `str`)."""
        return names_of(self.funcs)

    @property
    def func_count(self):
        """Number of functions."""
        return len(self.funcs)

    def func(self, *functions):
        """Returns the first function corresponding to an item in `functions`.

        Names as strings or objects of :class:`.Function` can be used as parameters.

        This is useful because on x86 + PE, functions may be prefixed with
        ``_``. Instead of using an if/else (ELF vs PE), you can simply obtain
        the function in the following way:

        .. code-block:: python

            my_func = module.func('my_func', '_my_func')
            my_func = module.func(foo, '_foo')

        When there is no such function, it raises ``AssertionError``.
        """
        if not functions:
            raise AssertionError('at least one function name has to be given')

        for name in map(get_name, functions):
            for func in self.funcs:
                if func.name == name:
                    return func

        raise AssertionError('no such function')

    def has_funcs(self, *functions):
        """Are there given functions?

        :param functions: Function names or instances of :class:`.Function`.

        Example:

        .. code-block:: python

            module.has_funcs('func1', 'func2')
            module.has_funcs('func1', foo)

        The order is irrelevant. If you want to check that only the given
        functions appear in the module and no other functions, use
        :func:`has_just_funcs()` instead.

        If you call this method without any arguments, it checks whether there
        is at least one function in the module:

        .. code-block:: python

            module.has_funcs()
        """
        names = get_set_of_names(functions)
        if not names:
            return self.func_count > 0
        return names.issubset(set(self.func_names))

    def has_no_funcs(self):
        """Are there no functions?"""
        return self.func_count == 0

    def has_just_funcs(self, *functions):
        """Are there only given functions?
        Names as strings or objects of :class:`.Function` can be used as parameters.

        Example:

        .. code-block:: python

            module.has_just_funcs('func1', 'func2')
            module.has_just_funcs('func1', foo)

        The order is irrelevant.
        """
        return set(self.func_names) == get_set_of_names(functions)

    def has_func(self, name):
        """Is there a function with the given name (`str`)?"""
        return name in self.func_names

    def has_func_matching(self, regexp):
        """Is there a function with a name matching the given regular
        expression?

        `regexp` can be either a string or a compiled regular expression. The
        standard function ``re.fullmatch()`` is used to perform the matching.
        """
        for name in self.func_names:
            if re.fullmatch(regexp, name) is not None:
                return True
        return False

    @property
    @memoize
    def comments(self):
        """Comments in the code (list of :class:`.Comment`)."""
        comments = []
        for token in self._tu.cursor.get_tokens():
            if token.kind == cindex.TokenKind.COMMENT:
                comments.append(Comment(token.spelling))
        return comments

    def has_comment_matching(self, regexp):
        """Is there a comment matching the given regular expression?

        See the description of
        :func:`~regression_tests.parsers.c_parser.comment.Comment.matches()`
        for more info.
        """
        for comment in self.comments:
            if comment.matches(regexp):
                return True
        return False

    @property
    @memoize
    def includes(self):
        """Includes in the code (list of :class:`.Include`).

        Only direct includes are considered (i.e. nested includes are
        discarded).
        """
        # We have to iterate through the tokens because
        #
        # (1) includes are not available through self._tu.cursor.get_children(),
        #
        # (2) file inclusions from self._tu.get_includes() have just
        #     absolute paths to the included files.
        includes = []
        tokens = list(self._tu.cursor.get_tokens())
        i = 0
        while i < len(tokens):
            include, i = self._try_read_next_include(tokens, i)
            if include is not None:
                includes.append(include)
        return includes

    def has_include_of_file(self, file):
        """Is there an include of the given file (`str`)?"""
        for include in self.includes:
            if include.file == file:
                return True
        return False

    @property
    @memoize
    def string_literal_values(self):
        """Returns a set of values of all string literals (a set of `str`)."""
        values = set()

        def add_to_values_if_string_literal(node):
            if node.kind != cindex.CursorKind.STRING_LITERAL:
                return

            # There seems to be a bug in clang (cindex) that causes NAN,
            # which expands to __builtin_nanf, to be considered a string
            # literal with no tokens. As a workaround, do not consider
            # nodes without tokens to be valid string literals.
            if not has_tokens(node):
                return

            values.add(StringLiteral(node).value)

        # We have to visit all the global variables and functions.
        for node in self._tu.cursor.get_children():
            if self._is_func(node) or self._is_global_var(node):
                visit_node(node, add_to_values_if_string_literal)

        return values

    def has_string_literal(self, value):
        """Is there a string literal of the given value?

        It searches through the whole module (global variables and function
        bodies).

        Example:

        .. code-block:: python

            module.has_string_literal('Result is: %d')

        When the literal is not found in :attr:`string_literal_values`,
        :func:`~regression_tests.parsers.text_parser.Text.contains()`
        is called to check whether the literal exists in the
        module. This behavior is needed because there may be a syntax error
        near the string literal. In such cases, the literal is not present in
        the module because the code that contains it is skipped during parsing.
        """
        if value in self.string_literal_values:
            return True

        return self.contains('"{}"'.format(re.escape(value)))

    def has_string_literal_matching(self, regexp):
        """Is there a string literal matching the given regular expression?

        `regexp` can be either a string or a compiled regular expression.
        The standard function ``re.fullmatch()`` is used to perform the matching.

        When the literal is not found in :attr:`string_literal_values`,
        :func:`~regression_tests.parsers.text_parser.Text.contains()`
        is called to check whether a matching literal exists
        in the module. See the description of :func:`has_string_literal()` for
        the reason.
        """
        if self._has_string_literal_value_matching(regexp):
            return True

        return self._contains_string_literal_matching(regexp)

    @property
    @memoize
    def structs(self):
        """Structures (list of :class:`.StructType`).

        The returned type is plain list, not
        :class:`~regression_tests.utils.list.NamedObjectList`.
        """
        struct_nodes = filter(self._is_struct, self._tu.cursor.get_children())
        return [StructType(node.type) for node in struct_nodes]

    @property
    @memoize
    def unnamed_structs(self):
        """Unnamed structures (list of :class:`.StructType`).

        The returned type is plain list, not
        :class:`~regression_tests.utils.list.NamedObjectList`.
        """
        return [struct for struct in self.structs if not struct.has_name()]

    @property
    @memoize
    def named_structs(self):
        """Named structures (list of :class:`.StructType`).

        The returned list can be indexed by either positions (0, 1, ...) or
        structure names. Example:

        .. code-block:: python

            module.named_structs[0]      # Returns the first structure.
            module.named_structs['node'] # Returns the structure named 'node'.

        When there is no such structure, it raises ``IndexError``.
        """
        return NamedObjectList([x for x in self.structs if x.has_name()])

    @property
    @memoize
    def struct_names(self):
        """Names of the structures (list of `str`)."""
        return names_of(self.named_structs)

    @property
    def struct_count(self):
        """Number of structures."""
        return len(self.structs)

    @property
    def unnamed_struct_count(self):
        """Number of unnamed structures."""
        return len(self.unnamed_structs)

    @property
    def named_struct_count(self):
        """Number of named structures."""
        return len(self.named_structs)

    def has_any_structs(self):
        """Are there any structures (at least one)?"""
        return self.struct_count > 0

    def has_any_unnamed_structs(self):
        """Are there any unnamed structures (at least one)?"""
        return self.unnamed_struct_count > 0

    def has_any_named_structs(self):
        """Are there any named structures (at least one)?"""
        return self.named_struct_count > 0

    def has_named_structs(self, *structs):
        """Are there given named structures?

        :param structs: Structure names or instances of :class:`.StructType`.

        Example:

        .. code-block:: python

            module.has_named_structs('s1', 's2')
            module.has_named_structs('s1', struct)

        The order is irrelevant. If you want to check that only the given
        named structures appear in the module and no other named structures
        are present, use :func:`has_just_named_structs()` instead.

        If you call this method without any arguments, it checks whether there
        is at least one struct in the module:

        .. code-block:: python

            module.has_named_structs()
        """
        names = get_set_of_names(structs)
        if not names:
            return self.has_any_named_structs()
        return names.issubset(set(self.struct_names))

    def has_no_structs(self):
        """Are there no structures?"""
        return self.struct_count == 0

    def has_no_unnamed_structs(self):
        """Are there no unnamed structures?"""
        return self.unnamed_struct_count == 0

    def has_no_named_structs(self):
        """Are there no named structures?"""
        return self.named_struct_count == 0

    def has_just_named_structs(self, *structs):
        """Are there only given named structures?

        :param structs: Structure names or instances of :class:`.StructType`.

        Example:

        .. code-block:: python

            module.has_just_named_structs('s1', 's2')
            module.has_just_named_structs('s1', struct)

        The order is irrelevant.
        """
        return set(self.struct_names) == get_set_of_names(structs)

    def has_named_struct(self, struct):
        """Is there specified named structure?

        :param struct: Structure name or instance of :class:`.StructType`.
        """
        return get_name(struct) in self.struct_names

    @property
    @memoize
    def unions(self):
        """Unions (list of :class:`.UnionType`).

        The returned type is plain list, not
        :class:`~regression_tests.utils.list.NamedObjectList`.
        """
        union_nodes = filter(self._is_union, self._tu.cursor.get_children())
        return [UnionType(node.type) for node in union_nodes]

    @property
    @memoize
    def unnamed_unions(self):
        """Unnamed unions (list of :class:`.UnionType`).

        The returned type is plain list, not
        :class:`~regression_tests.utils.list.NamedObjectList`.
        """
        return [union for union in self.unions if not union.has_name()]

    @property
    @memoize
    def named_unions(self):
        """Named unions (list of :class:`.UnionType`).

        The returned list can be indexed by either positions (0, 1, ...) or
        union names. Example:

        .. code-block:: python

            module.named_unions[0]      # Returns the first union.
            module.named_unions['node'] # Returns the union named 'node'.

        When there is no such union, it raises ``IndexError``.
        """
        return NamedObjectList([x for x in self.unions if x.has_name()])

    @property
    @memoize
    def union_names(self):
        """Names of the unions (list of `str`)."""
        return names_of(self.named_unions)

    @property
    def union_count(self):
        """Number of unions."""
        return len(self.unions)

    @property
    def unnamed_union_count(self):
        """Number of unnamed unions."""
        return len(self.unnamed_unions)

    @property
    def named_union_count(self):
        """Number of named unions."""
        return len(self.named_unions)

    def has_any_unions(self):
        """Are there any unions (at least one)?"""
        return self.union_count > 0

    def has_any_unnamed_unions(self):
        """Are there any unnamed unions (at least one)?"""
        return self.unnamed_union_count > 0

    def has_any_named_unions(self):
        """Are there any named unions (at least one)?"""
        return self.named_union_count > 0

    def has_named_unions(self, *unions):
        """Are there given named unions?

        :param unions: Union names or instances of :class:`.UnionType`.

        Example:

        .. code-block:: python

            module.has_named_unions('u1', 'u2')
            module.has_named_unions('u1', union)

        The order is irrelevant. If you want to check that only the given
        named unions appear in the module and no other named unions
        are present, use :func:`has_just_named_unions()` instead.

        If you call this method without any arguments, it checks whether there
        is at least one union in the module:

        .. code-block:: python

            module.has_named_unions()
        """
        names = get_set_of_names(unions)
        if not names:
            return self.has_any_named_unions()
        return names.issubset(set(self.union_names))

    def has_no_unions(self):
        """Are there no unions?"""
        return self.union_count == 0

    def has_no_unnamed_unions(self):
        """Are there no unnamed unions?"""
        return self.unnamed_union_count == 0

    def has_no_named_unions(self):
        """Are there no named unions?"""
        return self.named_union_count == 0

    def has_just_named_unions(self, *unions):
        """Are there only given named unions?

        :param unions: Union names or instances of :class:`.UnionType`.

        Example:

        .. code-block:: python

            module.has_just_named_unions('u1', 'u2')
            module.has_just_named_unions('u1', union)

        The order is irrelevant.
        """
        return set(self.union_names) == get_set_of_names(unions)

    def has_named_union(self, union):
        """Is there specified named union?

        :param union: Union name or instance of :class:`.UnionType`.
        """
        return get_name(union) in self.union_names

    @property
    @memoize
    def enums(self):
        """Enums (list of :class:`.EnumType`).

        The returned type is plain list, not
        :class:`~regression_tests.utils.list.NamedObjectList`.
        """
        enum_nodes = filter(self._is_enum, self._tu.cursor.get_children())
        return [EnumType(node.type, node) for node in enum_nodes]

    @property
    @memoize
    def unnamed_enums(self):
        """Unnamed enums (list of :class:`.EnumType`).

        The returned type is plain list, not
        :class:`~regression_tests.utils.list.NamedObjectList`.
        """
        return [enum for enum in self.enums if not enum.has_name()]

    @property
    @memoize
    def named_enums(self):
        """Named enums (list of :class:`.EnumType`).

        The returned list can be indexed by either positions (0, 1, ...) or
        enum names. Example:

        .. code-block:: python

            module.named_enums[0]      # Returns the first enum.
            module.named_enums['node'] # Returns the enum named 'node'.

        When there is no such enum, it raises ``IndexError``.
        """
        return NamedObjectList([x for x in self.enums if x.has_name()])

    @property
    @memoize
    def enum_names(self):
        """Names of the enums (list of `str`)."""
        return names_of(self.named_enums)

    @property
    def enum_count(self):
        """Number of enums."""
        return len(self.enums)

    @property
    def unnamed_enum_count(self):
        """Number of unnamed enums."""
        return len(self.unnamed_enums)

    @property
    def named_enum_count(self):
        """Number of named enums."""
        return len(self.named_enums)

    def has_any_enums(self):
        """Are there any enums (at least one)?"""
        return self.enum_count > 0

    def has_any_unnamed_enums(self):
        """Are there any unnamed enums (at least one)?"""
        return self.unnamed_enum_count > 0

    def has_any_named_enums(self):
        """Are there any named enums (at least one)?"""
        return self.named_enum_count > 0

    def has_named_enums(self, *enums):
        """Are there given named enums?

        :param enums: Enum names or instances of :class:`.EnumType`.

        Example:

        .. code-block:: python

            module.has_named_enums('e1', 'e2')
            module.has_named_enums('e1', enum)

        The order is irrelevant. If you want to check that only the given
        named enums appear in the module and no other named enums
        are present, use :func:`has_just_named_enums()` instead.

        If you call this method without any arguments, it checks whether there
        is at least one enum in the module:

        .. code-block:: python

            module.has_named_enums()
        """
        names = get_set_of_names(enums)
        if not names:
            return self.has_any_named_enums()
        return names.issubset(set(self.enum_names))

    def has_no_enums(self):
        """Are there no enums?"""
        return self.enum_count == 0

    def has_no_unnamed_enums(self):
        """Are there no unnamed enums?"""
        return self.unnamed_enum_count == 0

    def has_no_named_enums(self):
        """Are there no named enums?"""
        return self.named_enum_count == 0

    def has_just_named_enums(self, *enums):
        """Are there only given named enums?

        :param enums: Enum names or instances of :class:`.EnumType`.

        Example:

        .. code-block:: python

            module.has_just_named_enums('e1', 'e2')
            module.has_just_named_enums('e1', enum)

        The order is irrelevant.
        """
        return set(self.enum_names) == get_set_of_names(enums)

    def has_named_enum(self, enum):
        """Is there specified named enum?

        :param enum: Enum name or instance of :class:`.EnumType`.
        """
        return get_name(enum) in self.enum_names

    @property
    @memoize
    def enum_item_names(self):
        """Items in enums (list of `str`)."""
        enum_item_names = []
        for node in self._tu.cursor.get_children():
            if self._is_enum(node):
                enum = EnumType(node.type, node)
                enum_item_names += enum.item_names
        return enum_item_names

    @property
    def enum_item_count(self):
        """Sum of item in all enums in module."""
        return len(self.enum_item_names)

    @property
    def empty_enums(self):
        """Empty enums (list of :class:`.EnumType`)."""
        return [enum for enum in self.enums if enum.is_empty()]

    @property
    def empty_enum_count(self):
        """Number of empty enums."""
        return len(self.empty_enums)

    def has_any_empty_enums(self):
        """Are there any empty enums (at least one)?"""
        return self.empty_enum_count > 0

    def has_no_empty_enums(self):
        """Are there no empty enums?"""
        return self.empty_enum_count == 0

    def dump(self, verbose=False):
        """Dumps information about the module to ``stdout``.

        The dumped content is same as for :func:`dump_to()`.
        :param verbose: Add dumps of functions?
        """
        self.dump_to(sys.stdout, verbose)

    def dump_to(self, stream, verbose=False):
        """Dumps information about the module to `stream`.

        :param stream: Stream to dump information to.
        :param verbose: Add dumps of functions?

        Content:

        * includes
        * global variables
        * structures
        * unions
        * enums
        * functions
        * string literals
        """
        s = []
        s.append(self.file_name)
        s.append('')
        s.append(underline('Includes:'))
        s.extend(map(str, self.includes))
        s.append('')
        s.append(underline('Global vars:'))
        s.extend(map(lambda gv: gv.str_with_type(), self.global_vars))
        s.append('')
        s.append(underline('Structs:'))
        s.extend(map(str, self.structs))
        s.append('')
        s.append(underline('Unions:'))
        s.extend(map(str, self.unions))
        s.append('')
        s.append(underline('Enums:'))
        s.extend(map(str, self.enums))
        s.append('')
        s.append(underline('Functions:'))
        s.extend(map(str, self.funcs))
        s.append('')
        s.append(underline('String literals:'))
        s.extend(self.string_literal_values)
        s.append('')

        if verbose and self.has_funcs():
            for func in self.funcs:
                header = 'Dump of {}:'.format(func.name)
                s.append(header)
                s.append('=' * len(header))
                with io.StringIO() as func_stream:
                    func.dump_to(func_stream)
                    s.append(func_stream.getvalue())

        stream.write('\n'.join(s))

    def _is_global_var(self, node):
        """Checks if the given node is a global variable.

        External global variables (coming from included headers) are not
        considered to be global variables.
        """
        return (
            self._is_from_current_file(node) and
            node.kind == cindex.CursorKind.VAR_DECL
        )

    def _is_func(self, node):
        """Checks if the given node is a function.

        External functions or function declarations are not considered to be
        functions.
        """
        return (
            self._is_from_current_file(node) and
            node.kind == cindex.CursorKind.FUNCTION_DECL and
            node.is_definition()
        )

    def _is_struct(self, node):
        """Checks if the given node is a structure.

        External structures (coming from included headers) are not
        considered to be structures.
        """
        return (
            self._is_from_current_file(node) and
            node.kind == cindex.CursorKind.STRUCT_DECL
        )

    def _is_union(self, node):
        """Checks if the given node is a union.

        External unions (coming from included headers) are not
        considered to be unions.
        """
        return (
            self._is_from_current_file(node) and
            node.kind == cindex.CursorKind.UNION_DECL
        )

    def _is_enum(self, node):
        """Checks if the given node is an enum.

        External enums (coming from included headers) are not
        considered to be enums.
        """
        return (
            self._is_from_current_file(node) and
            node.kind == cindex.CursorKind.ENUM_DECL
        )

    def _is_from_current_file(self, node):
        """Checks if the node is in the current file, i.e. not coming from an
        included file.
        """
        return (
            node.location.file is not None and
            node.location.file.name == self.file_name
        )

    def _try_read_next_include(self, tokens, i):
        """Tries to read the next include from the given list of tokens,
        starting at index `i`.

        :returns: A pair (include or ``None``, next `i`).
        """
        # There are two possible formats:
        #
        # (1)  #  include  <      FILE     >
        #      i  i + 1    i + 2  i + 3    i + X
        #
        # (2)  #  include  "file"
        #      i  i + 1    i + 2
        #
        # where FILE may be composed of identifiers and punctuation (e.g.
        # "stdio.h" is composed of two identifiers and a punctuation) and X
        # depends on the number of tokens in FILE.

        # Try format (1) first.
        if (i + 4 < len(tokens) and
                tokens[i].kind == cindex.TokenKind.PUNCTUATION and
                tokens[i].spelling == '#' and
                tokens[i + 1].kind == cindex.TokenKind.IDENTIFIER and
                tokens[i + 1].spelling == 'include' and
                tokens[i + 2].kind == cindex.TokenKind.PUNCTUATION and
                tokens[i + 2].spelling == '<'):
            include_text = '#include ' + tokens[i + 2].spelling
            i += 3  # for  #  include  ["|<]
            while (tokens[i].kind != cindex.TokenKind.PUNCTUATION or
                    tokens[i].spelling not in ['"', '>']):
                include_text += tokens[i].spelling
                i += 1
            include_text += tokens[i].spelling
            return Include(include_text), i + 1
        # Try format (2).
        elif (i + 2 < len(tokens) and
                tokens[i].kind == cindex.TokenKind.PUNCTUATION and
                tokens[i].spelling == '#' and
                tokens[i + 1].kind == cindex.TokenKind.IDENTIFIER and
                tokens[i + 1].spelling == 'include' and
                tokens[i + 2].kind == cindex.TokenKind.LITERAL):
            include_text = '#include ' + tokens[i + 2].spelling
            return Include(include_text), i + 3
        # No include.
        return (None, i + 1)

    def _has_string_literal_value_matching(self, regexp):
        """Checks if :attr:`string_literal_values` contains a string literal
        matching the given regular expression.
        """
        for value in self.string_literal_values:
            if re.fullmatch(regexp, value) is not None:
                return True
        return False

    def _contains_string_literal_matching(self, regexp):
        """Checks if the module contains a string literal matching the given
        regular expression by calling :func:`contains()`.
        """
        regexp = self._get_pattern_from(regexp)

        # We need to correctly handle situations when the regular expression
        # starts with a caret ('^') or ends with a dollar ('$'). If we did not
        # do this, the regular expression would not match after we surround it
        # with quotes.
        if regexp.startswith('^'):
            regexp = regexp[1:]
        if regexp.endswith('$'):
            regexp = regexp[:-1]

        return self.contains('"{}"'.format(regexp))

    def _get_pattern_from(self, regexp):
        """Returns the pattern (`str`) from the given regular expression
        (either `str` or a compiled regular expression).
        """
        # Compiled regular expressions have a 'pattern' attribute containing
        # the pattern.
        return regexp.pattern if hasattr(regexp, 'pattern') else regexp

    def __repr__(self):
        return '<{} file_name={!r}>'.format(
            self.__class__.__name__,
            self.file_name,
        )


from regression_tests.parsers.c_parser.exprs.literals.string_literal import StringLiteral
from regression_tests.parsers.c_parser.exprs.variable import Variable
from regression_tests.parsers.c_parser.function import Function
