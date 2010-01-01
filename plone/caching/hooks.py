from zope.component import adapter
from ZPublisher.interfaces import IPubBeforeCommit
from plone.caching.lookup import getResponseMutator, getCacheInterceptor

from plone.caching.interfaces import X_CACHE_RULE_HEADER, X_MUTATOR_HEADER

@adapter(IPubBeforeCommit)
def mutateResponse(event):
    """Invoke a response mutator if one can be found
    """
    
    request = event.request
    published = request.get('PUBLISHED', None)
    if published is None:
        return
    
    rulename, operation, mutator = getResponseMutator(published, request)
    if mutator is not None:
        
        request.response.addHeader(X_CACHE_RULE_HEADER, rulename)
        request.response.addHeader(X_MUTATOR_HEADER, operation)
        
        mutator(rulename, request.response)


# TODO: Hook in cache interceptor

