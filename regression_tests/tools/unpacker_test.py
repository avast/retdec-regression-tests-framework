"""
    Test class for unpacker tests.
"""

from regression_tests.tools.tool_test import ToolTest


class UnpackerTest(ToolTest):
    """Test class for unpacker tests."""

    @property
    def fileinfo(self):
        """Access to the fileinfo run after unpacking.

        An alias for ``self.tool.fileinfo``. See the description of the
        :attr:`~regression_tests.tools.unpacker.Unpacker.fileinfo` property for
        more details.
        """
        return self.tool.fileinfo
