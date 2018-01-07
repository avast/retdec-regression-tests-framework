"""
    Logging support.
"""

import logging
import os


def setup_logging(config, script_name):
    """Setups logging facilities for the given script.

    :param Config config: Configuration.
    :param str script_name: Name of the script that is being run.
    """
    if not config['logging'].getboolean('enabled'):
        disable_logging()
        return

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    # Log into a log file.
    log_file_handler = _create_log_file_handler(config, script_name)
    root_logger.addHandler(log_file_handler)

    if config['logging'].getboolean('log_also_to_stderr'):
        # Log into the standard error.
        stderr_handler = _create_stderr_handler(config)
        root_logger.addHandler(stderr_handler)


def disable_logging():
    """Disables the logging facilities."""
    logging.disable(logging.CRITICAL)


def _create_log_file_handler(config, script_name):
    """Creates a handler for logging into a log file and returns it."""
    log_file_path = _get_log_file_for_script(config, script_name)
    log_file_handler = logging.FileHandler(log_file_path)
    log_file_formatter = logging.Formatter(config['logging']['entry_format'])
    log_file_handler.setFormatter(log_file_formatter)
    return log_file_handler


def _get_log_file_for_script(config, script_name):
    """Returns a path to the log file for the given script."""
    logs_dir = config['logging']['logs_dir']
    if not os.path.isabs(logs_dir):
        logs_dir = os.path.join(os.path.dirname(__file__), os.pardir, logs_dir)

    return os.path.join(logs_dir, script_name + config['logging']['extension'])


def _create_stderr_handler(config):
    """Creates a handler for the standard error output and returns it."""
    stderr_handler = logging.StreamHandler()
    stderr_formatter = logging.Formatter('{} {}'.format(
        config['logging']['stderr_entry_prefix'],
        config['logging']['entry_format'])
    )
    stderr_handler.setFormatter(stderr_formatter)
    return stderr_handler
