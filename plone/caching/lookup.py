from zope.component import queryMultiAdapter, queryUtility

from plone.registry.interfaces import IRegistry

from z3c.caching.registry import lookup

from plone.caching.interfaces import IResponseMutator
from plone.caching.interfaces import ICacheInterceptor

from plone.caching.interfaces import ICacheSettings

def getResponseMutator(published, request):
    """Return a tuple ``(rulename, operation, mutator)`` where rulename is
    the matched caching rule, operation is the name of the mutation operation
    for that rule set, and mutator is an ``IResponseMutator`` for the
    published object (usually a view or similar). If caching is disabled or
    there is not enough context to find a response mutator, return
    ``(None, None, None,)``.
    """
    
    registry = queryUtility(IRegistry)
    if registry is None:
        return None, None, None
    
    settings = registry.forInterface(ICacheSettings, check=False)
    if not settings.enabled:
        return None, None, None
    
    rule = lookup(published)
    if rule is None:
        return None, None, None
    
    if settings.mutatorMapping is None:
        return None, None, None
    
    operation = settings.mutatorMapping.get(rule, None)
    if operation is None:
        return None, None, None
    
    return rule, operation, queryMultiAdapter((published, request), IResponseMutator, name=operation)
    
def getCacheInterceptor(published, request):
    """Return a tuple ``(rulename, operation, interceptor)`` where rulename is
    the matched caching rule, operation is the name of the interceptor
    operation for that rule set, and interceptor is an ``ICacheInterceptor``
    for the published object (usually a view or similar). If caching is
    disabled or there is not enough context to find a response interceptor,
    return ``(None, None, None,)``.
    """
    
    registry = queryUtility(IRegistry)
    if registry is None:
        return None, None, None
    
    settings = registry.forInterface(ICacheSettings, check=False)
    if not settings.enabled:
        return None, None, None
    
    rule = lookup(published)
    if rule is None:
        return None, None, None
    
    if settings.interceptorMapping is None:
        return None, None, None
    
    operation = settings.interceptorMapping.get(rule, None)
    if operation is None:
        return None, None, None
    
    return rule, operation, queryMultiAdapter((published, request), ICacheInterceptor, name=operation)
