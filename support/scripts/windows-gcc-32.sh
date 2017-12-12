#!/bin/sh
#
# A wrapper around GCC for 32b compilation on Windows.
#
# Since MSYS2 does not support multilib, we have to use our custom
# wrapper around gcc that properly handles the -m32 parameter.
#

PATH="/mingw32/bin/:$PATH" /mingw32/bin/gcc "$@"
