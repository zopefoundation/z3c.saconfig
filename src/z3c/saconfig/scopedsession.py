from z3c.saconfig.interfaces import IScopedSession

from sqlalchemy.orm import scoped_session
from zope import component

def session_factory():
    """This is used by scoped session to create a new Session object.

    It delegates to a IScopedSession utility.
    """
    utility = component.getUtility(IScopedSession)
    return utility.sessionFactory()

def scopefunc():
    """This is used by scoped session to distinguish between sessions.

    It delegates to a IScopedSession utility.
    """
    utility = component.getUtility(IScopedSession)
    return utility.scopeFunc()

# this is framework central configuration. Use a IScopedSession utility
# to define behavior.
Session = scoped_session(session_factory, scopefunc)
