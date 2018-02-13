.. currentmodule:: regression_tests

Creating a New Test
===================

This section describes a way of creating new regression tests.

Basics
------

To create a new test, perform the following steps:

1. Create a new subdirectory inside the root directory. Example:

.. code-block:: text

    regression-tests
    └── integration
        └── ack

The naming conventions are described in :doc:`general_overview`.

2. Create a ``test.py`` file inside that directory. Example:

.. code-block:: text

    regression-tests
    └── integration
        └── ack
            └── test.py

The structure of this file is described later.

3. Add all the necessary input files to the created directory. Example:

.. code-block:: text

    regression-tests
    └── integration
        └── ack
            ├── ack.exe
            └── test.py

General Structure of test.py Files
----------------------------------

A ``test.py`` file has the following structure:

.. code-block:: python

    from regression_tests import *

    # Test class 1
    # Test class 2
    # ...

The first line imports all the needed class names from the :mod:`regression_tests` package. You can import them explicitly if you want, but the ``import *`` is just fine in our case [#import-star-fn]_. More specifically, it automatically imports the following classes, discussed later in this documentation:

* :class:`Test`
* :class:`TestSettings`
* :class:`CriticalTestSettings`

Also, other useful functions are automatically imported, which we will use later.

Every test class is of the following form:

.. code-block:: python

    class TestName(Test):
        # Settings 1
        # Settings 2
        # ...

        # Test method 1
        # Test method 2
        # ...

The name of a class can be any valid Python identifier, written by convention in ``CamelCase``. Furthermore, it has to inherit from :class:`Test`, which represents the base class of all tests. Example:

.. code-block:: python

    class AckTest(Test):
        # ...

Every test setting is of the following form:

.. code-block:: python

    settings_name = TestSettings(
        # Decompilation arguments.
        # ...
    )

The arguments specify the input file(s), architecture(s), file format(s), and other settings to be used in the test cases. Instead of class :class:`TestSettings`, you can also use :class:`CriticalTestSettings`. See our wiki for more details on the difference between regular and critical tests. Example:

.. code-block:: python

    settings = TestSettings(
        input='ack.exe'
    )

Finally, there have to be some test methods to check that the decompiled code satisfies the needed properties. Every test method is of the following form:

.. code-block:: python

    def test_description_of_the_test(self):
        # Assertions
        # ...

A method has to start with the prefix ``test_`` and its name should contain a description of what exactly is this method testing. This is a usual convention among unit test frameworks. The reason is that when a test fails, its method name reveals the purpose of the test.

The assertions can be ``assert`` statements, assertions from the standard `unittest <https://docs.python.org/3/library/unittest.html#module-unittest>`_ module (``self.assertXYZ()``), or specific assertions provided by the classes of the regression tests framework. Example:

.. code-block:: python

    def test_ack_has_correct_signature(self):
        # The following statements assert that in the decompiled C code, there
        # is an ack() function, its return type is int, and that it has two
        # parameters of type int.
        self.assertTrue(self.out_c.funcs['ack'].return_type.is_int(32))
        self.assertEqual(self.out_c.funcs['ack'].param_count, 2)
        self.assertTrue(self.out_c.funcs['ack'].params[0].type.is_int(32))
        self.assertTrue(self.out_c.funcs['ack'].params[1].type.is_int(32))

The above example uses assertions from the standard `unittest <https://docs.python.org/3/library/unittest.html#module-unittest>`_ module [#unittest-camel-case-fn]_.

See section :doc:`test_methods` for more details on how to write test methods and assertions.

Example of a test.py File
-------------------------

The following code is a complete example of a ``test.py`` file:

.. code-block:: python

    from regression_tests import *

    class AckTest(Test):
        settings = TestSettings(
            input='ack.exe'
        )

        def test_ack_has_correct_signature(self):
            # The following statements assert that in the decompiled C code,
            # there is an ack() function, its return type is int, and that it
            # has two parameters of type int.
            self.assertTrue(self.out_c.funcs['ack'].return_type.is_int(32))
            self.assertEqual(self.out_c.funcs['ack'].param_count, 2)
            self.assertTrue(self.out_c.funcs['ack'].params[0].type.is_int(32))
            self.assertTrue(self.out_c.funcs['ack'].params[1].type.is_int(32))

Next, we will learn the details of specifying test settings.

.. [#import-star-fn] Do not use the construct ``import *`` in real-world projects though because of namespace pollution and `other reasons <http://stackoverflow.com/a/2386740>`_.
.. [#unittest-camel-case-fn] The assertions in the standard `unittest <https://docs.python.org/3/library/unittest.html#module-unittest>`_ module are historically named by using ``CamelCase`` instead of ``snake_case``.
