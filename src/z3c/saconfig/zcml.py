import warnings

import zope.component.zcml
import zope.interface
import zope.schema
from zope.component.security import PublicPermission
from zope.configuration.name import resolve

from .interfaces import IEngineFactory
from .interfaces import IScopedSession
from .utility import EngineFactory


class IEngineDirective(zope.interface.Interface):
    """Registers a database engine factory."""

    url = zope.schema.URI(
        title='Database URL',
        description="e.g. 'sqlite:///:memory:'.",
        required=True)

    name = zope.schema.Text(
        title="Engine name",
        description="Empty if this is the default engine.",
        required=False,
        default='')

    convert_unicode = zope.schema.Bool(
        title='Convert all string columns to unicode',
        description='This setting makes the SQLAlchemy String column type '
                    'equivalent to UnicodeString. Do not use this unless '
                    'there is a good reason not to use standard '
                    'UnicodeString columns',
        required=False,
        default=False)

    echo = zope.schema.Bool(
        title='Echo SQL statements',
        description='Enable logging statements for debugging.',
        required=False,
        default=None)

    setup = zope.schema.BytesLine(
        title='After engine creation hook',
        description='Callback for creating mappers etc. '
                    'One argument is passed, the engine',
        required=False,
        default=None)

    # Connection pooling options - probably only works on SQLAlchemy 0.5 and up

    pool_size = zope.schema.Int(
        title="The size of the pool to be maintained",
        description="Defaults to 5 in SQLAlchemy.",
        required=False)

    max_overflow = zope.schema.Int(
        title="The maximum overflow size of the pool.",
        description="When the number of checked-out connections "
                    "reaches the size set in pool_size, additional "
                    "connections will be returned up to this limit. "
                    "Defaults to 10 in SQLAlchemy",
        required=False)

    pool_recycle = zope.schema.Int(
        title="Number of seconds between connection recycling",
        description="Upon checkout, if this timeout is "
                    "surpassed the connection will be closed and "
                    "replaced with a newly opened connection",
        required=False)

    pool_timeout = zope.schema.Int(
        title="The number of seconds to wait before giving up on "
              "returning a connection.",
        description="Defaults to 30 in SQLAlchemy if not set",
        required=False)


class ISessionDirective(zope.interface.Interface):
    """Registers a database scoped session"""

    name = zope.schema.Text(
        title="Scoped session name",
        description="Empty if this is the default session.",
        required=False,
        default="")

    twophase = zope.schema.Bool(
        title='Use two-phase commit',
        description='Session should use two-phase commit',
        required=False,
        default=False)

    engine = zope.schema.Text(
        title="Engine name",
        description="Empty if this is to use the default engine.",
        required=False,
        default="")

    factory = zope.schema.DottedName(
        title='Scoped Session utility factory',
        description='GloballyScopedSession by default',
        required=False,
        default="z3c.saconfig.utility.GloballyScopedSession")


def engine(_context, url, name="", convert_unicode=False,
           echo=None, setup=None, twophase=False,
           pool_size=None, max_overflow=None, pool_recycle=None,
           pool_timeout=None):

    if convert_unicode:  # pragma: no cover
        warnings.warn(
            '`convert_unicode` is no longer suported by SQLAlchemy, so it is'
            ' ignored here.', DeprecationWarning)

    kwargs = {
        'echo': echo,
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

    factory = EngineFactory(url, **kwargs)

    zope.component.zcml.utility(
        _context,
        provides=IEngineFactory,
        component=factory,
        permission=PublicPermission,
        name=name)

    if setup:
        if isinstance(setup, bytes):
            setup = setup.decode()

        if _context.package is None:
            callback = resolve(setup)
        else:
            callback = resolve(setup, package=_context.package.__name__)
        _context.action(
            discriminator=(IEngineFactory, name),
            callable=callback,
            args=(factory(), ),
            order=9999)


def session(_context, name="", engine="", twophase=False,
            factory="z3c.saconfig.utility.GloballyScopedSession"):
    if _context.package is None:
        ScopedSession = resolve(factory)
    else:
        ScopedSession = resolve(factory, package=_context.package.__name__)
    scoped_session = ScopedSession(engine=engine, twophase=twophase)

    zope.component.zcml.utility(
        _context,
        provides=IScopedSession,
        component=scoped_session,
        permission=PublicPermission,
        name=name)
