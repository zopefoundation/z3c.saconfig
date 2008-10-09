import zope.interface
import zope.schema
import zope.component.zcml
from zope.configuration.name import resolve

import utility
import interfaces

class IEngineDirective(zope.interface.Interface):
    """Registers a database engine factory."""

    url = zope.schema.URI(
        title=u"Database URL",
        description=u"e.g. 'sqlite:///:memory:'.",
        required=True)

    name = zope.schema.Text(
        title=u"Engine name",
        description=u"Empty if this is the default engine.",
        required=False,
        default=u"")

    echo = zope.schema.Bool(
        title=u'Echo SQL statements',
        description=u'Enable logging statements for debugging.',
        required=False,
        default=False)

    setup = zope.schema.BytesLine(
        title=u'After engine creation hook',
        description=u'Callback for creating mappers etc. One argument is passed, the engine',
        required=False,
        default=None)


class ISessionDirective(zope.interface.Interface):
    """Registers a database scoped session"""

    name = zope.schema.Text(
        title=u"Scoped session name",
        description=u"Empty if this is the default session.",
        required=False,
        default=u"")

    twophase = zope.schema.Bool(
        title=u'Use two-phase commit',
        description=u'Session should use two-phase commit',
        required=False,
        default=False)

    engine = zope.schema.Text(
        title=u"Engine name",
        description=u"Empty if this is to use the default engine.",
        required=False,
        default=u"")

    factory = zope.schema.DottedName(
        title=u'Scoped Session utility factory',
        description=u'GloballyScopedSession by default',
        required=False,
        default="z3c.saconfig.utility.GloballyScopedSession")


def engine(_context, url, name=u"", echo=False, setup=None, twophase=False):
    factory = utility.EngineFactory(url, echo=echo)
    
    zope.component.zcml.utility(
        _context,
        provides=interfaces.IEngineFactory,
        component=factory,
        permission=zope.component.zcml.PublicPermission,
        name=name)
    
    if setup:
        if _context.package is None:
            callback = resolve(setup)
        else:
            callback = resolve(setup, package=_context.package.__name__)
        callback(factory())

def session(_context, name=u"", engine=u"", twophase=False,
            factory="z3c.saconfig.utility.GloballyScopedSession"):
    if _context.package is None:
        ScopedSession = resolve(factory)
    else:
        ScopedSession = resolve(factory, package=_context.package.__name__)
    scoped_session = ScopedSession(engine=engine, twophase=twophase)

    zope.component.zcml.utility(
        _context,
        provides=interfaces.IScopedSession,
        component=scoped_session,
        permission=zope.component.zcml.PublicPermission,
        name=name)
    
