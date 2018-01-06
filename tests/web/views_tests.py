"""
    Tests for the :mod:`regression_tests.web.views` module.
"""

import unittest
from unittest import mock

from regression_tests.config import parse_standard_config_files
from regression_tests.web import app


class BaseViewsTests(unittest.TestCase):
    """A base class for all views tests."""

    def setUp(self):
        self.app = app.test_client()

        # Patch parse_standard_config_files() to allow config customization.
        parse_config_patcher = mock.patch('regression_tests.web.views.parse_standard_config_files')
        self.addCleanup(parse_config_patcher.stop)
        self.mock_parse_standard_config_files = parse_config_patcher.start()
        # Do not parse the local configuration file to ensure that the tests
        # are run with the same settings, disregarding overrides in the local
        # configuration file.
        self.config = parse_standard_config_files(include_local=False)
        self.mock_parse_standard_config_files.return_value = self.config

        # Customize the config by overriding the needed global settings.
        # Use the SQLite :memory: database.
        self.config['db']['conn_url'] = 'sqlite://'


class IndexTests(BaseViewsTests):
    """Tests for the `/` endpoint."""

    def test_index_page_exists(self):
        rv = self.app.get('/')
        self.assertEqual(rv.status_code, 200)


class DocsTests(BaseViewsTests):
    """Tests for the `/docs` endpoint."""

    def test_redirect_is_performed(self):
        rv = self.app.get('/docs')
        self.assertEqual(rv.status_code, 301)
