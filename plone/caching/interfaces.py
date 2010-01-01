import zope.i18nmessageid

from zope.interface import Interface
from zope import schema

_ = zope.i18nmessageid.MessageFactory('plone.caching')

X_CACHE_RULE_HEADER  = 'X-Cache-Rule'
X_MUTATOR_HEADER     = 'X-Cache-Mutator'
X_INTERCEPTOR_HEADER = 'X-Cache-Interceptor'

class ICacheSettings(Interface):
    """Settings expected to be found in plone.registry
    """
    
    enabled = schema.Bool(
            title=_(u"Globally enabled"),
            description=_(u"If not set, no caching operations will be attempted"),
            default=False,
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

#
#  Cache operations
# 

class IResponseMutator(Interface):
    """Represents a caching operation, typically setting of response headers.
    
    Should be registered as a named multi-adapter from a cacheable object
    (e.g. a view, or just Interface for a general operation) and the request.
    """
    
    def __call__(ruleset, response):
        """Mutate the response. ``rulset`` is the name of the caching ruleset
        that was matched. It may be ``None``. ``response`` is the current
        HTTP response.
        """

class ICacheInterceptor(Interface):
    """Represents a caching intercept, typically for the purposes of sending
    a 304 response.
    
    Should be registered as a named multi-adapter from a cacheable object
    (e.g. a view, or just Interface for a general operation) and the request.
    """
    
    def __call__(ruleset, response):
        """Mutate the response if required, e.g. by setting headers. Return
        None if the request should *not* be interrupted. Otherwise, return
        a new response body as a unicode string. For simple 304 responses,
        returning ``u""`` will suffice.
        
        ``rulset`` is the name of the caching ruleset that was matched. It may
        be ``None``. ``response`` is the current HTTP response.
        """

#
# Cache operation *types* (for UI support)
# 

class ICacheOperationType(Interface):
    """Base interface for IResponseMutatorType and ICacheInterceptorType -
    see below
    """
    
    title = schema.TextLine(
            title=_(u"Title"),
            description=_(u"A descriptive title for the operation"),
        )
    
    description = schema.Text(
            title=_(u"Description"),
            description=_(u"A longer description for the operaton"),
            required=False,
        )
    
    prefix = schema.DottedName(
            title=_(u"Registry prefix"),
            description=_(u"Prefix for records in the registry pertaining to "
                          u"this operation. This, alongside the next "
                          u"parameter, allows the user interface to present "
                          u"relevant configuration options for this "
                          u"operation."),
            required=False, 
        )
    
    options = schema.Tuple(
            title=_(u"Registry options"),
            description=_(u"A tuple of options which can be used to "
                          u"configure this operation. An option is looked "
                          u"up in the registry by concatenating the prefix "
                          u"with the option name, optionally preceded by "
                          u"the rule set name, to allow per-rule overrides."),
            value_type=schema.DottedName(),
            required=False,
        )
    
class IResponseMutatorType(ICacheOperationType):
    """A named utility which is used to provide UI support for response
    mutators. The name should correspond to the mutator adapter name.
    
    The usual pattern is::
    
        from zope.interface import implements, classProvides, Interface
        from zope.component import adapts
    
        from plone.caching.interfaces import IResponseMutator
        from plone.caching.interfaces import IResponseMutatorType
        
        from plone.caching.utils import lookupOptions
        
        class SomeMutator(object):
            implements(IResponseMutator)
            adapts(Interface, Interface)
            classProvides(IResponseMutatorType)
            
            title = u"Some mutator"
            description = u"Mutator description"
            prefix = 'my.package.somemutator'
            options = ('option1', 'option2')
            
            def __init__(self, published, request):
                self.published = published
                self.request = request
            
            def __call__(self, rulename, response):
                options = lookupOptions(self.__class__, rulename)
                ...
        
    This defines an adapter factory (the class), which itself provides
    information about the type of mutator. In ZCML, these would be registered
    with::
        
        <adapter factory=".mutator.SomeMutator" name="my.package.somemutator" />
        <utility component=".mutator.SomeMutator" name="my.package.somemutator" />
    
    Note that the use of *component* for the ``<utility />`` registration - we
    are registering the class as a utility. Also note that the utility and
    adapter names must match. By convention, the option prefix should be the
    same as the adapter/utility name.
    
    You could also register an instance as a utility, of course.
    """

class ICacheInterceptorType(ICacheOperationType):
    """``ICacheInterceptor`` equivalent of ``IResponseMutatorType`` - see
    above.
    """
