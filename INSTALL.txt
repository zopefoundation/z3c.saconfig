Installation
************

Introduction
============

Normally this code would be set up an as egg. If you want help with
development, you can install it as a buildout.

Installation
============

This package can be checked out from
svn://svn.zope.org/repos/main/z3c.saconfig/trunk. You can then execute
the buildout to download and install the requirements and install the
test runner. Using your desired python run::

  $ python bootstrap.py

If installation configuration changes later, you need to run::

  $ bin/buildout

Running the tests
=================

After running the buildout, you can run the test script like this::

  $ bin/test

By default, the tests are run against an in-memory SQLite database.

To enable testing with your own database set the ``TEST_DSN`` and
``TEST_DSN2`` environment variables to your sqlalchemy database dsn::

  $ export TEST_DSN=postgres://test:test@localhost/test
 
Since the tests also need access to a second, independent database,
you also need to define a TEST_DSN2 that points to a different
database::

  $ export TEST_DSN2=postgres://test:test@localhost/test2

Two-phase commit behaviour may be tested by setting the TEST_TWOPHASE
variable to a non empty string. e.g::

  $ export TEST_TWOPHASE=True bin/test
