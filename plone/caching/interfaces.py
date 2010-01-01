import zope.i18nmessageid

from zope.interface import Interface
from zope import schema

_ = zope.i18nmessageid.MessageFactory('plone.caching')

X_CACHE_RULE_HEADER = 'X-Cache-Rule'
X_MUTATOR_HEADER    = 'X-Cache-Operation'

class ICacheSettings(Interface):
    """Settings expected to be found in plone.registry
    """
    
    enabled = schema.Bool(
            title=_(u"Globally enabled"),
            description=_(u"If not set, no caching operations will be attempted"),
            default=False
        )
    
    mutatorMapping = schema.Dict(
            title=_(u"Rule set/operation mapping"),
            description=_(u"Maps rule set names to request mutation operation names"),
            key_type=schema.DottedName(title=_(u"Rule set name")),
            value_type=schema.DottedName(title=_(u"Request mutator name")),
        )

    interceptorMapping = schema.Dict(
            title=_(u"Rule set/interceptor mapping"),
            description=_(u"Maps rule set names to cache interceptor operation names"),
            key_type=schema.DottedName(title=_(u"Rule set name")),
            value_type=schema.DottedName(title=_(u"Interceptor name")),
        )
