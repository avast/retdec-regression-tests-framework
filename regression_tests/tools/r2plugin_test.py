"""
    Test class for r2plugin tests.
"""

from regression_tests.tools.tool_test import ToolTest


class R2PluginTest(ToolTest):
    """Test class for r2plugin tests."""

    @property
    def out_c(self):
        """Contents of the output C file.

        An alias for ``self.r2plugin.out_c``.
        """
        return self.r2plugin.out_c

    def setUp(self):
        """Performs basic validations over run r2 plugin."""
        super().setUp()

        msg = '{} timeouted; output:\n...\n{}'.format(
            self.r2plugin.name,
            self.r2plugin.end_of_output()
        )
        self.assertFalse(self.r2plugin.timeouted, msg=msg)

        msg = '{} failed; output:\n...\n{}'.format(
            self.r2plugin.name,
            self.r2plugin.end_of_output()
        )
        self.assertTrue(self.r2plugin.succeeded, msg=msg)
