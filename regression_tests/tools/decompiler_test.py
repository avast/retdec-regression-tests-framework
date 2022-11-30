"""
    Test class for decompilation tests.
"""

import os
import re

from regression_tests.tools.tool_test import ToolTest
from regression_tests.utils.os import on_windows, on_macos


class DecompilerTest(ToolTest):
    """Test class for decompilation tests."""

    @property
    def decompiler(self):
        """The executed decompilation for the test."""
        return self._tool

    @property
    def out_c(self):
        """Contents of the output file in the C language.

        An alias for ``self.decompiler.out_hll``.
        """
        return self.decompiler.out_c

    @property
    def out_dsm(self):
        """Contents of the output DSM file.

        An alias for ``self.decompiler.out_dsm``.
        """
        return self.decompiler.out_dsm

    @property
    def out_config(self):
        """Contents of the output configuration file.

        An alias for ``self.decompiler.out_config``.
        """
        return self.decompiler.out_config

    @property
    def out_ll(self):
        """Contents of the output LLVM IR file.

        An alias for ``self.decompiler.out_ll``.
        """
        return self.decompiler.out_ll

    def setUp(self):
        """Performs basic validations over the run decompilation."""
        super().setUp()

        msg = '{} timeouted; output:\n...\n{}'.format(
            self.decompiler.name,
            self.decompiler.end_of_output()
        )
        self.assertFalse(self.decompiler.timeouted, msg=msg)

        msg = '{} failed; output:\n...\n{}'.format(
            self.decompiler.name,
            self.decompiler.end_of_output()
        )
        self.assertEqual(self.decompiler.return_code, 0, msg=msg)

    def assert_c_produces_output_when_run(self, input, expected_output,
                                          expected_return_code=None, timeout=5):
        """Asserts that the output C produces the given output when compiled
        and run with the given input.

        :param str input: Input passed to the compiled program.
        :param str expected_output: Output that is expected to be produced.
        :param int expected_return_code: Exit code that is expected to be
                                         returned by the program.
        :param int timeout: Timeout for the compilation and execution of the
                            program (in seconds).

        :raises AssertionError:

          - If the output file from the decompilation is not a C file.
          - If there is an error during the compilation (syntax error, crash,
            timeout).
          - If the obtained output differs from the expected output.
          - If the program exits with a different return code than expected
            (pass ``None`` as `expected_return_code` to skip the check for the
            return code).
        """
        self._verify_decomp_output_is_c_file()
        self._compile_output_file(timeout)
        actual_output, actual_return_code = self._run_compiled_output_file(
            input, timeout)

        msg = 'where the input was: {}'.format(input)
        if expected_return_code is not None:
            self.assertEqual(actual_return_code, expected_return_code, msg)
        self.assertEqual(actual_output, expected_output, msg)

    def assert_out_c_is_compilable(self, timeout=5):
        """Asserts that the output C file can be compiled within the given
        timeout.

        :raises AssertionError:

          - If the output file from the decompilation is not a C file.
          - If there is an error during the compilation (syntax error, crash,
            timeout).
        """
        self._verify_decomp_output_is_c_file()
        self._compile_output_file(timeout)

    def _should_skip_c_compilation_tests(self):
        """Should we skip tests that want to compile output C file?"""
        # We use environment variables to communicate the configuration from a
        # runner to tests as there is currently no better way (see runner.py).
        return 'RETDEC_TESTS_SKIP_C_COMPILATION_TESTS' in os.environ

    def _verify_decomp_output_is_c_file(self):
        """Verifies that the decompilation produced a C file."""
        if not self.decompiler.out_hll_is_c():
            raise AssertionError('the output file is not a C file')

    def _compile_output_file(self, timeout):
        """Compiles the output C file.

        If we should skip tests that compile output

        If the file has already been compiled, this function does nothing.
        """
        if self._should_skip_c_compilation_tests():
            self.skipTest('compilation of C files is disabled')

        self._fix_out_c_file_if_needed()
        self._compile_file_if_not_exists(
            self._fixed_out_c_file,
            self._compiled_out_c_file,
            timeout
        )

    @property
    def _compiled_input_c_file(self):
        """Compiled input C file."""
        return self.decompiler.dir.get_file(
            self.decompiler.input_file.name + '-compiled'
        )

    @property
    def _fixed_out_c_file(self):
        """Fixed output C file."""
        if self._out_c_file_needs_to_be_fixed():
            return self.decompiler.out_c_file.renamed(
                self.decompiler.out_c_file.name + '.fixed.c')
        # We can use the original file.
        return self.decompiler.out_c_file

    @property
    def _compiled_out_c_file(self):
        """Compiled output C file."""
        return self.decompiler.out_c_file.renamed(
            self.decompiler.out_c_file.name + '-compiled'
        )

    def _compile_file_if_not_exists(self, input_file, output_file, timeout):
        """Compiles the given input file to the given output file with the
        given timeout.
        """
        if output_file.exists():
            return

        compiler_arch_bitsize = '-m64' if self._use_64_bit_compiler() else '-m32'
        output, return_code, timeouted = self.decompiler._run_cmd(
            self._get_compiler_for_out_c() + [
                '--std=c99', compiler_arch_bitsize, input_file.path, '-o', output_file.path
            ]
        )
        what = "compilation of file '{}'".format(input_file.path)
        self._verify_not_timeouted(what, timeouted, timeout)
        self._verify_ended_successfully(what, return_code, output)

        return output

    def _get_compiler_for_out_c(self):
        """Returns a compiler for the output C file."""
        # Currently, we always use GCC.
        if on_windows():
            # Since MSYS2 does not support multilib, we have to use our custom
            # wrappers around gcc that properly handle the -m32/-m64 parameters.
            # Moreover, since these wrappers are shell scripts, we have to run
            # them through sh.exe (otherwise, Windows doesn't find them).
            if self._use_64_bit_compiler():
                return ['sh', 'windows-gcc-64.sh']
            else:
                return ['sh', 'windows-gcc-32.sh']
        return ['gcc']

    def _use_64_bit_compiler(self):
        """Should we use a 64b compiler to compile the output C file?"""
        arch = self.out_config.json.get('architecture', {})
        return arch.get('bitSize') == 64 or on_macos()

    def _fix_out_c_file_if_needed(self):
        """Fixes the output C unless it has already been fixed or does not need
        to be fixed.
        """
        if (not self._out_c_file_needs_to_be_fixed() or
                self._fixed_out_c_file.exists()):
            return

        out_c = self.decompiler.out_c

        # To make the decompiled C compilable, some functions need to be
        # inserted at the beginning of it.
        fix = '// ================ COMPILATION FIX BEGIN ================\n'
        if self._decomp_arch == 'arm':
            fix += 'int modsi3(int a, int b) { return a % b; }\n'
            fix += 'int divsi3(int a, int b) { return a / b; }\n'
            fix += 'float divdf3(float a, float b) { return a / b; }\n'
            fix += 'double eabii2d(int a) { return (double)a; }\n'
            fix += 'void __gccmain() { }\n'
        elif self._decomp_arch == 'x86':
            if on_macos():
                fix += '#include <math.h>\n'

            fix += 'void ___main() { }\n'
            fix += 'double _modf(double a, double *b) { return modf(a, b); }\n'

        arch = self.out_config.json.get('architecture', {})
        if self._use_64_bit_compiler() and arch.get('bitSize') == 32:
            out_c = re.sub('int32_t', 'int64_t', out_c)
            fix += '\n// Following substition was applied: s/int32_t/int64_t/g\n'
        fix += '// ================= COMPILATION FIX END =================\n'

        self.decompiler.dir.store_file(
            self._fixed_out_c_file.name,
            fix + out_c
        )

    def _out_c_file_needs_to_be_fixed(self):
        """Checks if the output C file needs to be fixed."""
        return self._decomp_arch in ['arm', 'x86'] or self._use_64_bit_compiler()

    @property
    def _decomp_arch(self):
        """Architecture for which the input file was decompiled."""
        if self.settings.arch is not None:
            return self.settings.arch

        # The architecture is not explicitly specified in the settings, so we
        # have to obtain it from the config. This is usually the
        # case when the input file is a binary file and the writer of the test
        # did not specify the architecture.
        return self._get_arch_from_out_config()

    def _get_arch_from_out_config(self):
        arch = self.out_config.json.get('architecture', {}).get('name')
        if arch is None:
            return None

        return arch.lower()

    def _run_compiled_output_file(self, input, timeout):
        """Runs the compiled output C file with the given input and timeout and
        returns the output and return code.
        """
        return self._run_file(self._compiled_out_c_file, input, timeout)

    def _run_file(self, file, input, timeout):
        """Runs the given file with the given input and timeout. """
        output, return_code, timeouted = self.decompiler._run_cmd(
            [file.path], input, timeout)
        self._verify_not_timeouted(
            "run of file '{}'".format(file.path),
            timeouted,
            timeout
        )
        return output, return_code

    def _verify_ended_successfully(self, what, return_code, output):
        """Verifies that the given command ended successfully."""
        if return_code != 0:
            # Use "" instead of '' because what may contain '.
            raise AssertionError(
                "{} failed with return code {}; output:\n{}".format(
                    what, return_code, output
                )
            )

    def _verify_not_timeouted(self, what, timeouted, timeout):
        """Verifies that the given command didn't timeouted."""
        if timeouted:
            # Use "" instead of '' because what may contain '.
            raise AssertionError(
                "{} timeouted (timeout: {} second{})".format(
                    what,
                    timeout,
                    's' if timeout != 1 else ''
                )
            )
