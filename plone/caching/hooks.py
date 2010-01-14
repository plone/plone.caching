import types
import logging

from zope.interface import implements
from zope.interface import Interface

from zope.component import adapts, adapter, queryMultiAdapter, queryUtility

from ZPublisher.interfaces import IPubAfterTraversal
from ZODB.POSException import ConflictError

from plone.registry.interfaces import IRegistry

from plone.transformchain.interfaces import ITransform
from plone.transformchain.interfaces import DISABLE_TRANSFORM_REQUEST_KEY

from plone.caching.interfaces import X_CACHE_RULE_HEADER
from plone.caching.interfaces import X_MUTATOR_HEADER, X_INTERCEPTOR_HEADER

from plone.caching.interfaces import ICacheSettings
from plone.caching.interfaces import IRulesetLookup
from plone.caching.interfaces import IResponseMutator
from plone.caching.interfaces import ICacheInterceptor

logger = logging.getLogger('plone.caching')

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
    the exception. We set and lock the response status to avoid defaulting to
    a 404 exception.
    """
    
    try:
        request = event.request
        published = request.get('PUBLISHED', None)
        if published is None:
            return
        
        # If we get a method, try to look up its class
        if isinstance(published, types.MethodType):
            published = getattr(published, 'im_self', published)
        
        registry = queryUtility(IRegistry)
        if registry is None:
            return
        
        settings = registry.forInterface(ICacheSettings, check=False)
        if not settings.enabled:
            return
        
        if settings.interceptorMapping is None:
            return
        
        lookup = queryMultiAdapter((published, request,), IRulesetLookup)
        if lookup is None:
            return
        
        # From this point, we want to at least log
        rule = lookup()
        operation = None
        interceptor = None
        
        if rule is not None:
            operation = settings.interceptorMapping.get(rule, None)
            if operation is not None:
                interceptor = queryMultiAdapter((published, request), ICacheInterceptor, name=operation)
        
        logger.debug("Published: %s Ruleset: %s Interceptor: %s", repr(published), rule, operation)
        
        if interceptor is not None:
            
            request['plone.caching.intercepted'] = True
            
            request.response.addHeader(X_CACHE_RULE_HEADER, rule)
            request.response.addHeader(X_INTERCEPTOR_HEADER, operation)
            responseBody = interceptor(rule, request.response)
            
            if responseBody is not None:
                
                # The view is liable to have set a response status. Lock it
                # now so that it doesn't get set to 500 later.
                
                status = request.response.getStatus()
                if status:
                    request.response.setStatus(status, lock=True)
                
                # Stop any post-processing
                request.environ[DISABLE_TRANSFORM_REQUEST_KEY] = True
                
                raise Intercepted(status, responseBody)
    
    except ConflictError:
        raise
    except Intercepted:
        raise
    except:
        logging.exception("Swallowed exception in plone.caching IPubAfterTraversal event handler")

class MutatorTransform(object):
    """Transformation using plone.transformchain.
    
    This is registered at order 12000, i.e. "late". A typical transform
    chain order may include:
    
    * lxml transforms (e.g. plone.app.blocks, collectivexdv) => 8000-8999
    * gzip => 10000
    * caching => 12000
    
    This transformer is uncommon in that it doesn't actually change the
    response body. Instead, we look up response mutator caching operations,
    which can modify response headers and perform other caching functions.
    """
    
    implements(ITransform)
    adapts(Interface, Interface)
    
    order = 12000
    
    def __init__(self, published, request):
        self.published = published
        self.request = request
    
    def transformUnicode(self, result, encoding):
        self.mutate()
        return None
    
    def transformBytes(self, result, encoding):
        self.mutate()
        return None
    
    def transformIterable(self, result, encoding):
        self.mutate()
        return None
    
    def mutate(self):
        
        published = self.published
        if published is None:
            return
        
        request = self.request
        if request.get('plone.caching.intercepted', False):
            return
        
        # If we get a method, try to look up its class
        if isinstance(published, types.MethodType):
            published = getattr(published, 'im_self', published)
        
        registry = queryUtility(IRegistry)
        if registry is None:
            return
        
        settings = registry.forInterface(ICacheSettings, check=False)
        if not settings.enabled:
            return
        
        if settings.mutatorMapping is None:
            return
        
        lookup = queryMultiAdapter((published, request,), IRulesetLookup)
        if lookup is None:
            return
        
        # From this point, we want to at least log
        rule = lookup()
        operation = None
        mutator = None
        
        if rule is not None:
            operation = settings.mutatorMapping.get(rule, None)
            if operation is not None:
                mutator = queryMultiAdapter((published, request), IResponseMutator, name=operation)
        
        logger.debug("Published: %s Ruleset: %s Mutator: %s", repr(published), rule, operation)
        
        if mutator is not None:
            request.response.addHeader(X_CACHE_RULE_HEADER, rule)
            request.response.addHeader(X_MUTATOR_HEADER, operation)
            mutator(rule, request.response)

