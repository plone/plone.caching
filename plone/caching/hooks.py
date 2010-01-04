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
        
        if mutator is not None:
        
            request.response.addHeader(X_CACHE_RULE_HEADER, rulename)
            request.response.addHeader(X_MUTATOR_HEADER, operation)
        
            mutator(rulename, request.response)
    except ConflictError:
        raise
    except:
        logging.exception("Swallowed exception in plone.caching IPubBeforeCommit event handler")
    
class InterceptorControlFlowException(Exception):
    """Exception raised in order to abort regular processing and render a
    specific response body instead. The actual exception raised will be a
    subtype of this with a named indicating the HTTP status. Zope's
    HTTPResponse uses the exception name to look up status.
    """
    
    responseBody = u""

class OK(InterceptorControlFlowException):
    pass

class MovedPermanently(InterceptorControlFlowException):
    pass

class MovedTemporarily(InterceptorControlFlowException):
    pass

class NotModified(InterceptorControlFlowException):
    pass

class UseProxy(InterceptorControlFlowException):
    pass

class TemporaryRedirect(InterceptorControlFlowException):
    pass

class Unauthorized(InterceptorControlFlowException):
    pass

class Forbidden(InterceptorControlFlowException):
    pass

class NotFound(InterceptorControlFlowException):
    pass

class ProxyAuthenticationRequired(InterceptorControlFlowException):
    pass

status_exception_map = {
    200: OK,
    301: MovedPermanently,
    302: MovedTemporarily,
    304: NotModified,
    305: UseProxy,
    307: TemporaryRedirect,
    401: Unauthorized,
    403: Forbidden,
    404: NotFound, 
    407: ProxyAuthenticationRequired,
}

class InterceptorResponse(object):
    """View for InterceptorControlFlowException, serving to return an empty
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
        
        if interceptor is not None:
        
            request.response.addHeader(X_CACHE_RULE_HEADER, rulename)
            request.response.addHeader(X_INTERCEPTOR_HEADER, operation)
        
            responseBody = interceptor(rulename, request.response)
            if responseBody is not None:
                # Try to find a suitable exception
                
                status = event.request.response.getStatus()
                exceptionType = status_exception_map.get(status, None)
                if exceptionType is None:
                    # If we can't find it, generate a class object with an
                    # appropriate __name__. This will show up in the error
                    # log and be generally confusing, but what the heck
                    exceptionType = type(str(event.request.response.getStatus()),
                           (InterceptorControlFlowException,), {})
                
                exception = exceptionType()
                exception.responseBody = responseBody
                raise exception
    
    except ConflictError:
        raise
    except InterceptorControlFlowException:
        raise
    except:
        logging.exception("Swallowed exception in plone.caching IPubAfterTraversal event handler")
