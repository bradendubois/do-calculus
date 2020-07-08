## Further Documentation

The directory ``documentation`` contains more expansive documentation on various components of using / adding to / modifying the software.

### Graph Files

By default, there are a few files in ``causal_graphs``; any of these can be loaded, and graphs can be easily created, and placed in the same directory to be loaded by the software.

For information on creating graphs, see ``Causal Graph Files``.

### Configuration Settings

A default configuration file is generated the first time the software is run (if there is not already one). All the settings can be modified; options include directories to search, what to log or output, accuracy / formatting rules, etc.

For information on configuration settings, their usage and options, see ``Configuration``.

### Regression Tests

A regression test suite is implemented in the software, and by default, is run at launch. Any number of test files can be created, and by default are located in ``regression_tests/test_files``. They allow for various kinds of tests, including simply checking that probability calculated matches an expected, whether some set of tests sum to some value, and a couple more.

For information on creating test files, see ``Regression Tests``.

### Decorator Usage

Decorators are an advanced Python concept relying on its functional programming; it is not heavily used yet in this software.

For information on decorators, see ``Decorator Usage``.

### Source Code Design / Architecture

An effort has been made to document source code consistently and clearly. As well, an emphasis has been made to write *clear*, *readable*, and *robust* code.

For information the overall architecture / design, see ``Architecture``.
