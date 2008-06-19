from zope.interface import Interface

class IScopedSession(Interface):
    """A utility that plugs into SQLAlchemy's scoped session machinery.

    The idea is that you'd either register a IScopedSession utility globally,
    for simple configurations, or locally, if you want to have the ability
    to transparently use a different engine and session configuration per
    database.
    """
    def session_factory():
        """Create a SQLAlchemy session.

        Typically you'd use sqlalchemy.orm.create_session to create
        the session here.
        """

    def scopefunc():
        """Determine the scope of the session.

        This can be used to scope the session per thread, per Zope 3 site,
        or otherwise. Return an immutable value to scope the session,
        like a thread id, or a tuple with thread id and application id.
        """


