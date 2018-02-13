"""
    Views for the web interface.
"""

import jinja2
from flask import g
from flask import redirect
from flask import render_template
from flask import request

from regression_tests.config import parse_standard_config_files
from regression_tests.db import DB
from regression_tests.utils.format import format_age
from regression_tests.utils.format import format_date
from regression_tests.utils.format import format_id
from regression_tests.utils.format import format_runtime
from regression_tests.web import app
from regression_tests.web.utils import interactive_case_name
from regression_tests.web.utils import limit_shown_commits


@app.template_filter()
@jinja2.evalcontextfilter
def nl2br(eval_ctx, text):
    """A jinja2 filter that converts newlines in the given text to ``<br />``.

    This filter is needed to be used when displaying text having newlines.
    """
    # Based on:
    #  - http://flask.pocoo.org/snippets/28/
    #  - http://stackoverflow.com/a/14126505
    result = jinja2.escape(text).replace('\n', jinja2.Markup('<br />'))
    if eval_ctx.autoescape:
        result = jinja2.Markup(result)
    return result


@app.before_request
def before_request():
    g.config = parse_standard_config_files()
    g.db = DB(g.config['db']['conn_url'])

    # Template settings.
    app.jinja_env.lstrip_blocks = True
    app.jinja_env.trim_blocks = True

    # Filters.
    app.jinja_env.filters['age'] = format_age
    app.jinja_env.filters['date'] = format_date
    app.jinja_env.filters['id'] = format_id
    app.jinja_env.filters['runtime'] = format_runtime
    app.jinja_env.filters['nl2br'] = nl2br


@app.route('/')
def index():
    # Number of commits to show.
    max_commits_count = g.db.get_commits_count()
    shown_commits_count = limit_shown_commits(
        request.args.get('commits', g.config['web']['max_commits']),
        max_commits_count
    )

    context = {
        'shown_commits_count': shown_commits_count,
        'max_commits_count': max_commits_count,
        'interactive_case_name': interactive_case_name,
        'commit_details_url': g.config['web']['commit_details_url'],
        'commits_results': g.db.get_results_for_recent_commits(
            shown_commits_count
        ),
        'last_db_update': g.db.get_date_of_last_update(),
        'wiki_page_url': g.config['web']['wiki_page_url'],
        'api_docs_url': g.config['web']['api_docs_url']
    }
    return render_template('index.html', **context)


@app.route('/docs/')
def docs():
    return redirect(g.config['web']['api_docs_url'], code=301)
