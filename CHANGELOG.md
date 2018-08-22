# Changelog

2018-08-22: Fix: Add a missing setup of Clang bindings to `parse_c_file.py`.
2018-08-17: Fix: Correctly terminate all subprocesses upon receiving SIGINT (Ctrl-C) or SIGTERM.
2018-08-01: Change: Use Python scripts instead of shell scripts to run our tools. This change corresponds to the recent migration from shell scripts to Python scripts in RetDec ([#338](https://github.com/avast-tl/retdec/pull/338)).
2018-06-10: Fix: Prioritize our packages in `deps/` over system-level packages ([#5](https://github.com/avast-tl/retdec-regression-tests-framework/issues/5)).
2018-05-30: Fix: Make `runner.py` exit with return code `1` when any of the tests fails.
2018-03-31: Fix: Fixed the obtaining of path to `libclang` on macOS. Now, regression tests can be also run from macOS.
2018-02-16: Change: Removed support for setting file format in decompilations. This change corresponds to the recent removal of the `-f/--format` parameter from `retdec-decompiler.sh`.
2018-01-11: Change: Renamed tools to match their names after recent changes in the [retdec](https://github.com/avast-tl/retdec) repository. For example, instead of `decompile.sh`, there is `retdec-decompiler.sh`.
2018-01-07: Enhancement: `runner.py` can now be run from any directory, no just from within the framework's root directory ([#3](https://github.com/avast-tl/retdec-regression-tests-framework/pull/3)).
2018-01-06: Enhancement: Added version numbers for dependencies in `requirements.txt` ([#2](https://github.com/avast-tl/retdec-regression-tests-framework/pull/2)).
2018-01-06: Fix: Added a missing dependency `nose-timer` into `requirements.txt` ([#1](https://github.com/avast-tl/retdec-regression-tests-framework/pull/1)).
2017-12-24: Change: Renamed the `retdec_installed_dir` configuration variable to `retdec_install_dir`.
