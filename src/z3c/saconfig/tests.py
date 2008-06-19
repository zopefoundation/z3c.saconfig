# You may want to run the tests with your database. To do so set the
# environment variable TEST_DSN to the connection url. e.g.:
#
# export TEST_DSN=postgres://plone:plone@localhost/test
# export TEST_DSN=mssql://plone:plone@/test?dsn=mydsn
#
# To test in twophase commit mode export TEST_TWOPHASE=True 
#
# NOTE: The sqlite that ships with Mac OS X 10.4 is buggy.
# Install a newer version (3.5.6) and rebuild pysqlite2 against it.


import unittest
import doctest
import os

from zope.testing import cleanup

TEST_TWOPHASE = bool(os.environ.get('TEST_TWOPHASE'))
TEST_DSN = os.environ.get('TEST_DSN', 'sqlite:///:memory:')

def tearDownReadMe(test):
    # clean up Zope
    cleanup.cleanUp()

    # clean up SQLAlchemy
    Base = test.globs['Base']
    engine = test.globs['engine']
    Base.metadata.drop_all(engine)

def test_suite():
    optionflags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS

    suite = unittest.TestSuite()
    suite.addTest(doctest.DocFileSuite(
        'README.txt',
        optionflags=optionflags,
        tearDown=tearDownReadMe,
        globs={'TEST_DSN': TEST_DSN, 'TEST_TWOPHASE': TEST_TWOPHASE}))
    return suite
