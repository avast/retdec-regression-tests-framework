"""
    Tests for the :mod:`regression_tests.config` module.
"""

import unittest

from regression_tests import config
from tests.utils import TemporaryFile


class ParseTests(unittest.TestCase):
    """Tests for `config.parse()`."""

    def test_empty_config_is_returned_when_no_files_are_given(self):
        parsed_config = config.parse()
        self.assertEqual(parsed_config.sections(), [])

    def test_single_file_is_parsed_correctly(self):
        config_content = '''
        ; Global configuration file

        [sec1]
            var1 = value1

        [sec2]
            var2 = value2
        '''
        with TemporaryFile(config_content) as cf:
            parsed_config = config.parse(cf.path)
            self.assertEqual(parsed_config.sections(), ['sec1', 'sec2'])
            self.assertEqual(parsed_config['sec1']['var1'], 'value1')
            self.assertEqual(parsed_config['sec2']['var2'], 'value2')

    def test_two_files_are_parsed_correctly(self):
        global_config_content = '''
        ; Global configuration file

        [sec1]
            var1 = value1

        [sec2]
            var2 = value2
        '''
        local_config_content = '''
        ; Local configuration file

        [sec2]
            var2 = other_value2
            var3 = value3
        '''
        with TemporaryFile(global_config_content) as global_cf:
            with TemporaryFile(local_config_content) as local_cf:
                parsed_config = config.parse(global_cf.path, local_cf.path)
                self.assertEqual(parsed_config.sections(), ['sec1', 'sec2'])
                self.assertEqual(parsed_config['sec1']['var1'], 'value1')
                self.assertEqual(parsed_config['sec2']['var2'], 'other_value2')
                self.assertEqual(parsed_config['sec2']['var3'], 'value3')

    def test_file_that_cannot_be_read_is_ignored(self):
        parsed_config = config.parse('/hopefully-non-existing-file.txt')
        self.assertEqual(parsed_config.sections(), [])
