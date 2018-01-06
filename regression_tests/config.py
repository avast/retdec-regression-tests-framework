"""
    Representation and parsing of configuration files.
"""

import configparser


def parse_config(*config_files):
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
