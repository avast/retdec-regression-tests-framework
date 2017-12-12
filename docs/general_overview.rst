.. currentmodule:: regression_tests

General Overview
================

This section contains a general overview of the directory structure for regression tests.

Basic Directory Structure
-------------------------

The *root directory* of all regression tests is ``retdec-regression-tests``. The tests are structured into subdirectories, where each test is formed by a single subdirectory. Such a subdirectory has to contain:

* A ``test.py`` file, which is a *test module* containing test classes, settings, and methods that check whether the test passes or fails. Basically, it represents test specification.
* *Inputs* for the test. These are usually binary files to be decompiled.

A sample test structure looks like this:

.. code-block:: text

    regression-tests/
    ├── bugs/
    │   └── invalid-function-name/
    │       ├── input.exe
    │       └── test.py
    ├── features/
    │   └── main-detection/
    │       ├── input.msvc.exe
    │       ├── input.gcc.elf
    │       └── test.py
    └── integration/
            ├── ack/
            │   ├── ack.exe
            │   └── test.py
            └── ackermann/
                ├── ackermann.exe
                └── test.py

Outputs from Decompilations
---------------------------

After you run the regression tests, outputs from decompilations are placed into subdirectories named ``outputs``. In this way, you can check them after the tests finish to see what exactly was generated. These subdirectories are created inside the corresponding test directory. For example, for ``retdec-regression-tests/integration/ack``, the outputs are placed into ``retdec-regression-tests/integration/ack/outputs``.

To differentiate between the outputs of different decompilations, the outputs from each decompilation are placed into a properly named directory. The name is based on the parameters that were passed to the ``decompile.sh`` script when the test ran.

For example, a directory with outputs for the ``factorial`` test may contain the following subdirectories and files:

.. code-block:: text

    regression-tests/integration/factorial/outputs/
    ├── Test_2017 (factorial.x86.gcc.O0.exe)/
    │   ├── factorial.x86.gcc.O0.c
    │   ├── factorial.x86.gcc.O0.c-compiled
    │   ├── factorial.x86.gcc.O0.c.backend.bc
    │   ├── factorial.x86.gcc.O0.c.backend.ll
    │   ├── factorial.x86.gcc.O0.c.fixed.c
    │   ├── factorial.x86.gcc.O0.c.frontend.dsm
    │   ├── factorial.x86.gcc.O0.c.json
    │   └── factorial.x86.gcc.O0.c.log
    ├── ...
    └── Test_2017 (factorial.x86.clang.O0.exe)/
        ├── factorial.x86.clang.O0.c
        ├── factorial.x86.clang.O0.c-compiled
        ├── factorial.x86.clang.O0.c.backend.bc
        ├── factorial.x86.clang.O0.c.backend.ll
        ├── factorial.x86.clang.O0.c.fixed.c
        ├── factorial.x86.clang.O0.c.frontend.dsm
        ├── factorial.x86.clang.O0.c.json
        └── factorial.x86.clang.O0.c.log

Naming Conventions
------------------

Directory names can contain characters that are valid on common file systems, **except a dot** (``.``). The reason for not allowing a dot is that it is internally used to separate subdirectories in module names. Python uses a dot to separate namespaces, anyway. Examples:

.. code-block:: python

    features               # OK
    cool_backend_feature1  # OK
    cool-backend-feature2  # OK

    cool.backend.feature1  # WRONG: A dot '.' is not allowed by the regression tests framework.
    cool/backend/feature1  # WRONG: A slash '/' is not allowed in a directory name on Linux.
    cool|backend*feature1  # WRONG: Characters '|' and '*' are not allowed on Windows.

The naming of functions, classes, methods, and variables inside ``test.py`` files follows standard Python conventions, defined in `PEP8 <http://legacy.python.org/dev/peps/pep-0008/>`_. Example:

.. code-block:: python

    def my_function():
        my_var = [1, 2, 3]

    class MyClass(BaseClass):
        def do_something(self):
            ...

        def do_something_else(self):
            ...

Summary
-------

To summarize, a *test* is a subdirectory that is arbitrarily nested inside the root directory and contains a ``test.py`` file and input files. After the tests are run, the output files are placed into a corresponding ``outputs`` directory. For every decompilation, the outputs are placed into a separate subdirectory.

Next, we will learn how to create a new test.
