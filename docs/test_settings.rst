.. currentmodule:: regression_tests

Specifying Test Settings
========================

This section gives a detailed description of how to specify settings for regression tests. It also describes the relation of test settings to test cases.

Basics
------

Test settings are specified as class attributes inside test classes, described in section :doc:`tests`. The general form is

.. code-block:: python

    settings_name = SettingsClass(
        arg1=value1,
        arg2=value2,
        # ...
    )

The name can by any valid Python identifier, written conventionally in ``snake_case``. The used class can be either :class:`TestSettings` or its subclass :class:`CriticalTestSettings`. Test cases that use the first class are *regular tests* whereas test cases that use the second class are so-called *critical tests*. The difference between those two is described our our wiki.

The arguments and values specified in the initializer of the used settings class define the parameters to be used for decompilations. For example, you may specify the input file or the used architecture. The selected arguments and values are then used to create arguments for the decompiler. For example, the following settings specify the input file and prescribe the use of the ``x86`` architecture:

.. code-block:: python

    settings = TestSettings(
        input='file.exe',
        arch='x86'
    )

From the above settings, the following ``retdec_decompiler.py`` argument list is automatically created:

.. code-block:: text

    retdec_decompiler.py file.exe -a x86

For a complete list of possible arguments to the initializer, see the description of :class:`~tools.decompiler_test_settings.DecompilerTestSettings`.

Every argument can be either a single value or a list of values. When you specify a single value, it will be used for all decompilations. However, if you specify multiple values, a separate decompilation is run for all of them. For example, consider the following test settings:

.. code-block:: python

    settings = TestSettings(
        input='file.exe',
        arch=['x86', 'arm']
    )

For such settings, the following two decompilations are run:

.. code-block:: text

    retdec_decompiler.py file.exe -a x86
    retdec_decompiler.py file.exe -a arm

That is, the regression tests framework runs a single decompilation for every combination of the values specified in the settings.

Test Cases and Their Creation
-----------------------------

A *test case* is an instance of your test class with an associated decompilation. Recall that a test class is a class that inherits from :class:`Test` (see section :doc:`tests`). As described above, when you specify settings with some arguments having multiple values (e.g. several architectures), a separate decompilation is run for all of them. For every decompilation, a test case is created, and all its test methods are called.

For example, consider the following test:

.. code-block:: python

    class Sample(Test)
        settings = TestSettings(
            input='file.exe',
            arch=['x86', 'arm']
        )

        def test_something1(self):
            # ...

        def test_something2(self):
            # ...

For this test, the following two test cases are created:

.. code-block:: text

    Sample (file.exe -a x86)
    Sample (file.exe -a arm)

The two test methods are then called on each of them:

.. code-block:: text

    Sample (file.exe -a x86)
        test_something1()
        test_something2()
    Sample (file.exe -a arm)
        test_something1()
        test_something2()

Classes Having Multiple Settings
--------------------------------

You may specify several settings in a test class. This is handy when you want to use different settings for some decompilations. For example, consider the following class:

.. code-block:: python

    class Sample(Test)
        settings1 = TestSettings(
            input='file1.exe',
            arch=['x86', 'arm']
        )
        settings2 = TestSettings(
            input='file2.elf',
            arch='thumb'
        )

        # Test methods...

We want to decompile ``file1.exe`` on ``x86`` and ``arm``, and ``file2.elf`` on ``thumb``. From this test class, the following three test cases are created:

.. code-block:: text

    Sample (file1.exe -a x86)
    Sample (file1.exe -a arm)
    Sample (file2.elf -a thumb)

Arbitrary Parameters for the Decompiler
---------------------------------------

If you look at the complete list of possible arguments (:class:`~tools.decompiler_test_settings.DecompilerTestSettings`), you see that not all ``retdec_decompiler.py`` parameters may be specified as arguments to :class:`TestSettings`. The reason is that ``retdec_decompiler.py`` provides too many parameters and their support in the form of arguments would be cumbersome. However, it is possible to specify arbitrary arguments that are directly passed to the ``retdec_decompiler.py`` script via the ``args`` argument:

.. code-block:: python

    class Sample(Test):
        settings = TestSettings(
            input='file.exe'
            arch='x86',
            args='--select-decode-only --select-functions func1,func2'
        )

These settings result into the creation of the following decompilation:

.. code-block:: text

    retdec_decompiler.py file.exe -a x86 --select-decode-only --select-functions func1,func2

In a greater detail, the ``args`` argument is taken, split into sub-arguments by whitespace, and passed to the ``retdec_decompiler.py`` script. The argument list internally looks like this:

.. code-block:: python

    ['file.exe', '-a', 'x86', '--select-decode-only', '--select-functions', 'func1,func2']

.. hint::

    When it is possible to specify a ``retdec_decompiler.py`` parameter in the form of a named argument (like architecture or endianness), always prefer it to specifying raw arguments by using the ``args`` argument. That is, do **not** write

    .. code-block:: python

        class Sample(Test):
            settings = TestSettings(
                input='file.exe'
                args='-a x86'   # Always prefer using arch='x86'.
            )

    The reason is that named arguments are less prone to changes in ``retdec_decompiler.py``. Indeed, when such an argument changes in ``retdec_decompiler.py``, all that has to be done is changing the internal mapping of named arguments to ``retdec_decompiler.py`` arguments. No test needs to be changed.

If you want to specify separate arguments for several decompilations for single settings, place them into a list when specifying the settings. For example, consider the following test class:

.. code-block:: python

    class Sample(Test):
        settings = TestSettings(
            input='file.elf'
            arch='x86',
            args=[
                '--select-decode-only --select-functions func1,func2',
                '--select-decode-only --select-functions func3'
            ]
        )

It results into these two decompilations:

.. code-block:: text

    retdec_decompiler.py file.elf -a x86 --select-decode-only --select-functions func1,func2
    retdec_decompiler.py file.elf -a x86 --select-decode-only --select-functions func3

You can also specify multiple settings, as already described earlier in this section.

Specifying Input Files From Directory
-------------------------------------

When there is a lot of input files, the directory structure may become less readable (the ``test.py`` file is buried among input files). In a situation like this, you may put the input files into a directory (e.g. ``input``) and use :func:`~regression_tests.test_utils.files_in_dir()` to automatically generate a list of files in this directory:

.. code-block:: python

    settings = TestSettings(
        input=files_in_dir('inputs')
    )

You can also specify which files should be included or excluded:

.. code-block:: python

    settings = TestSettings(
        input=files_in_dir('inputs', matching=r'.*\.exe', excluding=['problem-file.exe'])
    )
