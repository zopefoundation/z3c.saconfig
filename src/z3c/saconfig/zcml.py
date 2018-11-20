from .interfaces import IEngineFactory
from .interfaces import IScopedSession
from .utility import EngineFactory
from zope.configuration.name import resolve

import six
import zope.component.zcml
import zope.interface
import zope.schema


try:
    from zope.component.security import PublicPermission
except ImportError:
    # BBB for Zope 2.10
    from zope.component.zcml import PublicPermission


class IEngineDirective(zope.interface.Interface):
    """Registers a database engine factory."""

    url = zope.schema.URI(
        title=six.text_type("Database URL"),
        description=six.text_type("e.g. 'sqlite:///:memory:'."),
        required=True)

    name = zope.schema.Text(
        title=six.text_type("Engine name"),
        description=six.text_type("Empty if this is the default engine."),
        required=False,
        default=six.text_type(""))

    convert_unicode = zope.schema.Bool(
        title=six.text_type('Convert all string columns to unicode'),
        description=six.text_type(
            'This setting makes the SQLAlchemy String column type '
            'equivalent to UnicodeString. Do not use this unless '
            'there is a good reason not to use standard '
            'UnicodeString columns'),
        required=False,
        default=False)

    echo = zope.schema.Bool(
        title=six.text_type('Echo SQL statements'),
        description=six.text_type('Enable logging statements for debugging.'),
        required=False,
        default=None)

    setup = zope.schema.BytesLine(
        title=six.text_type('After engine creation hook'),
        description=six.text_type(
            'Callback for creating mappers etc. One argument '
            'is passed, the engine'),
        required=False,
        default=None)

    # Connection pooling options - probably only works on SQLAlchemy 0.5 and up

    pool_size = zope.schema.Int(
        title=six.text_type("The size of the pool to be maintained"),
        description=six.text_type("Defaults to 5 in SQLAlchemy."),
        required=False)

    max_overflow = zope.schema.Int(
        title=six.text_type("The maximum overflow size of the pool."),
        description=six.text_type(
            "When the number of checked-out connections reaches the "
            "size set in pool_size, additional connections will be "
            "returned up to this limit. Defaults to 10 in SQLAlchemy"),
        required=False)

    pool_recycle = zope.schema.Int(
        title=six.text_type("Number of seconds between connection recycling"),
        description=six.text_type(
            "Upon checkout, if this timeout is surpassed the connection "
            "will be closed and replaced with a newly opened connection"),
        required=False)

    pool_timeout = zope.schema.Int(
        title=six.text_type(
            "The number of seconds to wait before giving up on "
            "returning a connection."),
        description=six.text_type(
            "Defaults to 30 in SQLAlchemy if not set"),
        required=False)


class ISessionDirective(zope.interface.Interface):
    """Registers a database scoped session"""

    name = zope.schema.Text(
        title=six.text_type("Scoped session name"),
        description=six.text_type("Empty if this is the default session."),
        required=False,
        default=six.text_type(""))

    twophase = zope.schema.Bool(
        title=six.text_type('Use two-phase commit'),
        description=six.text_type('Session should use two-phase commit'),
        required=False,
        default=False)

    engine = zope.schema.Text(
        title=six.text_type("Engine name"),
        description=six.text_type("Empty if this is to use the default engine."),
        required=False,
        default=six.text_type(""))

    factory = zope.schema.DottedName(
        title=six.text_type('Scoped Session utility factory'),
        description=six.text_type('GloballyScopedSession by default'),
        required=False,
        default="z3c.saconfig.utility.GloballyScopedSession")


def engine(_context, url, name=six.text_type(""), convert_unicode=False,
           echo=None, setup=None, twophase=False,
           pool_size=None, max_overflow=None, pool_recycle=None,
           pool_timeout=None):

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

    factory = EngineFactory(url, **kwargs)

    zope.component.zcml.utility(
        _context,
        provides=IEngineFactory,
        component=factory,
        permission=PublicPermission,
        name=name)

    if setup:
        try:
            setup = setup.decode()
        except AttributeError:
            pass

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
