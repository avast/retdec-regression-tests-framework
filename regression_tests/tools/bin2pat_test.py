"""
    Test class for bin2pat tests.
"""

from regression_tests.tools.tool_test import ToolTest


class Bin2PatTest(ToolTest):
    """Test class for bin2pat tests."""

    @property
    def out_yara(self):
        """Contents of the output Yara file.

        An alias for ``self.bin2pat.out_yara``.
        """
        return self.bin2pat.out_yara
