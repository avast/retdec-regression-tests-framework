"""
    Tests for the :mod:`regression_tests.utils` package.

    Due to name clashes, this package also contains utilities for tests.
"""

import os
import tempfile


class TemporaryFile:
    """A context manager for working with a temporary file containing the given
    content.

    Example:

    >>> with TemporaryFile("file content") as f:
    >>>     print(f.path)

    The created object (``f`` above) has the following attributes:

    * `content`: original content passed to the constructor
    * `path`: path to the file
    """

    def __init__(self, content):
        self.content = content

    def __enter__(self):
        with tempfile.NamedTemporaryFile('wt', delete=False) as f:
            self.path = f.name
            try:
                f.write(self.content)
                f.flush()
            except:  # noqa: E722
                os.remove(self.path)
                raise
        return self

    def __exit__(self, *exc_info):
        os.remove(self.path)
