#!/usr/bin/env python3
"""
    Starts a local web server on 127.0.0.1:5000 with auto-reload that can be
    used during development or to view results on local PCs.

    Warning: Do NOT use this local server in production because it may allow
             attackers to execute arbitrary code on the server!
"""

from regression_tests.web import app

app.run(debug=True)
