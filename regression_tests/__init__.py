"""
    The main package for regression tests.
"""

__all__ = [
    'Test',
    'TestSettings',
    'CriticalTestSettings',
    'files_in_dir',
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
from regression_tests.test_settings import CriticalTestSettings

# Utilities.
from regression_tests.test_utils import files_in_dir

# Register available tool test settings. This cannot be done in modules because
# they may not be imported (then, the registration would not be performed).
from regression_tests.tools import register_available_tool_test_settings
register_available_tool_test_settings()
