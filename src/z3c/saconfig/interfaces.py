from zope.interface import Interface, implements, Attribute

class IScopedSession(Interface):
    """A utility that plugs into SQLAlchemy's scoped session machinery.

    The idea is that you'd either register a IScopedSession utility globally,
    for simple configurations, or locally, if you want to have the ability
    to transparently use a different engine and session configuration per
    database.
    """
    def sessionFactory():
        """Create a SQLAlchemy session.

        Typically you'd use sqlalchemy.orm.create_session to create
        the session here.
        """

    def scopeFunc():
        """Determine the scope of the session.

        This can be used to scope the session per thread, per Zope 3 site,
        or otherwise. Return an immutable value to scope the session,
        like a thread id, or a tuple with thread id and application id.
        """

class ISiteScopedSession(IScopedSession):
    """A utility that makes sessions be scoped by site.
    """
    def siteScopeFunc():
        """Returns a unique id per site.
        """

class IEngineFactory(Interface):
    """A utility that maintains an SQLAlchemy engine.

    If the engine isn't created yet, it will create it. Otherwise the
    engine will be cached.
    """

    def __call__():
        """Get the engine.

        This creates the engine if this factory was not used before,
        otherwise returns a cached version.
        """

    def configuration():
        """Returns the engine configuration in the form of an args, kw tuple.

        Return the parameters used to create an engine as a tuple with
        an args list and a kw dictionary.
        """

    def reset():
        """Reset the cached engine (if any).

        This causes the engine to be recreated on next use.
        """

class IEngineCreatedEvent(Interface):
    """An SQLAlchemy engine has been created.

    Hook into this event to do setup that can only be performed with
    an active engine.
    """
    engine = Attribute("The engine that was just created.")
    
class EngineCreatedEvent(object):
    implements(IEngineCreatedEvent)

    def __init__(self, engine):
        self.engine = engine
