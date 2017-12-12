"""
    Tests for the regression tests.
"""

from unittest import mock

from regression_tests.clang import setup_clang_bindings
from regression_tests.config import parse as parse_config


class WithPatching:
    """A mixin that allows simple patching through ``mock.patch`` in tests
    during their setup phase.
    """

    def patch(self, what, with_what):
        """Patches `what` with `with_what`."""
        patcher = mock.patch(what, with_what)
        patcher.start()
        self.addCleanup(patcher.stop)


# We need to setup Clang bindings as they are used by tests for parsing of C
# source code.
config = parse_config('config.ini', 'config_local.ini')
setup_clang_bindings(config['runner']['clang_dir'])
del config
