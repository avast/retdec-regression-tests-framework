"""
    Test class for tool tests.
"""

from regression_tests.test import Test


class ToolTest(Test):
    """Test class for tool tests.

    Assume that the test was created with the following settings:

    .. code-block:: python

        class MyTest(Test):
            settings = TestSettings(
                tool='fileinfo',
                ...
            )

    To access the tool in tests, you can either use the ``tool`` attribute:

    .. code-block:: python

        assert self.tool.return_code == 0

    or the safe name of the tool:

    .. code-block:: python

        assert self.fileinfo.return_code == 0

    See the description of :func:`.Tool.safe_name()`
    for more details on the name's format.
    """

    def __init__(self, tool, settings, **kwargs):
        """
        :param Tool tool: The tool for the test.
        :param ~regression_tests.settings.TestSettings settings: The settings
            of the test.

        `settings` and all the other arguments are passed directly into the
        :class:`~regression_tests.Test`'s constructor.
        """
        # The order of the following lines is important because of an
        # overridden __getattr__() that accesses the _tool attribute.
        self._tool = tool
        super().__init__(settings, **kwargs)

    @property
    def tool(self):
        """The executed tool for the test."""
        return self._tool

    def __getattr__(self, name):
        # Allow accessing the tool through its safe name.
        if name == self.tool.safe_name:
            return self.tool

        raise AttributeError(
            "'{}' object has no attribute '{}'".format(
                self.__class__.__name__,
                name
            )
        )
