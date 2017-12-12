.. Regression Tests documentation master file, created by
   sphinx-quickstart on Tue Aug 19 08:56:12 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Regression Tests' Documentation!
===========================================

This is an API documentation for the regression tests framework. It describes ways of writing regression tests and provides an overview of the supported functions and methods.

It is assumed that you have read the general documentation on our wiki. If you have not, please read it first and come back after that. This API documentation will make more sense. Trust me :).

The documentation is primarily focused on tests for decompilations, i.e. for the ``decompile.sh`` script. You can, however, write tests for arbitrary tools. This is described in section :doc:`tests_for_arbitrary_tools`. Nevertheless, it is highly recommended to read the whole documentation, even if you plan to write tests only for a single tool.

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
