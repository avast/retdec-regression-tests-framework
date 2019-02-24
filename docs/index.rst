.. Regression Tests documentation master file, created by
   sphinx-quickstart on Tue Aug 19 08:56:12 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Regression Tests' Documentation!
===========================================

This is a documentation for the `regression tests framework <https://github.com/avast-tl/retdec-regression-tests-framework/>`_. It describes how to write regression tests for `RetDec <https://github.com/avast-tl/retdec/>`_ and its tools, and provides an overview of the supported functions and methods.

The documentation is primarily focused on tests for the RetDec decompiler, i.e. for the ``retdec-decompiler.py`` script. You can, however, write tests for arbitrary RetDec-related tools, such as ``fileinfo`` or ``unpacker``. This is described in section :doc:`tests_for_arbitrary_tools`. Nevertheless, it is highly recommended to read the whole documentation, even if you plan to write tests only for a single tool.

Table of Contents
=================

.. toctree::
   :maxdepth: 2

   general_overview
   tests
   test_settings
   test_methods
   tests_for_arbitrary_tools
   support_and_feedback

Indices
=======

* :ref:`genindex`
* :ref:`modindex`
