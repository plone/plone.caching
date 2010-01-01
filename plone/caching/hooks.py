from zope.component import adapter
from ZPublisher.interfaces import IPubBeforeCommit, IPubAfterTraversal
from plone.caching.lookup import getResponseMutator, getCacheInterceptor

from plone.caching.interfaces import X_CACHE_RULE_HEADER
from plone.caching.interfaces import X_MUTATOR_HEADER, X_INTERCEPTOR_HEADER

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

@adapter(IPubAfterTraversal)
def intercept(event):
    """Invoke a request interceptor if one can be found.
    
    To properly abort request processing, this will raise an exception. The
    actual response (typically an empty response) is then set via a view on
    the exception.
    """
    
    request = event.request
    published = request.get('PUBLISHED', None)
    if published is None:
        return
    
    rulename, operation, interceptor = getCacheInterceptor(published, request)
    if interceptor is not None:
        
        request.response.addHeader(X_CACHE_RULE_HEADER, rulename)
        request.response.addHeader(X_INTERCEPTOR_HEADER, operation)
        
        if interceptor(rulename, request.response):
            raise InterceptorControlFlowException()

class InterceptorControlFlowException(Exception):
    """Exception raised in order to abort regular processing and attempt a 304
    type response instead.
    """

class InterceptorResponse(object):
    """View for InterceptorControlFlowException, serving to return an empty
    response in the case of an intercepted response.
    """
    
    def __init__(self, context, request):
        self.context = context
        self.request = request
        
    def __call__(self):
        return u''
