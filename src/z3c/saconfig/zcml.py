import zope.interface
import zope.schema
import zope.component.zcml

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

def engine(_context, url, name=u"", echo=False):
    factory = utility.EngineFactory(url, echo=echo)
    
    zope.component.zcml.utility(
        _context,
        provides=interfaces.IEngineFactory,
        component=factory,
        permission=zope.component.zcml.PublicPermission,
        name=name)
        
