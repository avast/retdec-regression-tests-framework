.. currentmodule:: regression_tests

Writing Test Methods
====================

This section gives a description of how to write test methods. It also presents a brief overview of the available assertions.

Basics
------

Test methods are written in the same way as unit tests with the standard `unittest <https://docs.python.org/3/library/unittest.html#module-unittest>`_ module. Moreover, the base class for all tests, :class:`Test`, inherits from `unittest.TestCase <https://docs.python.org/3/library/unittest.html?highlight=unittest.testcase#unittest.TestCase>`_. Therefore, you can use anything that is available in the ``unittest`` module, including assertion methods.

Every test method has to be begin with suffix ``test``. Examples:

.. code-block:: python

    def test_something(self):
        # ...

    def test_something_else(self):
        # ...

Its name should contain a description of what exactly is this method testing. This is the usual convention among unit test frameworks. The reason is that when a test fails, its method name reveals the purpose of the test.

Inside test methods, you can write your assertions about the decompiled code, or even about the decompilation itself. To write an assertion, you can either use the standard ``assert`` statement from Python, or you can use the `assertions from the unittest module <https://docs.python.org/3/library/unittest.html?highlight=unittest#assert-methods>`_. For example, the following two assertions are functionally equivalent:

.. code-block:: python

    def test_ack_has_proper_number_of_parameters(self):
        # Using the assert statement:
        assert self.out_c.funcs['ack'].param_count == 2
        # Using a method from the unittest module:
        self.assertEqual(self.out_c.funcs['ack'].param_count, 2)

.. hint::

    Even though both of these assertions are functionally equivalent, the assertions from the unittest module provide more useful output. For example, imagine that the decompiled function ``ack()`` has a different number of parameters than two. The first assertion fails with the following message:

    .. code-block:: text

        FAIL: test_ack_has_proper_number_of_parameters (integration.ack.Test)
        ----------------------------------------------------------------------
        Traceback (most recent call last):
        File "integration/ack/test.py", line 34, in test_ack_has_proper_number_of_parameters
            assert self.out_c.funcs['ack'].param_count == 2
        AssertionError

    In contrast, the second assertion fails with this message:

    .. code-block:: text

        FAIL: test_ack_has_proper_number_of_parameters (integration.ack.Test)
        ----------------------------------------------------------------------
        Traceback (most recent call last):
        File "integration/ack/test.py", line 36, in test_ack_has_proper_number_of_parameters
            self.assertEqual(self.out_c.funcs['ack'].param_count, 2)
        AssertionError: 3 != 2

    That is, you can see that the decompiled function has three parameters, but we were expecting two. Such a piece of information is not provided if you use the ``assert`` statement.

Automatically Performed Verifications
-------------------------------------

There are verifications that are performed automatically for every test case. Currently, there is only one such verification:

* The decompilation succeeded, i.e. it did not fail or timeout.

When the above verification fails (e.g. the decompilation timeouted), the test is ended with a failure without even running the test methods. Therefore, you do not have to manually test that the decompilation was successful.

Sometimes, however, you expect the decompilation to fail. For example, when the input file format is unsupported and you want to verify that a proper error message is emitted. In such cases, you can disable the automatic verification in the following way:

.. code-block:: python

    class Test(Test):
        settings = TestSettings(
            input='mips-elf64'
        )

        def setUp(self):
            # Prevent the base class from checking that the decompilation
            # succeeded (we expect it to fail).
            pass

        def test_decompilation_fails_with_correct_error(self):
            assert self.decompiler.return_code == 1
            assert self.decompiler.log.contains(r"Error: Unsupported target format 'ELF64'.")

Accessing Decompilation and Outputs
-----------------------------------

The corresponding decompilation is available in the ``self.decompiler`` attribute, which is of type :class:`~tools.decompiler.Decompiler`. It provides access to the decompilation itself and to the produced files. Some of the available attributes are:

* ``self.decompiler.args`` - Arguments for the decompilation (:class:`~tools.decompiler_arguments.DecompilerArguments`).
* ``self.decompiler.return_code`` - Return code of the decompilation (``int``).
* ``self.decompiler.timeouted`` - Has the decompilation timeouted (``bool``)?
* ``self.decompiler.log`` - Full log from the decompilation (:class:`~parsers.text_parser.Text`).
* ``self.decompiler.fileinfo_output`` - Output from fileinfo (:class:`~parsers.fileinfo_output_parser.FileinfoOutput`).
* ``self.decompiler.fileinfo_outputs`` - A list of outputs from fileinfo (list of :class:`~parsers.fileinfo_output_parser.FileinfoOutput`). This is handy when fileinfo ran multiple times (e.g. when the input file is packed).
* ``self.decompiler.out_c`` - Output C (:class:`~parsers.c_parser.module.Module`).
* ``self.decompiler.out_dsm`` - Output DSM (:class:`~parsers.text_parser.Text`).
* ``self.decompiler.out_ll`` - Output LLVM IR (:class:`~parsers.text_parser.Text`).
* ``self.decompiler.out_config`` - Output configuration file (:class:`~parsers.config_parser.Config`).

For a complete list of attributes :class:`~tools.decompiler.Decompiler` provides, see its documentation.

.. hint::

    As a shortcut, the :class:`Test` class provides the following attributes:

    * ``self.out_c`` - Output C (alias to `self.decompiler.out_c`).
    * ``self.out_dsm`` - Output DSM (alias to `self.decompiler.out_dsm`).
    * ``self.out_ll`` - Output LLVM IR (alias to `self.decompiler.out_ll`).
    * ``self.out_config`` - Output configuration file (alias to `self.decompiler.out_config`).

    That is, you can write, e.g, ``self.out_c`` and ``self.out_dsm`` instead of ``self.decompiler.out_c`` and ``self.decompiler.out_dsm``.

Accessing Test Settings
-----------------------

The settings used for the particular decompilation can be accessed through ``self.settings``, which is of type :class:`TestSettings`. This allows you to write assertions that depend on the input settings. Example:

.. code-block:: python

    if '--select-functions' in self.settings.args:
        # Specific assertions for selective decompilation.
        # ...

Verifying Text Outputs
----------------------

Text outputs, like the decompilation log, output C, output LLVM IR, or output DSM, are instances of :class:`~parsers.text_parser.Text`. Instances of this class behave like strings and provide all the methods the standard ``str`` class provides (`documentation <https://docs.python.org/3/library/stdtypes.html?highlight=str#textseq>`_). Apart from them, however, it also contains a special method ``contains()`` that can be used to verify whether the output contains the given `regular expression <https://docs.python.org/3/library/re.html?highlight=re#module-re>`_. Example:

.. code-block:: python

    assert self.out_c.contains(r'printf\("%d", \S+ / 4\);')
    assert self.out_dsm.contains(r'; function: factorial')
    assert self.out_ll.contains(r'dec_label_pc_400010')
    assert self.decompiler.log.contains(r'# DONE')

Verifying C Outputs
-------------------

Every C output is a text output. This means that all the methods of :class:`~parsers.text_parser.Text` also work on C outputs. Nevertheless, C outputs, which are of class :class:`~parsers.c_parser.module.Module`, provide a far richer interface for verifying the correctness of the decompiled C file. Indeed, as we see shortly, you can check whether the decompiled C contains the given functions, number of parameters, includes, comments, etc.

Available Entities
^^^^^^^^^^^^^^^^^^

Class :class:`~parsers.c_parser.module.Module` provides access to the following entities:

* the source code as a string (``self.out_c``, which is a string-like object),
* global variables (:class:`~parsers.c_parser.exprs.variable.Variable`),
* functions (:class:`~parsers.c_parser.function.Function`),
* comments (:class:`~parsers.c_parser.comment.Comment`),
* includes (:class:`~parsers.c_parser.include.Include`),
* string literals (:class:`~parsers.c_parser.exprs.literals.string_literal.StringLiteral`),
* structures (:class:`~parsers.c_parser.types.struct_type.StructType`),
* unions (:class:`~parsers.c_parser.types.union_type.UnionType`),
* enumerations (:class:`~parsers.c_parser.types.enum_type.EnumType`).

Supported types:

* void (:class:`~parsers.c_parser.types.void_type.VoidType`),
* integral types (:class:`~parsers.c_parser.types.integral_type.IntegralType`), with subclasses :class:`~parsers.c_parser.types.int_type.IntType`, :class:`~parsers.c_parser.types.char_type.CharType`, and :class:`~parsers.c_parser.types.bool_type.BoolType`,
* floating-point types (:class:`~parsers.c_parser.types.floating_point_type.FloatingPointType`), with subclasses :class:`~parsers.c_parser.types.float_type.FloatType` and :class:`~parsers.c_parser.types.double_type.DoubleType`,
* pointers (:class:`~parsers.c_parser.types.pointer_type.PointerType`),
* arrays (:class:`~parsers.c_parser.types.array_type.ArrayType`),
* functions (:class:`~parsers.c_parser.types.function_type.FunctionType`),
* structures (:class:`~parsers.c_parser.types.struct_type.StructType`),
* unions (:class:`~parsers.c_parser.types.union_type.UnionType`),
* enumerations (:class:`~parsers.c_parser.types.enum_type.EnumType`).

Supported expressions:

* variables (:class:`~parsers.c_parser.exprs.variable.Variable`),
* literals (:class:`~parsers.c_parser.exprs.literals.literal.Literal`), with subclasses :class:`~parsers.c_parser.exprs.literals.integral_literal.IntegralLiteral`, :class:`~parsers.c_parser.exprs.literals.floating_point_literal.FloatingPointLiteral`, :class:`~parsers.c_parser.exprs.literals.character_literal.CharacterLiteral`, and :class:`~parsers.c_parser.exprs.literals.string_literal.StringLiteral`,
* unary operators (:class:`~parsers.c_parser.exprs.unary_ops.unary_op_expr.UnaryOpExpr`),
* binary operators (:class:`~parsers.c_parser.exprs.binary_ops.binary_op_expr.BinaryOpExpr`),
* ternary operator (:class:`~parsers.c_parser.exprs.ternary_op_expr.TernaryOpExpr`),
* casts (:class:`~parsers.c_parser.exprs.cast_expr.CastExpr`),
* function calls (:class:`~parsers.c_parser.exprs.call_expr.CallExpr`),
* initializer lists (:class:`~parsers.c_parser.exprs.init_list_expr.InitListExpr`).

Supported statements in function bodies:

* if (:class:`~parsers.c_parser.stmts.if_stmt.IfStmt`),
* switch (:class:`~parsers.c_parser.stmts.switch_stmt.SwitchStmt`),
* for loop (:class:`~parsers.c_parser.stmts.for_loop.ForLoop`),
* while loop (:class:`~parsers.c_parser.stmts.while_loop.WhileLoop`),
* do-while loop (:class:`~parsers.c_parser.stmts.do_while_loop.DoWhileLoop`),
* break (:class:`~parsers.c_parser.stmts.break_stmt.BreakStmt`),
* continue (:class:`~parsers.c_parser.stmts.continue_stmt.ContinueStmt`),
* return (:class:`~parsers.c_parser.stmts.return_stmt.ReturnStmt`),
* goto (:class:`~parsers.c_parser.stmts.goto_stmt.GotoStmt`),
* empty statement (:class:`~parsers.c_parser.stmts.empty_stmt.EmptyStmt`),
* variable definition and assignment (:class:`~parsers.c_parser.stmts.var_def_stmt.VarDefStmt`).

Verifying Configuration Files
-----------------------------

Every output configuration file (in the JSON format) is a text file, so just like C files, you can use all the methods of :class:`~parsers.text_parser.Text`. However, additional attributes and methods are provided to make the verification easier. See the documentation of :class:`~parsers.config_parser.Config` for more details.

Compiling and Running C Outputs
-------------------------------

To check that the generated C output is compilable, use :func:`Test.assert_out_c_is_compilable()`:

.. code-block:: python

    self.assert_out_c_is_compilable()

To check that the output C produces the expected output when compiled and run, use :func:`Test.assert_c_produces_output_when_run()`:

.. code-block:: python

    self.assert_c_produces_output_when_run('input text', 'expected output')

It compiles the output C file, runs it with the given input text, and verifies that the output matches.

.. hint::
    By default, the compiled file is run with a 5 seconds timeout. If this value is insufficient, you can increase it by specifying an explicit timeout:

    .. code-block:: python

        # Increase the timeout to 10 seconds.
        self.assert_c_produces_output_when_run('input text', 'expected output', timeout=10)

Running Code Only On Selected Platforms
---------------------------------------

Some checks should run only on specific platforms (e.g. a test works only on Linux and Windows but not on macOS). The framework provides the following three functions to check on which operating system the test is running:

* :func:`~utils.os.on_linux()`
* :func:`~utils.os.on_macos()`
* :func:`~utils.os.on_windows()`

Usage example:

.. code-block:: python

    if not on_macos():
        # This code will not be executed when running on macOS.
        # ...

There is no need to import anything (other than the usual `from regression_tests import *` at the top of a `test.py` file).

Examples
--------

This sections contains examples of real-world assertions that you can use in your tests.

Output C
^^^^^^^^

.. code-block:: python

    # Check that the output C is compilable.
    self.assert_out_c_is_compilable()

    # Check that the input and output C produce the same output
    # when compiled and run with the given inputs:
    self.assert_c_produces_output_when_run('0 0', 'ack(0, 0) = 1\n')
    self.assert_c_produces_output_when_run('1 1', 'ack(1, 1) = 3\n')

    # Check that there is at least one function.
    assert self.out_c.has_funcs()

    # Check that functions ack() and main() are present (possibly among other
    # functions).
    assert self.out_c.has_funcs('ack', 'main')

    # If there are many functions, prefer the following way of testing of their
    # presence. The reason is that when a function is missing, you immediately
    # know which one is it.
    assert self.out_c.has_func('ack')
    assert self.out_c.has_func('main')

    # You can also check that there is a function matching the given regular
    # expression. This is useful if the exact function name can differ between
    # platforms or compilers. For example, the name can be sometimes prefixed
    # with an underscore.
    assert self.out_c.has_func_matching(r'_?ack')

    # Check that there are only two functions: ack() and main().
    assert self.out_c.has_just_funcs('ack', 'main')

    # Check that ack() calls itself recursively.
    assert self.out_c.funcs['ack'].calls('ack')

    # Check that there are no global variables.
    assert self.out_c.has_no_global_vars()

    # Check that there is the given string literal.
    assert self.out_c.has_string_literal('Result is: %d');

    # Check that there is a comment with the number of detected functions, and
    # that the number of functions detected in the front-end matches the number
    # of functions detected by the back-end.
    assert self.out_c.has_comment_matching(r'.*Detected functions: (\d+) \(\1 in front-end\)')

    # Check that the following includes are present.
    assert self.out_c.has_include_of_file('stdio.h')
    assert self.out_c.has_include_of_file('stdint.h')

    # Check that main has correct return type, parameter names and types.
    assert self.out_c.funcs['main'].return_type.is_int()
    assert self.out_c.funcs['main'].params[0].type.is_int()
    self.assertEqual(self.out_c.funcs['main'].params[0].name, 'argc')
    assert self.out_c.funcs['main'].params[1].type.is_pointer()
    self.assertEqual(self.out_c.funcs['main'].params[1].name, 'argv')

    # Check that the ack() function has correct return type, parameter count,
    # and types.
    assert self.out_c.funcs['ack'].return_type.is_int(32)
    self.assertEqual(self.out_c.funcs['ack'].param_count, 2)
    assert self.out_c.funcs['ack'].params[0].type.is_int(32)
    assert self.out_c.funcs['ack'].params[1].type.is_int(32)

    # You can also use the following methods, which parse the given C type and
    # check the correspondence.
    assert self.out_c.funcs['ack'].params[1].type.is_same_as('int32_t')
    assert self.out_c.funcs['ack'].params[1].type.is_same_as('int')

Output DSM
^^^^^^^^^^

.. code-block:: python

    # Check that the output DSM contains the given comment.
    assert self.out_dsm.contains(r'; function: ack')

Output LLVM IR
^^^^^^^^^^^^^^

.. code-block:: python

    # Check that the output LLVM IR contains the given label.
    assert self.out_ll.contains(r'dec_label_pc_400010')

Output Config
^^^^^^^^^^^^^

.. code-block:: python

    # Check that 10 functions are present in the config by using the JSON
    # representation.
    self.assertEqual(len(self.out_config.json.functions), 10)

Decompilation
^^^^^^^^^^^^^

.. code-block:: python

    # Check that the log from the decompilation contains
    # the given front-end phase.
    assert self.decompiler.log.contains(r'Running phase: libgcc idioms optimization')

    # Check that the log from the decompilation contains
    # the given comment.
    assert self.decompiler.log.contains(r'# Done!')

In the next section, you will learn how to write tests for arbitrary tools, not just for the decompiler.
