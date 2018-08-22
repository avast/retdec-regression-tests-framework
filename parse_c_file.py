#!/usr/bin/env python3
"""
    Parses the given C source code.

    The parsed module is printed to ``stdout``, including any parsing errors.
"""

import argparse

from regression_tests.clang import setup_clang_bindings
from regression_tests.config import parse_standard_config_files
from regression_tests.parsers.c_parser import parse_file


def parse_args():
    """Parses command-line arguments and returns them."""
    parser = argparse.ArgumentParser(description='Parser of C files.')
    parser.add_argument('FILE', help=('Path to a file with C code to be parsed.'))
    parser.add_argument('-v', '--verbose', action='store_true',
                        help=('Print also dumps of functions.'))
    args = parser.parse_args()

    return args


args = parse_args()
config = parse_standard_config_files()
setup_clang_bindings(config['runner']['clang_dir'])
module = parse_file(args.FILE, print_errors=True)
if module.has_parse_errors():
    print()
module.dump(args.verbose)
