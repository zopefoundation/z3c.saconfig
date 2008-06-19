"""
Some reusable, standard implementations of IScopedSession.
"""

import thread
from zope.interface import implements
import sqlalchemy
from zope.sqlalchemy import ZopeTransactionExtension

from z3c.saconfig.interfaces import IScopedSession

class GloballyScopedSession(object):
    """A globally scoped session.

    Register this as a global utility to have just one kind of session
    per Zope instance. All applications in this instance will share the
    same session.

    To register as a global utility you may need to register it with
    a custom factory, or alternatively subclass it and override __init__
    to pass the right arguments to the superclasses __init__.
    """
    implements(IScopedSession)

    def __init__(self, **kw):
        """Pass keywords arguments for sqlalchemy.orm.create_session.

        Note that GloballyScopedSesssion does have different defaults than
        ``create_session`` for various parameters where it makes sense
        for Zope integration, namely:

        autocommit = False
        autoflush = True
        extension = ZopeTransactionExtension()

        Normally you wouldn't pass these in, but if you have the need
        to override them, you could.
        """
        if 'autocommit' not in kw:
            kw['autocommit'] = False
        if 'autoflush' not in kw:
            kw['autoflush'] = True
        if 'extension' not in kw:
            kw['extension'] = ZopeTransactionExtension()
        self.kw = kw

    def session_factory(self):
        return sqlalchemy.orm.create_session(**self.kw)
    
    def scopefunc(self):
        return thread.get_ident()
