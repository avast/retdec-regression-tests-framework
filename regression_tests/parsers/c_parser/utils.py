"""
    Helper functions.
"""

from clang import cindex

from regression_tests.utils.list import items_to_set
from regression_tests.utils.list import StrPropertyList


#: Indentation to be used when emitting structured data (like members in
#: structures or unions).
INDENT = 4 * ' '


class IdentifiedObjectList(StrPropertyList):
    """A list of objects indexable with an integer or object's identification.

    It provides support for a list of objects that have an ``identification``
    attribute or property that can be indexed with an integer or object's
    identification.

    For example, consider a ``Variable`` class with an ``identification``
    attribute:

    .. code-block:: python

        class Variable:
            def __init__(self, name):
                self.identification = name

            # Other useful methods.

            def __str__(self):
                return self.name

    Then, the present class can be used to do the following:

    >>> vars = NamedObjectList([Variable('a'), Variable('b'), Variable('c')])
    >>> print(vars[1])
    b
    >>> print(vars['b'])
    b

    That is, you can index the list with integers or variable identification.
    And, as it subclasses the built-in class `list`, it provides all the
    methods of the standard `list` class.
    """

    @property
    def property_name(self):
        return 'identification'

    def modify_key(self, key):
        return remove_whitespace(key)


def is_char_kind(type):
    """Is the given Clang type of a character kind?"""
    # Clang has many kinds for a char, so check all of them.
    return type.kind in {
        cindex.TypeKind.CHAR_U,
        cindex.TypeKind.UCHAR,
        cindex.TypeKind.CHAR_S,
        cindex.TypeKind.SCHAR
    }


def is_array_kind(type):
    """Is the given Clang type of an array kind?"""
    # Clang has many kinds for an array, so check all of them.
    return type.kind in {
        cindex.TypeKind.CONSTANTARRAY,
        cindex.TypeKind.INCOMPLETEARRAY,
        cindex.TypeKind.VARIABLEARRAY,
        cindex.TypeKind.DEPENDENTSIZEDARRAY
    }


def first_child_node(node):
    """Returns the first child node of the given node."""
    children = list(node.get_children())
    assert children, 'there are no children in node {}'.format(node)
    return children[0]


def last_child_node(node):
    """Returns the last child node of the given node."""
    children = list(node.get_children())
    assert children, 'there are no children in node {}'.format(node)
    return children[-1]


def has_tokens(node):
    """Has the node any tokens?"""
    # node.get_tokens() is a generator, so check if there is at least one
    # token (a token object always evaluates to True).
    return any(node.get_tokens())


def has_token(node, token):
    """Has the node the specified token?"""
    return any(filter(lambda t: t.spelling == token, node.get_tokens()))


def has_token_in_position(node, token, pos):
    """Has the node the specified token in specified position
    (indexed from 0)?
    """
    tokens = list(node.get_tokens())
    return tokens[pos].spelling == token


def string_from_tokens(node):
    """Creates string from tokens. Omits semicolon."""
    return ''.join(map(lambda t: t.spelling, node.get_tokens()))[:-1]


def remove_whitespace(str):
    """Removes whitespace from the given string.

    Whitespace between quotation marks (``"``) is left untouched.
    """
    result = ''
    inside_string = False
    for c in str:
        if c == '"':
            inside_string = not inside_string
        elif c.isspace() and not inside_string:
            continue
        result += c
    return result


def first_token(node):
    """Returns the first token of the given node."""
    tokens = list(node.get_tokens())
    assert tokens, 'there are no tokens in node {}'.format(node)
    return tokens[0]


def visit_node(node, callback):
    """Recursively visits the given node and its children and calls callback on
    every one of them, including the passed node.

    Only the nodes that are from the same file as the given node are visited.
    """
    callback(node)
    for child in node.get_children():
        if from_same_file(child, node):
            visit_node(child, callback)


def from_same_file(node1, node2):
    """Checks if the two given nodes are from the same file."""
    return (
        node1.location.file is not None and
        node2.location.file is not None and
        node1.location.file.name == node2.location.file.name
    )


def get_parse_errors(diagnostics):
    """Returns a list of parse errors from the given diagnostics."""
    errors = []
    for diagnostic in diagnostics:
        if diagnostic.severity == cindex.Diagnostic.Error:
            errors.append('{}:{}:{}: {}'.format(
                diagnostic.location.file.name if diagnostic.location.file else '-',
                diagnostic.location.line,
                diagnostic.location.column,
                diagnostic.spelling
            ))
    return errors


def print_parse_errors(errors, file_name):
    """Prints parse errors from the given list."""
    print('Errors during parsing of {}:'.format(file_name))
    for error in errors:
        print(' - {}'.format(error))


def get_name(item):
    """Returns `item` if called with :class:`str`, `name` property of item
    otherwise."""
    if isinstance(item, str):
        return item
    else:
        return item.name


def get_set_of_names(items):
    """Returns set of names.

    :param items: list of strings and objects with `name` property.
    """
    return {get_name(item) for item in items_to_set(items)}


def underline(text):
    """Returns `text` and another line of the same length composed of dashes.

    :param str text: text to be underlined.
    """
    return '{}\n{}'.format(text, '-' * len(text))


def nth_item(n, generator):
    """Returns the `n`-th item yielded by `generator`.

    Item numbering starts from 0.
    """
    for x in range(n):
        next(generator)
    return next(generator)
