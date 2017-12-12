"""
    The main package for regression tests.
"""

__all__ = [
    'Test',
    'TestSettings',
    'CriticalTestSettings',
    'files_in_dir',
]

# Ensure that packages in the 'libs' directory can be found during import.
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir, 'libs'))

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
