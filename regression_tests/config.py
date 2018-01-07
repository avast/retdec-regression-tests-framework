"""
    Representation and parsing of configuration files.
"""

import configparser
import os


def parse_config(config_files):
    """Parses the given configuration files and returns the configuration.

    Options may be overridden. This allows one to have a global configuration
    file that specifies all the available options with default values, and
    local configuration files that contain local settings that override the
    global ones.

    If any of the configuration files cannot be read, it is ignored.
    """
    config = configparser.ConfigParser()
    config.read(config_files)
    return config


def parse_standard_config_files(include_local=True):
    """Parses configurations files from the standard location.

    The standard location is the root directory of the framework.
    """
    def path_to(config_file):
        return os.path.join(os.path.dirname(__file__), os.pardir, config_file)

    config_files = ['config.ini']
    if include_local:
        config_files.append('config_local.ini')

    return parse_config([path_to(config_file) for config_file in config_files])
