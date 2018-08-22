"""
    OS-related utilities.
"""

import binascii
import contextlib
import os
import re
import sys


@contextlib.contextmanager
def chdir(dir):
    """A context manager that performs actions in the given directory.

    Example:

    >>> import os
    >>> print(os.getcwd())
    /
    >>> with chdir('/tmp'):
    ...     print(os.getcwd())
    ...
    /tmp
    >>> print(os.getcwd())
    /
    """
    # From http://petrzemek.net/blog/2014/06/21/unit-testing-with-unittest-mock-patch/.
    orig_cwd = os.getcwd()
    os.chdir(dir)
    try:
        yield
    finally:
        os.chdir(orig_cwd)


def make_file_name_valid(file_name, max_length=255):
    """Returns a version of the given file name that should be valid on most
    current operating systems and filesystems.

    Invalid characters are removed from the file name. If the resulting file
    name is empty, this function returns an underscore (``'_'``).

    Long file names may be trimmed. According to the wikipedia page below, the
    maximum allowed length is usually 255 characters for commonly used file
    systems (e.g. ext4 and NTFS). Pass a different `max_length` to
    override this limit (``None`` means no limit). When `max_length` is too
    low, the minimal usable length will be automatically used.

    Based on http://en.wikipedia.org/wiki/Filename.
    """
    file_name = _remove_invalid_characters(file_name)
    if not file_name:
        file_name = '_'

    if max_length is not None:
        file_name = _trim_file_name(file_name, max_length)

    return file_name


def make_dir_name_valid(dir_name, path_to_dir=None, max_nested_file_length=None):
    """Version of :func:`make_file_name_valid()` for directory names.

    :param str dir_name: Name of the directory to make valid.
    :param str path_to_dir: The absolute path to the directory (when known).
    :param int max_nested_file_length: The maximal length of files that may
        appear in the directory (when known).

    The `path_to_dir` and `max_nested_file_length` parameters are needed only
    on Windows.
    """
    # On Linux, the situation is very simple.
    if not on_windows():
        return make_file_name_valid(dir_name)

    # On Windows, there is an additional limitation: a complete path may
    # have at most 260 characters
    # (https://msdn.microsoft.com/en-us/library/windows/desktop/aa365247%28v=vs.85%29.aspx).
    # We use the absolute path to the directory and the
    # maximal-nested-file-length hint to create a (hopefully) proper limit of
    # the name of the directory.
    assert path_to_dir is not None, 'path_to_dir is required on Windows'
    assert max_nested_file_length is not None, 'max_nested_file_length is required on Windows'
    max_length = 260 - len(path_to_dir) - len(os.path.sep) - max_nested_file_length
    return make_file_name_valid(dir_name, max_length=max_length)


def on_linux():
    """Returns ``True`` if the script is running on Linux."""
    return sys.platform == 'linux'


def on_windows():
    """Returns ``True`` if the script is running on MS Windows."""
    # On 64b Windows, the value of sys.platform is also 'win32'
    # (https://stackoverflow.com/a/2145582).
    return sys.platform in ('win32', 'msys')


def on_macos():
    """Returns ``True`` if the script is running on macOS."""
    return sys.platform == 'darwin'


def _remove_invalid_characters(file_name):
    """Removes invalid characters from the given file name."""
    return re.sub(r'[/\x00-\x1f]', '', file_name)


def _trim_file_name(file_name, max_length):
    """Trims the given file name to the given maximal length and returns it."""
    if len(file_name) <= max_length:
        return file_name

    # To preserve uniqueness, we shorten the file name to a certain number
    # of characters and append the CRC32 sum of the original name to it.
    # Then, the new file name will be
    #
    #     "$PREFIX_OF_ORIG_NAME - crc32($ORIG_NAME)"
    #
    # We use CRC32 instead of e.g. MD5 to make the hash shorter.
    SEPARATOR = ' - '
    CRC32_HASH = str(binascii.crc32(file_name.encode()))
    PREFIX_LENGTH = max_length - (len(CRC32_HASH) + len(SEPARATOR))

    # We have to ensure that the prefix has a sufficient length; otherwise, use
    # just the hash.
    if PREFIX_LENGTH <= 0:
        return CRC32_HASH

    return '{}{}{}'.format(
        file_name[:PREFIX_LENGTH],
        SEPARATOR,
        CRC32_HASH
    )
