"""
    Utilities for writing regression tests.
"""

import inspect
import os
import re


def files_in_dir(dir, *, matching=None, excluding=None):
    """Returns a list of files in the given directory.

    :param str dir: Relative path to the directory.
    :param regexp matching: Only files whose name match the given regular
                            expression are included.
    :param regexp/list excluding: Files to be excluded. Either a list of file
                                  names or a regular expression.

    The returned files are ordered by their name and prefixed with `dir`:

    >>> files_in_dir('inputs')
    ['inputs/a.exe', 'inputs/b.exe', 'inputs/c.exe']

    To do the regular-expression matching, the standard function
    ``re.fullmatch()`` is used, which differs from ``re.match()``. Keep that in
    mind when writing regular expressions.

    .. note::

        The base directory is selected to be the directory of the file from
        which this function is called. This is needed in regression tests to
        support the following usage:

        .. code-block:: python

            settings = TestSettings(
                input=files_in_dir('inputs')
            )

        Otherwise, the user would need to explicitly pass a path to the
        directory where the ``test.py`` file is located because ``'inputs'`` is
        relative to that directory. By using dark magic, this function is able
        to find this directory automatically.
    """
    assert not os.path.isabs(dir), 'directory path has to be relative'

    # We have to find the path to the directory of the test.py file from
    # which this function is called. To do that, we have to look at the
    # stack and obtain the path from the last-but-one stack frame. This is
    # sort of a hack, but greatly simplifies the usage of this function
    # from a user's perspective.
    #
    # The first 1 below means last-but-one stack frame. The second 1 is the
    # name of the file of this stack frame.
    test_file_path = inspect.stack()[1][1]
    base_dir = os.path.dirname(test_file_path)
    abs_dir = os.path.join(base_dir, dir)

    files = os.listdir(abs_dir)

    if matching is not None:
        files = [file for file in files if re.fullmatch(matching, file)]

    if excluding is not None:
        if isinstance(excluding, list):
            files = [file for file in files if file not in excluding]
        else:
            files = [
                file for file in files if not re.fullmatch(excluding, file)
            ]

    return [os.path.join(dir, file) for file in sorted(files)]
