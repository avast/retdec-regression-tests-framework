"""
    Web interface for regression tests.
"""

from flask import Flask
app = Flask(__name__)

from regression_tests.web.views import *
