"""
    Test class for IDA-plugin tests.
"""

from regression_tests.tools.tool_test import ToolTest


class IDAPluginTest(ToolTest):
    """Test class for IDA-plugin tests."""

    @property
    def out_c(self):
        """Contents of the output C file.

        An alias for ``self.idaplugin.out_c``.
        """
        return self.idaplugin.out_c

    def setUp(self):
        """Performs basic validations over run IDA plugin."""
        super().setUp()

        msg = '{} timeouted; output:\n...\n{}'.format(
            self.idaplugin.name,
            self.idaplugin.end_of_output()
        )
        self.assertFalse(self.idaplugin.timeouted, msg=msg)

        msg = '{} failed; output:\n...\n{}'.format(
            self.idaplugin.name,
            self.idaplugin.end_of_output()
        )
        self.assertTrue(self.idaplugin.succeeded, msg=msg)
