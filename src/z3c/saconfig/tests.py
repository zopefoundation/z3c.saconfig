# You may want to run the tests with your database. To do so set the
# environment variable TEST_DSN to the connection url. e.g.:
#
# export TEST_DSN=postgres://plone:plone@localhost/test
# export TEST_DSN=mssql://plone:plone@/test?dsn=mydsn

# Since the test exercise what happens with two different DSNs
# locally, you need to also set up a different TEST_DSN2.

# To test in twophase commit mode export TEST_TWOPHASE=True 
#
# NOTE: The sqlite that ships with Mac OS X 10.4 is buggy.
# Install a newer version (3.5.6) and rebuild pysqlite2 against it.


import unittest
import doctest
import os

from zope.testing import cleanup
from zope.testing.cleanup import addCleanUp

from zope import component
from zope.component import registry
import zope.component.eventtesting

TEST_TWOPHASE = bool(os.environ.get('TEST_TWOPHASE'))
TEST_DSN = os.environ.get('TEST_DSN', 'sqlite:///:memory:')
TEST_DSN1 = TEST_DSN
# this can reuse TEST_DSN1 in the default case, as we can open another
# in-memory database. You can't do this for other databases however.
TEST_DSN2 = os.environ.get('TEST_DSN', TEST_DSN1)

def setUpReadMe(test):
    # set up special local component architecture
    setHooks()
    # set up event handling
    zope.component.eventtesting.setUp(test)

def tearDownReadMe(test):
    # clean up Zope
    cleanup.cleanUp()

    # clean up SQLAlchemy
    Base = test.globs['Base']
    engine = test.globs['engine']
    Base.metadata.drop_all(engine)

# a very simple implementation of setSite and getSite so we don't have
# to rely on zope.app.component just for our tests
_site = None

class DummySite(object):
    def __init__(self, id):
        self.id = id
        self._sm = SiteManager()
        
    def getSiteManager(self):
        return self._sm

class SiteManager(registry.Components):
    def __init__(self):
        super(SiteManager, self).__init__()
        self.__bases__ = (component.getGlobalSiteManager(),)

def setSite(site=None):
    global _site
    _site = site

def getSite():
    return _site

def adapter_hook(interface, object, name='', default=None):
    try:
        return getSiteManager().adapters.adapter_hook(
            interface, object, name, default)
    except component.interfaces.ComponentLookupError:
        return default

def getSiteManager(context=None):
    if _site is not None:
        return _site.getSiteManager()
    return component.getGlobalSiteManager()

def setHooks():
    component.adapter_hook.sethook(adapter_hook)
    component.getSiteManager.sethook(getSiteManager)

def resetHooks():
    component.adapter_hook.reset()
    component.getSiteManager.reset()

# make sure hooks get cleaned up after tests are run
addCleanUp(resetHooks)

def engine_subscriber(engine):
    print "got: %s " % engine

def test_suite():
    optionflags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    globs = {
        'DummySite': DummySite,
        'setSite': setSite,
        'getSite': getSite,
        'TEST_DSN': TEST_DSN,
        'TEST_DSN1': TEST_DSN1,
        'TEST_DSN2': TEST_DSN2,
        'TEST_TWOPHASE': TEST_TWOPHASE,
        }
    
    suite = unittest.TestSuite()
    
    suite.addTest(doctest.DocFileSuite(
        'README.txt',
        optionflags=optionflags,
        setUp=setUpReadMe,
        tearDown=tearDownReadMe,
        globs=globs))
    return suite
