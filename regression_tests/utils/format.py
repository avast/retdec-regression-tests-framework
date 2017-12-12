"""
    Formatting utilities.
"""

# The implementation of format_age() and format_date() is taken from
# https://github.com/s3rvac/git-branch-viewer/blob/master/viewer/format.py

import re


def format_age(age):
    """Formats the given age (`timedelta` object).

    :returns: `age` of the form ``'X seconds/hours/days'``.

    When `age` is negative, the minus sign (``-``) is prepended before the
    returned string.
    """
    def format_nonnegative_age(age):
        # The timedelta internal representation uses only days and seconds (and
        # microseconds, but we do not care about them).
        SECONDS_IN_HOUR = 3600
        SECONDS_IN_MINUTE = 60
        if age.days > 0:
            repr = '{} days'.format(age.days)
        elif age.seconds >= SECONDS_IN_HOUR:
            repr = '{} hours'.format(age.seconds // SECONDS_IN_HOUR)
        elif age.seconds >= SECONDS_IN_MINUTE:
            repr = '{} minutes'.format(age.seconds // SECONDS_IN_MINUTE)
        else:
            repr = '{} seconds'.format(age.seconds)
        # Remove the ending 's' if we have only 1 second/minute/hour/day.
        return repr if not repr.startswith('1 ') else repr[:-1]

    def format_negative_age(age):
        return '-' + format_nonnegative_age(abs(age))

    def is_negative(age):
        return age.total_seconds() < 0

    if is_negative(age):
        return format_negative_age(age)
    return format_nonnegative_age(age)


def format_date(date):
    """Formats the given date (`datetime` object).

    :returns: `date` of the form ``'YYYY-MM-DD HH:MM:SS'``.

    If `date` is ``None``, it returns ``'-'``.
    """
    return date.strftime('%Y-%m-%d %H:%M:%S') if date is not None else '-'


def format_id(s):
    """Formats the given string so it can be used as an ID.

    Example:

    >>> format_id('name.surname')
    name-surname
    """
    if not s:
        return '_'
    return re.sub(r'[^-a-zA-Z0-9_]', '-', s)


def format_runtime(runtime):
    """Formats the given running time (in seconds)."""
    if runtime < 60:
        # Just seconds.
        return '{:.2f}s'.format(runtime)

    # Minutes and seconds.
    return '{}m {}s'.format(int(runtime // 60), int(runtime % 60))
