"""
    The main package for regression tests.
"""

__all__ = [
    'Test',
    'TestSettings',
    'files_in_dir',
    'on_linux',
    'on_macos',
    'on_windows',
]

# Ensure that packages in the 'deps' directory can be found during import.
import os
import sys
# Insert the path to the beginning of import paths to prioritize our packages
# in deps/ over system-level packages with the same name. This is needed when
# the user has Python Clang bindings in his system (#5).
sys.path.insert(0, os.path.join(os.path.dirname(__file__), os.pardir, 'deps'))

# Imports to simplify the importing of nested modules/classes.
from regression_tests.test import Test
from regression_tests.test_settings import TestSettings

# Utilities.
from regression_tests.test_utils import files_in_dir
from regression_tests.utils.os import on_linux
from regression_tests.utils.os import on_macos
from regression_tests.utils.os import on_windows

# Register available tool test settings. This cannot be done in modules because
# they may not be imported (then, the registration would not be performed).
from regression_tests.tools import register_available_tool_test_settings
register_available_tool_test_settings()
