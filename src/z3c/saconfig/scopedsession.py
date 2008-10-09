from z3c.saconfig.interfaces import IScopedSession

from sqlalchemy.orm import scoped_session
from zope import component

def session_factory(name=u''):
    """This is used by scoped session to create a new Session object.

    It delegates to a IScopedSession utility.
    """
    utility = component.getUtility(IScopedSession, name)
    return utility.sessionFactory()

def scopefunc(name=u''):
    """This is used by scoped session to distinguish between sessions.

    It delegates to a IScopedSession utility.
    """
    utility = component.getUtility(IScopedSession, name)
    return utility.scopeFunc()

# this is framework central configuration. Use a IScopedSession utility
# to define behavior.
Session = scoped_session(session_factory, scopefunc)

_named_scoped_sessions = {u'': Session}

def named_scoped_session(name):
    try:
        return _named_scoped_sessions[name]
    except KeyError:
        return _named_scoped_sessions.setdefault(name,
                            scoped_session(lambda:session_factory(name),
                                           lambda:scopefunc(name)))
