"""
    Utilities for the web interface.
"""


def interactive_case_name(case_name, module_name, limit=None):
    """Makes the given case name interactive.

    :param TestCaseName case_name: Name of a case.
    :param str module_name: Name of a module.
    :param int limit: Limit on the length of the shown case name (``None``
                      means no limit).

    :returns: Interactive case name (`str`).

    Example:

    >>> interactive_case_name(
    ...     TestCaseName('TestCase (file.exe -a x86)'),
    ...     'dir.subdir'
    ... )
    TestCase (
        <span class="tool-args"
              onclick="showToolArgs('file.exe -a x86', this);"
              title="Show tool arguments">
            file.exe -a x86
        </span>
    )
    """
    if limit is not None:
        # We have to adjust the limit to also include the class name and
        # parentheses.
        short_args_limit = max(limit - len(case_name.class_name) - 4, 0)
    else:
        short_args_limit = len(case_name)

    return ("""{0} (<span class="tool-args" onclick="showToolArgs('{1}', this);" """
            """title="Show tool arguments">{2}</span>)""").format(
                case_name.class_name,
                case_name.tool_args,
                case_name.short_tool_args(short_args_limit)
    )


def limit_shown_commits(selected_count, max_count):
    """Limits the number of shown commits based on the given selected (`str`)
    and maximal count (`int`).
    """
    try:
        selected_count = int(selected_count)
    except ValueError:
        selected_count = max_count
    return selected_count if 0 < selected_count < max_count else max_count
