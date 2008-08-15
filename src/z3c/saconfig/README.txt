z3c.saconfig
************

Introduction
============

This aim of this package is to offer a simple but flexible way to
configure SQLAlchemy's scoped session support using the Zope 3
component architecture. This package is based on ``zope.sqlalchemy``, which
offers transaction integration between Zope and SQLAlchemy.

We sketch out two main scenarios here:

* one database per Zope 3 instance.

* one database per site (or Grok application) in a Zope 3 instance
  (and thus multiple databases per Zope 3 instance).

This package does not provide facilities to allow multiple databases
in a single site; if you want more than one database in your Zope 3
instance, you will need to set up different sites.

GloballyScopedSession (one database per Zope 3 instance)
========================================================

The simplest way to set up SQLAlchemy for Zope is to have a single
thread-scoped session that's global to your entire Zope
instance. Multiple applications will all share this session. The
engine is set up with a global utility.

We use the SQLAlchemy ``sqlalchemy.ext.declarative`` extension to
define some tables and classes::

  >>> from sqlalchemy import *
  >>> from sqlalchemy.ext.declarative import declarative_base
  >>> from sqlalchemy.orm import relation

  >>> Base = declarative_base()
  >>> class User(Base):
  ...     __tablename__ = 'test_users'
  ...     id = Column('id', Integer, primary_key=True)
  ...     name = Column('name', String(50))
  ...     addresses = relation("Address", backref="user")
  >>> class Address(Base):
  ...     __tablename__ = 'test_addresses'
  ...     id = Column('id', Integer, primary_key=True)
  ...     email = Column('email', String(50))
  ...     user_id = Column('user_id', Integer, ForeignKey('test_users.id'))

So far this doesn't differ from the ``zope.sqlalchemy`` example. We
now arrive at the first difference. Instead of making the engine
directly, we can set up the engine factory as a (global) utility. This
utility makes sure an engine is created and cached for us.

  >>> from z3c.saconfig import EngineFactory
  >>> engine_factory = EngineFactory(TEST_DSN)

You can pass the parameters you'd normally pass to
``sqlalchemy.create_engine`` to ``EngineFactory``. Note that
``z3c.saconfig`` assumes ``convert_unicode`` to be ``True`` by
default.

We now register the engine factory as a global utility using
``zope.component``. Normally you'd use either ZCML or Grok to do this
confirmation, but we'll do it manually here::::

  >>> from zope import component
  >>> from z3c.saconfig.interfaces import IEngineFactory
  >>> component.provideUtility(engine_factory, provides=IEngineFactory)

Note that setting up an engine factory is not actually necessary in
the globally scoped use case. You could also just create the engine as
a global and pass it as ``bind`` when you create the
``GloballyScopedSession`` later.

Let's look up the engine by calling the factory and create the tables
in our test database::

  >>> engine = engine_factory()
  >>> Base.metadata.create_all(engine)

Now as for the second difference from ``zope.sqlalchemy``: how the
session is set up and used. We'll use the ``GloballyScopedSession``
utility to implement our session creation::

  >>> from z3c.saconfig import GloballyScopedSession

We give the constructor to ``GloballyScopedSession`` the parameters
you'd normally give to ``sqlalchemy.orm.create_session``, or
``sqlalchemy.orm.sessionmaker``::

  >>> utility = GloballyScopedSession(twophase=TEST_TWOPHASE)

``GlobalScopedSession`` looks up the engine using ``IEngineFactory``
if you don't supply your own ``bind``
argument. ``GloballyScopedSession`` also automatically sets up the
``autocommit``, ``autoflush`` and ``extension`` parameters to be the
right ones for Zope integration, so normally you wouldn't need to
supply these, but you could pass in your own if you do need it.

We now register this as an ``IScopedSession`` utility::
  
  >>> from z3c.saconfig.interfaces import IScopedSession
  >>> component.provideUtility(utility, provides=IScopedSession)
 
We are done with configuration now. As you have seen it involves
setting up two utilities, ``IEngineFactory`` and ``IScopedSession``,
where only the latter is really needed in this globally shared session
use case. 

After the ``IScopedSession`` utility is registered, one can import the
``Session`` class from z3c.saconfig.  This ``Session`` class is like
the one you'd produce with ``sessionmaker`` from
SQLAlchemy. `z3c.saconfig.Session`` is intended to be the only
``Session`` class you'll ever need, as all configuration and Zope
integration is done automatically for you by ``z3c.saconfig``,
appropriate the context in Zope where you use it. There is no need to
create ``Session`` classes yourself with ``sessionmaker`` or
``scoped_sesion`` anymore.

We can now use the ``Session`` class to create a session which will
behave according to the utility we provided::

  >>> from z3c.saconfig import Session
  >>> session = Session()

Now things go the usual ``zope.sqlalchemy`` way, which is like
``SQLAlchemy`` except you can use Zope's ``transaction`` module::

  >>> session.query(User).all()
  []    
  >>> import transaction
  >>> session.add(User(name='bob'))
  >>> transaction.commit()

  >>> session = Session()
  >>> bob = session.query(User).all()[0]
  >>> bob.name
  u'bob'
  >>> bob.addresses
  []

Events
======

When a new engine is created by an ``EngineFactory``, an
``IEngineCreatedEvent`` is fired. This event has an attribute
``engine`` that contains the engine that was just created::

  >>> from z3c.saconfig.interfaces import IEngineCreatedEvent
  >>> @component.adapter(IEngineCreatedEvent)
  ... def createdHandler(event):
  ...     print "created engine"
  >>> component.provideHandler(createdHandler)
  >>> event_engine_factory = EngineFactory(TEST_DSN1)
  >>> engine = event_engine_factory()
  created engine

Let's get rid of the event handler again::

  >>> sm = component.getSiteManager()
  >>> sm.unregisterHandler(None, 
  ...   required=[IEngineCreatedEvent])
  True

SiteScopedSession (one database per site)
=========================================

In the example above we have set up SQLAlchemy with Zope using
utilities, but it did not gain us very much, except that you can just
use ``z3c.saconfig.Session`` to get the correct session.

Now we'll see how we can set up different engines per site by
registering the engine factory as a local utility for each one.

In order to make this work, we'll set up ``SiteScopedSession`` instead
of ``GloballyScopedSession``. We need to subclass
``SiteScopedSession`` first because we need to implement its
``siteScopeFunc`` method, which should return a unique ID per site
(such as a path retrieved by ``zope.traversing.api.getPath``). We need
to implement it here, as ``z3c.saconfig`` leaves this policy up to the
application or a higher-level framework::

  >>> from z3c.saconfig import SiteScopedSession
  >>> class OurSiteScopedSession(SiteScopedSession):
  ...   def siteScopeFunc(self):
  ...      return getSite().id # the dummy site has a unique id
  >>> utility = OurSiteScopedSession()
  >>> component.provideUtility(utility, provides=IScopedSession)

We want to register two engine factories, each in a different site::

  >>> engine_factory1 = EngineFactory(TEST_DSN1)
  >>> engine_factory2 = EngineFactory(TEST_DSN2)

We need to set up the database in both new engines::

  >>> Base.metadata.create_all(engine_factory1())
  >>> Base.metadata.create_all(engine_factory2())

Let's now create two sites, each of which will be connected to another
engine::

  >>> site1 = DummySite(id=1)
  >>> site2 = DummySite(id=2)

We set the local engine factories for each site:

  >>> sm1 = site1.getSiteManager()
  >>> sm1.registerUtility(engine_factory1, provided=IEngineFactory)
  >>> sm2 = site2.getSiteManager()
  >>> sm2.registerUtility(engine_factory2, provided=IEngineFactory)

Just so we don't accidentally get it, we'll disable our global engine factory::

  >>> component.provideUtility(None, provides=IEngineFactory)

When we set the site to ``site1``, a lookup of ``IEngineFactory`` gets
us engine factory 1::

  >>> setSite(site1)
  >>> component.getUtility(IEngineFactory) is engine_factory1
  True

And when we set it to ``site2``, we'll get engine factory 2::

  >>> setSite(site2)
  >>> component.getUtility(IEngineFactory) is engine_factory2
  True

We can look up our global utility even if we're in a site::

  >>> component.getUtility(IScopedSession) is utility
  True
  
Phew. That was a lot of set up, but basically this is actually just
straightforward utility setup code; you should use the APIs or Grok's
``grok.local_utility`` directive to set up local utilities. Now all
that is out of the way, we can create a session for ``site1``::

  >>> setSite(site1)
  >>> session = Session()

The database is still empty::

  >>> session.query(User).all() 
  []

We'll add something to this database now::

  >>> session.add(User(name='bob'))
  >>> transaction.commit()

``bob`` is now there::

  >>> session = Session()
  >>> session.query(User).all()[0].name
  u'bob'

Now we'll switch to ``site2``::

  >>> setSite(site2)
  
If we create a new session now, we should now be working with a
different database, which should still be empty::

  >>> session = Session()
  >>> session.query(User).all() 
  []
  
We'll add ``fred`` to this database::

  >>> session.add(User(name='fred'))
  >>> transaction.commit()

Now ``fred`` is indeed there::
 
  >>> session = Session()
  >>> users = session.query(User).all()
  >>> len(users)
  1
  >>> users[0].name
  u'fred'

And ``bob`` is still in ``site1``::

  >>> setSite(site1)
  >>> session = Session()
  >>> users = session.query(User).all()
  >>> len(users)
  1
  >>> users[0].name
  u'bob'

Engines and Threading
=====================

  >>> engine = None
  >>> def setEngine():
  ...     global engine
  ...     engine = engine_factory1()

Engine factories must produce the same engine:
 
  >>> setEngine()
  >>> engine is engine_factory1()
  True

Even if you call it in a different thread:

  >>> import threading
  >>> engine = None
  >>> t = threading.Thread(target=setEngine)
  >>> t.start()
  >>> t.join()

  >>> engine is engine_factory1()
  True

Unless they are reset:
  
  >>> engine_factory1.reset()
  >>> engine is engine_factory1()
  False

Even engine factories with the same parameters created at (almost) the same
time should produce different engines:

  >>> EngineFactory(TEST_DSN1)() is EngineFactory(TEST_DSN1)()
  False

Configuration using ZCML
========================

A configuration directive is provided to register a database engine
factory using ZCML.

  >>> from cStringIO import StringIO
  >>> from zope.configuration import xmlconfig
  >>> import z3c.saconfig
  >>> xmlconfig.XMLConfig('meta.zcml', z3c.saconfig)()

Let's try registering the directory again.

  >>> xmlconfig.xmlconfig(StringIO("""
  ... <configure xmlns="http://namespaces.zope.org/db">
  ...   <engine name="dummy" url="sqlite:///:memory:" />
  ... </configure>"""))

  >>> component.getUtility(IEngineFactory, name="dummy")
  <z3c.saconfig.utility.EngineFactory object at ...>

This time with a setup call.

  >>> xmlconfig.xmlconfig(StringIO("""
  ... <configure xmlns="http://namespaces.zope.org/db">
  ...   <engine name="dummy2" url="sqlite:///:memory:"
  ...           setup="z3c.saconfig.tests.engine_subscriber" />
  ... </configure>"""))
  got: Engine(sqlite:///:memory:)

The session directive is provided to register a scoped session utility:

  >>> xmlconfig.xmlconfig(StringIO("""
  ... <configure xmlns="http://namespaces.zope.org/db">
  ...   <session name="dummy" engine="dummy2" />
  ... </configure>"""))

  >>> component.getUtility(IScopedSession, name="dummy")
  <z3c.saconfig.utility.GloballyScopedSession object at ...>

  >>> from z3c.saconfig import named_scoped_session
  >>> factory = component.getUtility(IEngineFactory, name="dummy2")
  >>> Session = named_scoped_session('dummy')
  >>> Session().bind is factory()
  True
