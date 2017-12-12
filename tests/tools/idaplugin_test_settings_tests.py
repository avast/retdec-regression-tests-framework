"""
    Tests for the :mod:`regression_tests.tools.idaplugin_test_settings` module.
"""

import unittest

from regression_tests.test_settings import TestSettings
from regression_tests.tools.idaplugin_arguments import IDAPluginArguments
from regression_tests.tools.idaplugin_runner import IDAPluginRunner
from regression_tests.tools.idaplugin_test import IDAPluginTest
from regression_tests.tools.idaplugin_test_settings import IDAPluginTestSettings


class IDAPluginTestSettingsTests(unittest.TestCase):
    """Tests for `IDAPluginTestSettings`."""

    def test_test_settings_creates_idaplugin_test_settings_when_tool_is_specified(self):
        settings = TestSettings(tool=IDAPluginTestSettings.TOOL, input='file.exe')
        self.assertIsInstance(settings, IDAPluginTestSettings)

    def test_tool_returns_correct_value(self):
        settings = IDAPluginTestSettings(input='file.exe')
        self.assertEqual(settings.tool, IDAPluginTestSettings.TOOL)

    def test_input_passed_to_constructor_is_accessible(self):
        INPUT = 'file.exe'
        settings = IDAPluginTestSettings(input=INPUT)
        self.assertEqual(INPUT, settings.input)

    def test_args_passed_to_constructor_are_accessible(self):
        ARGS = '--help'
        settings = IDAPluginTestSettings(input='file.exe', args=ARGS)
        self.assertEqual(ARGS, settings.args)

    def test_timeout_passed_to_constructor_is_accessible(self):
        TIMEOUT = 100
        settings = IDAPluginTestSettings(input='file.exe', timeout=TIMEOUT)
        self.assertEqual(settings.timeout, TIMEOUT)

    def test_tool_arguments_class_returns_correct_value(self):
        settings = IDAPluginTestSettings(input='file.exe')
        self.assertEqual(settings.tool_arguments_class, IDAPluginArguments)

    def test_tool_runner_class_returns_correct_value(self):
        settings = IDAPluginTestSettings(input='file.exe')
        self.assertEqual(settings.tool_runner_class, IDAPluginRunner)

    def test_tool_test_class_returns_correct_value(self):
        settings = IDAPluginTestSettings(input='file.exe')
        self.assertEqual(settings.tool_test_class, IDAPluginTest)

    def test_idb_passed_to_constructor_is_accessible(self):
        IDB = 'file.idb'
        settings = IDAPluginTestSettings(input='file.exe', idb=IDB)
        self.assertEqual(IDB, settings.idb)

    def test_idb_as_list_returns_empty_list_if_idb_is_not_set(self):
        settings = IDAPluginTestSettings(input='file.exe', idb=None)
        self.assertEqual([], settings.idb_as_list)

    def test_idb_as_list_returns_idb_when_idb_is_list(self):
        IDB = ['file1.idb', 'file2.idb']
        settings = IDAPluginTestSettings(input='file.exe', idb=IDB)
        self.assertEqual(IDB, settings.idb_as_list)

    def test_idb_as_list_returns_list_when_idb_is_single_file(self):
        IDB = 'file.idb'
        settings = IDAPluginTestSettings(input='file.exe', idb=IDB)
        self.assertEqual([IDB], settings.idb_as_list)

    def test_has_multiple_idbs_returns_true_when_there_are_multiple_idbs(self):
        settings = IDAPluginTestSettings(input='file.exe', idb=['file1.idb', 'file2.idb'])
        self.assertTrue(settings.has_multiple_idbs())

    def test_has_multiple_idbs_returns_false_when_there_is_just_single_idb(self):
        settings = IDAPluginTestSettings(input='file.exe', idb='file.idb')
        self.assertFalse(settings.has_multiple_idbs())

    def test_duplicate_idbs_are_merged(self):
        settings = IDAPluginTestSettings(input='file.exe', idb=['file.idb', 'file.idb'])
        self.assertEqual(settings.idb, 'file.idb')

        settings = IDAPluginTestSettings(
            input='file.exe',
            idb=['file.idb', 'other.idb', 'file.idb']
        )
        self.assertEqual(settings.idb, ['file.idb', 'other.idb'])
