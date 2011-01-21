import zope.interface
import zope.schema
import zope.component.zcml
try:
    from zope.component.security import PublicPermission
except ImportError:
    # BBB for Zope 2.10
    from zope.component.zcml import PublicPermission
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

    convert_unicode = zope.schema.Bool(
        title=u'Convert all string columns to unicode',
        description=u'This setting makes the SQLAlchemy String column type '
                    u'equivalent to UnicodeString. Do not use this unless '
                    u'there is a good reason not to use standard '
                    u'UnicodeString columns',
        required=False,
        default=False)
    
    echo = zope.schema.Bool(
        title=u'Echo SQL statements',
        description=u'Enable logging statements for debugging.',
        required=False,
        default=None)
    
    setup = zope.schema.BytesLine(
        title=u'After engine creation hook',
        description=u'Callback for creating mappers etc. One argument is passed, the engine',
        required=False,
        default=None)

    # Connection pooling options - probably only works on SQLAlchemy 0.5 and up
    
    pool_size = zope.schema.Int(
        title=u"The size of the pool to be maintained",
        description=u"Defaults to 5 in SQLAlchemy.",
        required=False)
    
    max_overflow = zope.schema.Int(
        title=u"The maximum overflow size of the pool.",
        description=u"When the number of checked-out connections reaches the " +
                    u"size set in pool_size, additional connections will be " +
                    u"returned up to this limit. Defaults to 10 in SQLAlchemy",
        required=False)
    
    pool_recycle = zope.schema.Int(
        title=u"Number of seconds between connection recycling",
        description=u"Upon checkout, if this timeout is surpassed the connection "
                    u"will be closed and replaced with a newly opened connection",
        required=False)
    
    pool_timeout = zope.schema.Int(
        title=u"The number of seconds to wait before giving up on returning a connection.",
        description=u"Defaults to 30 in SQLAlchemy if not set",
        required=False)

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

def engine(_context, url, name=u"", convert_unicode=False, echo=None, setup=None, twophase=False,
    pool_size=None, max_overflow=None, pool_recycle=None, pool_timeout=None):
    
    kwargs = {
        'echo': echo,
        'convert_unicode': convert_unicode,
    }
    
    # Only add these if they're actually set, since we want to let SQLAlchemy
    # control the defaults
    if pool_size is not None:
        kwargs['pool_size'] = pool_size
    if max_overflow is not None:
        kwargs['max_overflow'] = max_overflow
    if pool_recycle is not None:
        kwargs['pool_recycle'] = pool_recycle
    if pool_timeout is not None:
        kwargs['pool_timeout'] = pool_timeout
    
    factory = utility.EngineFactory(url, **kwargs)
    
    zope.component.zcml.utility(
        _context,
        provides=interfaces.IEngineFactory,
        component=factory,
        permission=PublicPermission,
        name=name)
    
    if setup:
        if _context.package is None:
            callback = resolve(setup)
        else:
            callback = resolve(setup, package=_context.package.__name__)
        _context.action(
            discriminator = (interfaces.IEngineFactory, name),
            callable = callback,
            args = (factory(), ),
            order=9999)


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
        permission=PublicPermission,
        name=name)
