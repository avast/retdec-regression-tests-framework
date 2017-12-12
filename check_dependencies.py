#!/usr/bin/env python3
"""
    Checks the dependencies for the regression tests framework.
"""

import sys


def print_status(what, purpose, status):
    print(' - {:<18} {:<27} [{:}]'.format(what, '(' + purpose + ')', status))


def check_module_availability(module_name, purpose):
    import importlib
    try:
        importlib.__import__(module_name)
        status = 'OK'
    except ImportError:
        status = 'FAIL'
    print_status(module_name, purpose, status)


#
# Required.
#
print('Required:')

# Python >= 3.4.
python_version = sys.version_info
if python_version.major < 3 or python_version.minor < 4:
    status = 'FAIL, only {}.{}.{}'.format(
        python_version.major,
        python_version.minor,
        python_version.micro
    )
else:
    status = 'OK'
print_status('Python >= 3.4', 'interpreter', status)

print()

# Note: When adding a package into one of the lists below, do not forget to
#       also add it to dependencies.txt!

#
# Optional but recommended.
#
print('Optional but recommended:')
check_module_availability('colorama', 'color support')
check_module_availability('sqlalchemy', 'database support')
check_module_availability('flask', 'web interface')

print()

#
# Optional (for developers).
#
print('Optional (for developers):')
check_module_availability('flake8', 'source code analysis')
check_module_availability('nose', 'unit tests runner')
check_module_availability('coverage', 'code coverage')
check_module_availability('sphinx', 'documentation generator')
check_module_availability('sphinx_rtd_theme', 'documentation theme')
