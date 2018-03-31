"""
    Parsing of C files.
"""

import os

from clang import cindex

from regression_tests.clang import INCLUDE_PATHS
from regression_tests.parsers.c_parser.utils import get_parse_errors
from regression_tests.parsers.c_parser.utils import print_parse_errors


def parse(code, file_name='dummy.c', print_errors=False):
    """Parses the given C code.

    :param str code: C code to be parsed.
    :param str file_name: Optional name of the original file.
    :param bool print_errors: Should parse errors be printed?

    :returns: Parsed representation of the given file (:class:`Module`).
    """
    index = cindex.Index.create()
    tu = index.parse(
        file_name,
        # We have to use proper include paths. Without them, Clang cannot find
        # some of the standard headers, such as stddef.h.
        args=['-std=c99'] + ['-I{}'.format(path) for path in INCLUDE_PATHS],
        unsaved_files=[(file_name, code)]
    )

    if print_errors:
        parse_errors = get_parse_errors(tu.diagnostics)
        if parse_errors:
            print_parse_errors(parse_errors, file_name)

    return Module(code, tu)


def parse_file(file_path, encoding='utf-8', print_errors=False):
    """Parses the given C file.

    :param str file_path: Path to the file to be parsed.
    :param str encoding: Encoding of the file.
    :param bool print_errors: Should parse errors be printed?

    :returns: Parsed representation of the given file (:class:`Module`).
    """
    with open(file_path, 'r', encoding=encoding) as f:
        return parse(
            f.read(),
            file_name=os.path.basename(file_path),
            print_errors=print_errors
        )


from regression_tests.parsers.c_parser.module import Module
