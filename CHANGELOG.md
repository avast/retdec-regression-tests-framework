# Changelog

* 2020-04-08: Change: Removed support for the following features that are no longer useful: storing results into a database, showing results on the web, sending email notifications, building of RetDec, resuming tests run, testing a specific commit.
* 2019-09-04: Enhancement: Add support for skipping tests that compile output C files (either via config or via the `--skip-c-compilation-tests` parameter of `runner.py`).
* 2019-03-11: Change: Removed mention of 32-bit Windows (it is no longer supported). Added a new requirement for Windows: 64-bit GCC compiler (package `mingw-w64-x86_64-gcc`).
* 2018-10-14: Change: Removed distinguishing of critical and non-critical tests. Now, there is only a single type of tests (called "non-critical" in the original parlance).
* 2018-10-14: Change: Removed support for running tests via a custom daemon. We no longer need this piece of functionality as we run tests via TeamCity.
* 2018-10-05: Fix: Fixed parsing of pointers to functions having unspecified number of parameters.
* 2018-10-05: Enhancement: Added support for parsing C source code containing parenthesized expressions.
* 2018-08-31: Enhancement: Added support for compiling decompiled C source code via 64b GCC. This will be needed to test 64b decompilations (work in progress).
* 2018-08-23: Enhancement: Provide `on_linux()`, `on_macos()`, and `on_windows()` to regression tests so that some checks can be performed only on a specific platform.
* 2018-08-22: Enhancement: Unified names of called functions in our C parser due to the presence of builtins. For example, `__builtin___memset_chk()` is now recognized as `memset()` when checking function calls.
* 2018-08-22: Fix: Added a missing setup of Clang bindings to `parse_c_file.py`.
* 2018-08-17: Fix: Correctly terminate all subprocesses upon receiving SIGINT (Ctrl-C) or SIGTERM.
* 2018-08-01: Change: Use Python scripts instead of shell scripts to run our tools. This change corresponds to the recent migration from shell scripts to Python scripts in RetDec ([#338](https://github.com/avast/retdec/pull/338)).
* 2018-06-10: Fix: Prioritize our packages in `deps/` over system-level packages ([#5](https://github.com/avast/retdec-regression-tests-framework/issues/5)).
* 2018-05-30: Fix: Make `runner.py` exit with return code `1` when any of the tests fails.
* 2018-03-31: Fix: Fixed the obtaining of path to `libclang` on macOS. Now, regression tests can be also run from macOS.
* 2018-02-16: Change: Removed support for setting file format in decompilations. This change corresponds to the recent removal of the `-f/--format` parameter from `retdec-decompiler.sh`.
* 2018-01-11: Change: Renamed tools to match their names after recent changes in the [retdec](https://github.com/avast/retdec) repository. For example, instead of `decompile.sh`, there is `retdec-decompiler.sh`.
* 2018-01-07: Enhancement: `runner.py` can now be run from any directory, no just from within the framework's root directory ([#3](https://github.com/avast/retdec-regression-tests-framework/pull/3)).
* 2018-01-06: Enhancement: Added version numbers for dependencies in `requirements.txt` ([#2](https://github.com/avast/retdec-regression-tests-framework/pull/2)).
* 2018-01-06: Fix: Added a missing dependency `nose-timer` into `requirements.txt` ([#1](https://github.com/avast/retdec-regression-tests-framework/pull/1)).
* 2017-12-24: Change: Renamed the `retdec_installed_dir` configuration variable to `retdec_install_dir`.
