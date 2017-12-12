"""
    Settings for IDA plugin.
"""

from regression_tests.tools.idaplugin_arguments import IDAPluginArguments
from regression_tests.tools.idaplugin_runner import IDAPluginRunner
from regression_tests.tools.idaplugin_test import IDAPluginTest
from regression_tests.tools.tool_test_settings import ToolTestSettings
from regression_tests.utils import overrides
from regression_tests.utils.list import as_list


class IDAPluginTestSettings(ToolTestSettings):
    """Settings for IDA-plugin tests.

    See the description of :class:`.ToolTestSettings` for additional
    attributes.
    """

    #: Name of the tool.
    TOOL = 'idaplugin'

    def __init__(self, *, idb=None, **kwargs):
        """
        :param str/list idb: IDA database file(s).

        See the description of :class:`.ToolTestSettings` for additional
        parameters.
        """
        kwargs['tool'] = self.TOOL
        ToolTestSettings.__init__(self, **kwargs)

        # idb
        self.idb = self._merge_duplicates(idb)

    @property
    @overrides(ToolTestSettings)
    def tool_arguments_class(self):
        return IDAPluginArguments

    @property
    @overrides(ToolTestSettings)
    def tool_runner_class(self):
        return IDAPluginRunner

    @property
    @overrides(ToolTestSettings)
    def tool_test_class(self):
        return IDAPluginTest

    @classmethod
    @overrides(ToolTestSettings)
    def should_be_created_from(cls, **kwargs):
        return kwargs.get('tool') == cls.TOOL

    @property
    def idb_as_list(self):
        """IDA database file(s) as a list.

        When the IDA database file is not set, the empty list is returned.
        When there is only a single IDA database file, a singleton list is
        returned. When there are multiple files, the list is returned directly.
        """
        return as_list(self.idb)

    def has_multiple_idbs(self):
        """Checks if the settings contains multiple IDA database files.

        :returns: ``True`` if the settings contains multiple IDA database
                  files, ``False`` otherwise.
        """
        return self._has_multiple_values_for_attr('idb')
