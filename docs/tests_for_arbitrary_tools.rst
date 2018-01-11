.. currentmodule:: regression_tests

Tests for Arbitrary Tools
=========================

By default, when you specify test settings (see :doc:`test_settings`), the tested tool is ``decompiler``. Sometimes, however, it may be desirable to directly test other tools, such as ``fileinfo`` or ``unpacker``, without the need to run a complete decompilation. This section describes how to write tests for tools other than the decompiler.

It is assumed that you have read all the previous sections. That is, to understand the present section, you need to know how to write tests and specify test settings for decompilations.

Specifying the Tool
-------------------

To specify a tool that differs from the decompiler, use the ``tool`` parameter of :class:`TestSettings`. For example, the next settings specify that ``fileinfo`` should be run with the given input file:

.. code-block:: python

    settings = TestSettings(
        tool='fileinfo',
        input='file.exe'
    )

You can use any tool that is present in the RetDec's installation directory. For example, the following test settings prescribe to run all unit tests through the ``run-unit-tests.sh`` script:

.. code-block:: python

    settings = TestSettings(
        tool='run-unit-tests.sh'
    )

Since this script does not take any inputs, the ``input`` parameter is omitted.

.. note::

    If you do not explicitly specify a tool, ``decompiler`` is used. That is, the following two settings are equivalent:

    .. code-block:: python

        settings1 = TestSettings(
            tool='decompiler',
            input='file.exe'
        )

        settings2 = TestSettings(
            input='file.exe'
        )

Passing Parameters
------------------

As you have already learned, to specify the input file(s), use the ``input`` parameter of :class:`TestSettings`. Remember that you can pass multiple input files at once:

.. code-block:: python

    settings = TestSettings(
        tool='fileinfo',
        input=['file1.exe', 'file2.exe', 'file3.exe']
    )

When you do this, the tool is run separately for each of the input files.

Other parameters may be specified through the ``args`` parameter as a space-separated string. For example, to run ``fileinfo`` with two additional parameters ``--json`` and ``--verbose``, use the following settings:

.. code-block:: python

    settings = TestSettings(
        tool='fileinfo',
        input='file.exe',
        args='--json --verbose'
    )

.. warning::

    You cannot specify parameters containing input or output files in this way (e.g. ``-o file.out``). If you need to specify such parameters to test your tool, contact us.

    Currently, the only supported tools with output files are ``fileinfo`` and ``unpacker``. For them, the ``-c`` parameter (for ``fileinfo``) or the ``-o`` parameter (for ``unpacker``) are appended automatically by the regression-tests framework.

Obtaining Outputs and Writing Tests
-----------------------------------

As with tests for the decompiler, your tool is automatically run and the outputs are made available to you. To access them from your tests, use ``self.$TOOL.$WHAT``. For example, for ``fileinfo`` tests, use ``self.fileinfo.return_code`` to get the return code or ``self.fileinfo.output`` to access the output.

For every tool, the following attributes are available:

* ``self.$TOOL.return_code``: Return (exit) code from the tool (``int``).
* ``self.$TOOL.timeouted``: Has the tool timeouted (``bool``)?
* ``self.$TOOL.output``: Output from the tool (:class:`~parsers.text_parser.Text`). It is a combined output from the standard and error outputs.

If your tool name includes characters out of ``[a-zA-Z0-9_]``, all such characters are replaced with underscores. For example, for ``run-unit-tests.sh``, you would use ``self.run_unit_tests_sh.return_code`` to get its return code.

.. hint::

    This may be cumbersome to type, so for every tool, you can use the ``self.tool.$WHAT`` alias to access the particular output. That is, the following two types of access are equivalent:

    .. code-block:: python

        assert self.run_unit_tests_sh.return_code == 0
        assert self.tool.return_code == 0

    The ``self.tool`` alias is available for all tools.

Testing Success or Failure
--------------------------

Instead of checking the return code to verify success or failure, you can use the ``succeeded`` or ``failed`` attributes. For example, to verify that ``fileinfo`` ended successfully, use

    .. code-block:: python

        assert self.fileinfo.succeeded

To check that ``fileinfo`` failed, use

    .. code-block:: python

        assert self.fileinfo.failed

This makes tests more readable.

Tools with Extra Support
------------------------

The regression-tests framework provides extra support for some tools. Such support may include additional test-settings parameters or attributes that can be used in tests. This section describes these tools. If you need additional support for your particular tool, contact us.

Fileinfo
^^^^^^^^

* The output from ``fileinfo`` is parsed to provide easier access. See the description of :class:`~parsers.fileinfo_output_parser.FileinfoOutput` for more details.
* Even though the tool's name is ``fileinfo``, the tool is internally run via ``retdec-fileinfo.sh``. It is a shell script that wraps ``retdec-fileinfo`` and allows passing additional parameters. See its source code for more details.

IDA Plugin
^^^^^^^^^^

* The tool's name is ``idaplugin``. Internally, the tool is run via the ``run-ida-decompilation.sh`` script.
* The input IDA database file can be specified via the ``idb`` parameter when creating test settings.
* The output C file can be accessed just like in decompilation tests: via ``self.out_c``. All C checks are available (e.g. you can check that only the given function was decompiled).

Unpacker
^^^^^^^^

* The ``self.unpacker.succeeded`` attribute checks not only that the return code is zero but also the existence of the unpacked file.
* It is possible to run ``fileinfo`` after unpacking. Just use the following parameter when constructing test settings: ``run_fileinfo=True``. By default, ``fileinfo`` produces verbose output in the JSON format. For a complete list of supported ``fileinfo``-related parameters, see the description of :class:`~tools.unpacker_test_settings.UnpackerTestSettings`. You may then access the ``fileinfo`` run by accessing ``self.fileinfo`` (e.g. ``self.fileinfo.output`` gives you access to the parsed output).

Examples
--------

Finally, we can take a look on some examples.

Bin2Pat
^^^^^^^

* The output YARA file generated by ``bin2pat`` is parsed to provide easier access to the YARA rules. See the description of :class:`~parsers.yara_parser.Yara` for more details.

Fileinfo
^^^^^^^^

Regular ``fileinfo`` test.

.. code-block:: python

    class FileinfoTest(Test):
        settings = TestSettings(
            tool='fileinfo',
            input='sample.exe',
            args='--json' # JSON output is easier to parse than the default plain output.
        )

        def test_correctly_analyzes_input_file(self):
            assert self.fileinfo.succeeded

            self.assertEqual(self.fileinfo.output['architecture'], 'x86')
            self.assertEqual(self.fileinfo.output['fileFormat'], 'PE')
            self.assertEqual(self.fileinfo.output['fileClass'], '32-bit')

            self.assertTrue(self.fileinfo.output['tools'][0]['name'].startswith('GCC'))

Verbose ``fileinfo`` with ``loader_info`` used.

.. code-block:: python

    class FileinfoTest(Test):
        settings = TestSettings(
            tool='fileinfo',
            args='-v',
            input='sample.exe'
        )

        def test_correctly_analyzes_input_file(self):
            assert self.fileinfo.succeeded

            self.assertEqual(self.fileinfo.output.loader_info.base_address, 0x400000)
            self.assertEqual(self.fileinfo.output.loader_info.loaded_segments_count, 2)

            self.assertEqual(self.fileinfo.output.loader_info.segments[0].name, '.text')
            self.assertEqual(self.fileinfo.output.loader_info.segments[0].address, 0x401000)
            self.assertEqual(self.fileinfo.output.loader_info.segments[0].size, 0x500)
            self.assertEqual(self.fileinfo.output.loader_info.segments[1].name, '.data')

IDA Plugin
^^^^^^^^^^

.. code-block:: python

    class IDAPluginTest(Test):
        settings = TestSettings(
            tool='idaplugin',
            input='sample.exe',
            idb='sample.idb',
            args='--select 0x1000' # main
        )

        # Success is checked automatically (you do not have to check it manually).

        def test_correctly_decompiles_main(self):
            assert self.out_c.has_func('main')

Unpacker
^^^^^^^^

.. code-block:: python

    class UnpackerTest(Test):
        settings = TestSettings(
            tool='unpacker',
            input='mpress.exe'
        )

        def test_correctly_unpacks_input_file(self):
            assert self.unpacker.succeeded

.. code-block:: python

    class UnpackerTest(Test):
        settings = TestSettings(
            tool='unpacker',
            input='upx.exe',
            run_fileinfo=True # Run fileinfo afterwards so we can check section names.
        )

        def test_unpacked_file_has_correct_section_names(self):
            assert self.unpacker.succeeded
            sections = self.fileinfo.output['sectionTable']['sections']
            self.assertEqual(len(sections), 4)
            self.assertEqual(sections[0]['name'], '.text')
            self.assertEqual(sections[1]['name'], '.rdata')
            self.assertEqual(sections[2]['name'], '.data')
            self.assertEqual(sections[3]['name'], '.reloc')

The next, last section concludes this documentation.
