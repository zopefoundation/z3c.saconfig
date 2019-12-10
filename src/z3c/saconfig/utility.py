"""
Some reusable, standard implementations of IScopedSession.
"""
from z3c.saconfig.interfaces import EngineCreatedEvent
from z3c.saconfig.interfaces import IEngineFactory
from z3c.saconfig.interfaces import IScopedSession
from z3c.saconfig.interfaces import ISiteScopedSession
from zope import component
from zope.event import notify
from zope.interface import implementer
from zope.sqlalchemy import register


import sqlalchemy
import threading
import time


try:
    from threading import get_ident
except ImportError:
    from thread import get_ident


SESSION_DEFAULTS = dict(
    autocommit=False,
    autoflush=True,
    )


@implementer(IScopedSession)
class GloballyScopedSession(object):
    """A globally scoped session.

    Register this as a global utility to have just one kind of session
    per Zope instance. All applications in this instance will share the
    same session.

    To register as a global utility you may need to register it with
    a custom factory, or alternatively subclass it and override __init__
    to pass the right arguments to the superclasses __init__.
    """

    def __init__(self, engine=u'', **kw):
        """Pass keywords arguments for sqlalchemy.orm.create_session.

        The `engine` argument is the name of a utility implementing
        IEngineFactory.

        Note that GloballyScopedSesssion does have different defaults than
        ``create_session`` for various parameters where it makes sense
        for Zope integration, namely:

        autocommit = False
        autoflush = True
        extension = ZopeTransactionExtension()

        Normally you wouldn't pass these in, but if you have the need
        to override them, you could.
        """
        self.engine = engine
        self.kw = _zope_session_defaults(kw)

    def sessionFactory(self):
        kw = self.kw.copy()
        if 'bind' not in kw:
            engine_factory = component.getUtility(IEngineFactory,
                                                  name=self.engine)
            kw['bind'] = engine_factory()
        session = sqlalchemy.orm.create_session(**kw)
        register(session)
        return session

    def scopeFunc(self):
        return get_ident()


def _zope_session_defaults(kw):
    """Adjust keyword parameters with proper defaults for Zope.
    """

    d = SESSION_DEFAULTS.copy()
    d.update(kw)

    return d


@implementer(ISiteScopedSession)
class SiteScopedSession(object):
    """A session that is scoped per site.

    Even though this makes the sessions scoped per site,
    the utility can be registered globally to make this work.

    Creation arguments as for GloballyScopedSession, except that no ``bind``
    parameter should be passed. This means it is possible to create
    a SiteScopedSession utility without passing parameters to its constructor.
    """

    def __init__(self, engine=u'', **kw):
        assert 'bind' not in kw
        self.engine = engine
        self.kw = _zope_session_defaults(kw)

    def sessionFactory(self):
        engine_factory = component.getUtility(IEngineFactory,
                                              name=self.engine)
        kw = self.kw.copy()
        kw['bind'] = engine_factory()
        session = sqlalchemy.orm.create_session(**kw)
        register(session)
        return session

    def scopeFunc(self):
        return (get_ident(), self.siteScopeFunc())

    def siteScopeFunc(self):
        raise NotImplementedError

# Credits: This method of storing engines lifted from zope.app.cache.ram


_COUNTER = 0
_COUNTER_LOCK = threading.Lock()

_ENGINES = {}
_ENGINES_LOCK = threading.Lock()


@implementer(IEngineFactory)
class EngineFactory(object):
    """An engine factory.

    If you need engine connection parameters to be different per site,
    EngineFactory should be registered as a local utility in that
    site.

    If you want this utility to be persistent, you should subclass it
    and mixin Persistent. You could then manage the parameters
    differently than is done in this __init__, for instance as
    attributes, which is nicer if you are using Persistent (or Zope 3
    schema). In this case you need to override the configuration method.
    """

    def __init__(self, *args, **kw):
        self._args = args
        self._kw = kw
        self._key = self._getKey()

    def _getKey(self):
        """Get a unique key"""
        global _COUNTER
        _COUNTER_LOCK.acquire()
        try:
            _COUNTER += 1
            return "%s_%f_%d" % (id(self), time.time(), _COUNTER)
        finally:
            _COUNTER_LOCK.release()

    def __call__(self):
        # optimistically try get without lock
        engine = _ENGINES.get(self._key, None)
        if engine is not None:
            return engine
        # no engine, lock and redo
        _ENGINES_LOCK.acquire()
        try:
            # need to check, another thread may have got there first
            if self._key not in _ENGINES:
                args, kw = self.configuration()
                _ENGINES[self._key] = engine = sqlalchemy.create_engine(
                    *args, **kw)
                notify(EngineCreatedEvent(engine, args, kw))
            return _ENGINES[self._key]
        finally:
            _ENGINES_LOCK.release()

    def configuration(self):
        """Returns engine parameters.

        This can be overridden in a subclass to retrieve the parameters
        from some other place.
        """
        return self._args, self._kw

    def reset(self):
        _ENGINES_LOCK.acquire()
        try:
            if self._key not in _ENGINES:
                return
            # XXX is disposing the right thing to do?
            _ENGINES[self._key].dispose()
            del _ENGINES[self._key]
        finally:
            _ENGINES_LOCK.release()
