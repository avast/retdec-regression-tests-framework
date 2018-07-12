"""
    A representation of a decompilation that has run.
"""

import re

from regression_tests.parsers.fileinfo_output_parser import FileinfoOutput
from regression_tests.tools.tool import Tool
from regression_tests.utils import memoize
from regression_tests.utils import overrides


class Decompiler(Tool):
    """A representation of a decompilation that has run."""

    @property
    def input_file(self):
        """The input file (:class:`.File`)."""
        return self.args.input_files[0]

    @property
    def out_hll_file(self):
        """Output file in the high-level language (C, Python)."""
        return self._get_file(self.args.output_file.name)

    @property
    @memoize
    def out_hll(self):
        """Contents of the output file in the high-level language (C, Python).
        """
        return self.out_hll_file.text

    def out_hll_is_c(self):
        """Checks if the output file in the high-level language is a C file."""
        return self.args.hll is None or self.args.hll == 'c'

    @property
    def out_c_file(self):
        """Output file in the C language.

        An alias for the :func:`out_hll_file` property.

        :raises AssertionError: If the HLL is not C.
        """
        self._verify_output_hll_is_c()
        return self.out_hll_file

    @property
    @memoize
    def out_c(self):
        """Contents of the output file in the C language.

        An alias for the :func:`out_hll` property.

        :raises AssertionError: If the HLL is not C.
        """
        self._verify_output_hll_is_c()
        return self.out_hll

    @property
    def out_dsm_file(self):
        """Output DSM file."""
        return self._get_file(self.args.output_file.name + '.frontend.dsm')

    @property
    @memoize
    def out_dsm(self):
        """Contents of the output DSM file.
        """
        return self.out_dsm_file.text

    @property
    def out_config_file(self):
        """Output configuration file."""
        return self._get_file(self.args.output_file.name + '.json')

    @property
    @memoize
    def out_config(self):
        """Contents of the output configuration file.
        """
        return self.out_config_file.text

    @property
    @overrides(Tool)
    def log_file_name(self):
        return self.args.output_file.name + '.log'

    @property
    @memoize
    def fileinfo_output(self):
        """Output from fileinfo (:class:`FileinfoOutput`).

        When there are multiple outputs (i.e. fileinfo run several times), it
        returns the first one. If this is the case, you can use
        func:`fileinfo_outputs()` instead, which always returns a list.

        :raises AssertionError: If fileinfo did not run or did not produce any
                                output.
        """
        if not self.fileinfo_outputs:
            raise AssertionError('fileinfo did not run or did not produce any output')
        return self.fileinfo_outputs[0]

    @property
    @memoize
    def fileinfo_outputs(self):
        """Outputs from fileinfo (list of :class:`FileinfoOutput`).

        This function can be used when fileinfo run several times. If it run
        only once, a singleton list is returned.
        """
        outputs = re.findall(r"""
                \#\#\#\#\#\ Gathering\ file\ information[^\n]+\n
                RUN: [^\n]+\n
                (.*?)
                \n
                (?:
                    \#\#\#\#\#\                          # Ended correctly.
                |
                    \./retdec_decompiler.py:\ line\ \d+: # Failed (segfault etc.).
                )
            """, self.log, re.VERBOSE | re.MULTILINE | re.DOTALL)
        return [FileinfoOutput(output.strip()) for output in outputs]

    def _verify_output_hll_is_c(self):
        """Verifies that the output HLL is C."""
        if not self.out_hll_is_c():
            raise AssertionError('the output high-level language is not C')
