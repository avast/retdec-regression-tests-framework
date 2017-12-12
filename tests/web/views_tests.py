"""
    Tests for the :mod:`regression_tests.web.views` module.
"""

import configparser
import unittest
from unittest import mock

from regression_tests.web import app


class BaseViewsTests(unittest.TestCase):
    """A base class for all views tests."""

    def setUp(self):
        self.app = app.test_client()

        # Patch parse_config() to allow config customization.
        parse_config_patcher = mock.patch('regression_tests.web.views.parse_config')
        self.addCleanup(parse_config_patcher.stop)
        self.mock_parse_config = parse_config_patcher.start()
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')
        self.mock_parse_config.return_value = self.config

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
