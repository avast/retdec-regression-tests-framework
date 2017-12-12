"""
    Tools.
"""

import importlib
import os
import re

from regression_tests.test_settings import TestSettings
from regression_tests.tools.tool_test_settings import ToolTestSettings
from regression_tests.utils.list import move_to_end


def register_available_tool_test_settings():
    """Registers test settings for all available tools."""
    # We need to ensure that ToolTestSettings are registered as the very last
    # settings because we want ToolTestSettings subclasses (like
    # FileinfoTestSettings) to take precedence.
    available_classes = list(_available_tool_test_settings_classes())
    move_to_end(ToolTestSettings, available_classes)

    for cls in available_classes:
        _register_tool_test_settings_class(cls)


def _available_tool_test_settings_classes():
    """Generates all available tool test setting classes."""
    for module_name, class_name in _tool_test_settings_module_and_class_names():
        yield _class_from_module(module_name, class_name)


def _tool_test_settings_module_and_class_names():
    """Generates pairs (module name, class name) of modules with classes
    representing tool test settings.
    """
    for file_name in os.listdir(os.path.dirname(__file__)):
        m = re.fullmatch(r'(.+_test_settings).py', file_name)
        if m is not None:
            module_name = m.group(1)
            yield module_name, _module_name_to_class_name(module_name)


def _class_from_module(module_name, class_name):
    """Imports and returns the given class from the given module."""
    module = importlib.import_module('{}.{}'.format(__name__, module_name))
    return getattr(module, class_name)


def _module_name_to_class_name(module_name):
    """Converts the given name of a module containing a tool test settings
    class into a class name.
    """
    # Settings for some of our tools have to be treated specially because the
    # generic conversion below is inadequate.
    if module_name == 'idaplugin_test_settings':
        return 'IDAPluginTestSettings'
    elif module_name == 'bin2pat_test_settings':
        return 'Bin2PatTestSettings'

    # Generic conversion. For example, 'tool_test_settings' is converted to
    # 'ToolTestSettings'.
    return ''.join(part.title() for part in module_name.split('_'))


def _register_tool_test_settings_class(cls):
    """Registers the given tool test settings class."""
    TestSettings.register_test_settings(cls)
