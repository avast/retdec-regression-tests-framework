"""
    Setup of Clang bindings.
"""

import os

import clang

from regression_tests.utils.os import on_windows
from regression_tests.utils.os import on_macos


#: Include paths.
INCLUDE_PATHS = []


def setup_clang_bindings(clang_dir):
    """Sets up Clang bindings so they can be used.

    This function has to be called prior to using Clang bindings.
    """
    assert os.path.exists(clang_dir), '{}: no such directory'.format(clang_dir)

    # Set a proper path to libclang so that the bindings can find them.
    if on_windows():
        libclang_file_path = os.path.join(clang_dir, 'bin', 'libclang.dll')
    elif on_macos():
        libclang_file_path = os.path.join(clang_dir, 'lib', 'libclang.dylib')
    else:
        libclang_file_path = os.path.join(clang_dir, 'lib', 'libclang.so')
    assert os.path.exists(libclang_file_path), '{}: no such file'.format(libclang_file_path)
    clang.cindex.conf.set_library_file(libclang_file_path)

    # Set proper include paths. Without them, Clang cannot find some of the
    # standard headers. These include paths have to be specified as additional
    # arguments when calling cindex.Index.parse().
    #
    # (1) CLANG_DIR/lib/clang/VERSION/include
    # Detect the VERSION part automatically (this should be the only
    # subdirectory in CLANG_DIR/lib/clang).
    clang_lib_dir = os.path.join(clang_dir, 'lib', 'clang')
    assert os.path.exists(clang_lib_dir), '{}: no such directory'.format(clang_lib_dir)
    clang_version = os.listdir(clang_lib_dir)
    assert clang_version, 'expected a subdirectory in {}'.format(clang_lib_dir)
    include_path = os.path.join(clang_dir, 'lib', 'clang', clang_version[0], 'include')
    assert os.path.exists(include_path), '{}: no such directory'.format(include_path)
    INCLUDE_PATHS.append(include_path)
    # (2) CLANG_DIR/include
    clang_include_dir = os.path.join(clang_dir, 'include')
    assert os.path.exists(clang_include_dir), '{}: no such directory'.format(clang_include_dir)
    INCLUDE_PATHS.append(clang_include_dir)
