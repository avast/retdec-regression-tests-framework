"""
    I/O-related functions.
"""

import atexit
import re
import sys

try:
    import colorama
except ImportError:
    # The colorama module is not available, so fall back to output without
    # colors. Instances of the following class can be called, and every
    # attribute is equal to the empty string (this is why it inherits from
    # str).
    class NoColorsColorama(str):
        """Fake implementation of colorama without color support."""

        def __call__(self, *args, **kwargs):
            pass

        def __getattr__(self, _):
            return self

    colorama = NoColorsColorama()
    print("warning: module 'colorama' (https://pypi.python.org/pypi/colorama)",
          "not found, running without color support", file=sys.stderr)

# Initialize Colorama. This has to be called at the beginning of this module,
# before function definitions. The reason is that the functions in this module
# have standard streams as default values of the stream argument. The
# initialization replaces them with custom streams. Therefore, if we
# initialized Colorama after the functions, the default values would be without
# color support.
colorama.init()

# Ensure that Colorama is de-initialized upon program exit. This will restore
# stdout and stderr to their original values, so that Colorama is disabled.
atexit.register(colorama.deinit)


def print_warning(msg, stream=sys.stderr):
    """Prints the given warning message to the given stream. """
    print_with_color_reset('warning: {}'.format(msg), stream)


def print_error(msg, stream=sys.stderr):
    """Prints the given error message to the given stream. """
    print_with_color_reset('error: {}'.format(msg), stream)


def print_prologue(tests_root_dir, test_cases,
                   stream=sys.stdout):
    """Prints a prologue for the tests to the given stream."""
    print_with_color_reset(
        'Running {} test case{} in {}...\n'.format(
            len(test_cases),
            's' if len(test_cases) != 1 else '',
            tests_root_dir,
        ),
        stream
    )


def print_test_results(test_results, stream=sys.stdout):
    """Prints the given test results to the given stream.
    """
    # Name and status.
    normal_color = colorama.Fore.WHITE + colorama.Style.BRIGHT
    if test_results.skipped:
        status_color = colorama.Fore.YELLOW + colorama.Style.BRIGHT
        status = 'SKIP'
    elif test_results.succeeded:
        status_color = colorama.Fore.GREEN + colorama.Style.BRIGHT
        status = 'OK'
    else:
        status_color = colorama.Fore.RED + colorama.Style.BRIGHT
        status = 'FAIL'
    name = '{}.{}'.format(
        test_results.module_name,
        test_results.case_name
    )
    # If the name is too long, trim it. Usually, the names are short enough to
    # fit, but there are some tests with long names.
    if len(name) > 98:
        name = name[0:93] + '[..])'
    text = '{0}{1:<100}[{2}{3:^6}{0}]  {4}({5:.2f}s)'.format(
        normal_color,
        name,
        status_color,
        status,
        colors_for_reset(),
        test_results.runtime
    )
    print_with_color_reset(text, stream)

    # Output.
    if test_results.failed:
        output_color = colorama.Fore.WHITE + colorama.Style.NORMAL
        print_with_color_reset(output_color + test_results.output, stream)

    # Since the tests run in parallel, ensure that the output is shown as soon
    # as possible to limit mixture of outputs from several tests.
    stream.flush()


def print_summary(tests_results, stream=sys.stdout):
    """Prints a summary for the given tests results (list of
    :class:`.TestResults`) to the given stream.
    """
    # Separate the tests from the summary with an empty line.
    print('', file=stream)

    # Print skipped tests first (if any).
    if tests_results.skipped:
        color = colorama.Fore.YELLOW + colorama.Style.BRIGHT
        print_with_color_reset(
            '{}[{} test{} skipped]'.format(
                color,
                tests_results.skipped_tests,
                's' if tests_results.skipped_tests != 1 else ''),
            stream
        )

    if tests_results.succeeded:
        color = colorama.Fore.GREEN + colorama.Style.BRIGHT
        print_with_color_reset(
            '{}SUCCESS ({}/{})'.format(
                color,
                tests_results.succeeded_tests,
                tests_results.run_tests),
            stream
        )
    else:
        color = colorama.Fore.RED + colorama.Style.BRIGHT
        print_with_color_reset(
            '{}FAIL (failed {} out of {} test{})'.format(
                color,
                tests_results.failed_tests,
                tests_results.run_tests,
                's' if tests_results.run_multiple_tests else ''),
            stream
        )


def print_with_color_reset(text, stream):
    """Prints the given text into the given stream and resets color
    afterwards.
    """
    print(text + colors_for_reset(), file=stream)


def colors_for_reset():
    """Returns a string to reset all the colors."""
    return colorama.Fore.RESET + colorama.Back.RESET + colorama.Style.RESET_ALL


def strip_shell_colors(text):
    """Strips shell colors from the given text."""
    return re.sub(r'\x1b[^m]*m', '', text)
