#!/bin/sh
#
# A wrapper around GCC for 64b compilation on Windows.
#
# Since MSYS2 does not support multilib, we have to use our custom
# wrapper around gcc that properly handles the -m64 parameter.
#

PATH="/mingw64/bin/:$PATH" /mingw64/bin/gcc "$@"
