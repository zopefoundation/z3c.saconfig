z3c.saconfig
************

Introduction
============

This aim of this package is to offer a simple but flexible way to
configure SQLAlchemy's scoped session support using the Zope 3
component architecture. This package is based on ``zope.sqlalchemy``, which
offers transaction integration between Zope and SQLAlchemy.

GloballyScopedSession
=====================

The simplest way to set up SQLAlchemy for Zope is to have a single
thread-scoped session that's global to your entire Zope
instance. Multiple applications will all share this session. The
engine is set up globally, in code.

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

We now set up an engine globally with our test DSN::

  >>> engine = create_engine(TEST_DSN, convert_unicode=True)

And we create the tables in our test database::

  >>> Base.metadata.create_all(engine)

So far this example doesn't differ any from the way
``zope.sqlalchemy`` operates. The difference is in how we set up the
session and use it. We'll use the ``GloballyScopedSession`` utility
to implement our session creation::

  >>> from z3c.saconfig import GloballyScopedSession

We give the constructor to ``GloballyScopedSession`` the parameters
you'd normally give to ``sqlalchemy.orm.create_session``, or
``sqlalchemy.orm.sessionmaker``::

  >>> utility = GloballyScopedSession(
  ...   bind=engine, 
  ...   twophase=TEST_TWOPHASE)

``GloballyScopedSession`` automatically sets up the ``autocommit``,
``autoflush`` and ``extension`` parameters to be the right ones for
Zope integration, so normally you wouldn't need to supply these, but
you could pass in your own if you do need it.

We now register this as an ``IScopedSession`` utility with
``zope.component``. Normally you'd use either ZCML or Grok to do this
confirmation, but we'll do it manually here::
  
  >>> from zope import component
  >>> from z3c.saconfig.interfaces import IScopedSession
  >>> component.provideUtility(utility, provides=IScopedSession)
 
We can now use the ``Session`` object create a session which
will behave according to the utility we provided::

  >>> from z3c.saconfig import Session
  >>> session = Session()

Now things go the usual ``zope.sqlalchemy`` way, which is like
``SQLAlchemy`` except you can use Zope's ``transaction`` module::

  >>> session.query(User).all()
  []    
  >>> import transaction
  >>> session.save(User(name='bob'))
  >>> transaction.commit()

  >>> session = Session()
  >>> bob = session.query(User).all()[0]
  >>> bob.name
  u'bob'
  >>> bob.addresses
  []

Running the tests
=================

This package can be checked out from
svn://svn.zope.org/repos/main. You can then execute the buildout to
download and install the requirements and install the test
runner. Using your desired python run:

$ python bootstrap.py

This will download the dependent packages and setup the test script, which may
be run with:

$ bin/test

To enable testing with your own database set the TEST_DSN environment
variable to your sqlalchemy database dsn. Two-phase commit behaviour
may be tested by setting the TEST_TWOPHASE variable to a non empty
string. e.g:

$ TEST_DSN=postgres://test:test@localhost/test TEST_TWOPHASE=True bin/test
