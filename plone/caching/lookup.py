from zope.interface import implements, Interface
from zope.component import adapts, queryMultiAdapter, queryUtility

from plone.registry.interfaces import IRegistry

from z3c.caching.registry import lookup

from plone.caching.interfaces import IResponseMutator
from plone.caching.interfaces import ICacheInterceptor
from plone.caching.interfaces import IOperationLookup
from plone.caching.interfaces import ICacheSettings

class DefaultOperationLookup(object):
    """Default lookup, which uses the registry.
    
    Only override this if you have very special needs. The safest option is
    to use the ``mutatorMapping`` and ``interceptorMapping`` dictionaries in
    the registry to map rule sets to operations.
    """
    
    implements(IOperationLookup)
    adapts(Interface, Interface)

    def __init__(self, published, request):
        self.published = published
        self.request = request

    def getResponseMutator(self):
        
        registry = queryUtility(IRegistry)
        if registry is None:
            return None, None, None
    
        settings = registry.forInterface(ICacheSettings, check=False)
        if not settings.enabled:
            return None, None, None
    
        rule = lookup(self.published)
        if rule is None:
            return None, None, None
    
        if settings.mutatorMapping is None:
            return None, None, None
    
        name = settings.mutatorMapping.get(rule, None)
        if name is None:
            return None, None, None
    
        mutator = queryMultiAdapter((self.published, self.request), IResponseMutator, name=name)
        return rule, name, mutator
    
    def getCacheInterceptor(self):
    
        registry = queryUtility(IRegistry)
        if registry is None:
            return None, None, None
    
        settings = registry.forInterface(ICacheSettings, check=False)
        if not settings.enabled:
            return None, None, None
    
        rule = lookup(self.published)
        if rule is None:
            return None, None, None
    
        if settings.interceptorMapping is None:
            return None, None, None
    
        name = settings.interceptorMapping.get(rule, None)
        if name is None:
            return None, None, None
    
        interceptor = queryMultiAdapter((self.published, self.request), ICacheInterceptor, name=name)
        return rule, name, interceptor
