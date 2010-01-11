import types
import logging

from zope.component import adapter, queryMultiAdapter

from ZPublisher.interfaces import IPubBeforeCommit, IPubAfterTraversal
from ZODB.POSException import ConflictError

from plone.caching.interfaces import X_CACHE_RULE_HEADER
from plone.caching.interfaces import X_MUTATOR_HEADER, X_INTERCEPTOR_HEADER
from plone.caching.interfaces import IOperationLookup

logger = logging.getLogger('plone.caching')

@adapter(IPubBeforeCommit)
def mutateResponse(event):
    """Invoke a response mutator if one can be found
    """
    
    try:
        request = event.request
        published = request.get('PUBLISHED', None)
        if published is None:
            return
        
        # If we get a method, try to look up its class
        if isinstance(published, types.MethodType):
            published = getattr(published, 'im_self', published)
        
        lookup = queryMultiAdapter((published, request,), IOperationLookup)
        rulename, operation, mutator = lookup.getResponseMutator()
        
        logger.debug("Published: %s Ruleset: %s Mutator: %s", repr(published), rulename, operation)
        
        if mutator is not None:
        
            request.response.addHeader(X_CACHE_RULE_HEADER, rulename)
            request.response.addHeader(X_MUTATOR_HEADER, operation)
        
            mutator(rulename, request.response)
    except ConflictError:
        raise
    except:
        logging.exception("Swallowed exception in plone.caching IPubBeforeCommit event handler")
    
class Intercepted(Exception):
    """Exception raised in order to abort regular processing before the
    published resource (e.g. a view) is called, and render a specific response
    body and status provided by a cache interceptor instead.
    """
    
    responseBody = None
    status = None
    
    def __init__(self, status=304, responseBody=u""):
        self.status = status
        self.responseBody = responseBody

class InterceptorResponse(object):
    """View for the Intercepted exception, serving to return an empty
    response in the case of an intercepted response.
    """
    
    def __init__(self, context, request):
        self.context = context
        self.request = request
        
    def __call__(self):
        return self.context.responseBody

@adapter(IPubAfterTraversal)
def intercept(event):
    """Invoke a request interceptor if one can be found.
    
    To properly abort request processing, this will raise an exception. The
    actual response (typically an empty response) is then set via a view on
    the exception. The exception type name is used to determine the response
    status (so a NotFound exception becomes a 404, say). Therefore, we attempt
    to look up a suitable exception type.
    """
    
    try:
        request = event.request
        published = request.get('PUBLISHED', None)
        if published is None:
            return
        
        # If we get a method, try to look up its class
        if isinstance(published, types.MethodType):
            published = getattr(published, 'im_self', published)
        
        lookup = queryMultiAdapter((published, request,), IOperationLookup)
        rulename, operation, interceptor = lookup.getCacheInterceptor()
        
        logger.debug("Published: %s Ruleset: %s Interceptor: %s", repr(published), rulename, operation)
        
        if interceptor is not None:
        
            request.response.addHeader(X_CACHE_RULE_HEADER, rulename)
            request.response.addHeader(X_INTERCEPTOR_HEADER, operation)
        
            responseBody = interceptor(rulename, request.response)
            if responseBody is not None:
                
                # The view is liable to have set a response status. Lock it
                # now so that it doesn't get set to 500 later.
                
                status = request.response.getStatus()
                if not status:
                    status = 304
                
                request.response.setStatus(status, lock=True)
                raise Intercepted(status, responseBody)
    
    except ConflictError:
        raise
    except Intercepted:
        raise
    except:
        logging.exception("Swallowed exception in plone.caching IPubAfterTraversal event handler")
