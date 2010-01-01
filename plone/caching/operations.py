from zope.interface import implements, classProvides, Interface
from zope.component import adapts, queryMultiAdapter

from plone.caching.interfaces import IResponseMutator
from plone.caching.interfaces import IResponseMutatorType
from plone.caching.interfaces import _

from plone.caching.utils import lookupOptions

class Chain(object):
    """Caching mutator which chains together several other mutators.
    
    The names of the mutators to execute are found in the ``plone.registry``
    option ``plone.caching.operations.chain.operations`` by default, and can
    be customised on a per-rule basis with
    ``plone.caching.operations.chain.${rulename}.chain``.
    
    The option must be a sequence type (e.g. a ``List``).
    """
    
    implements(IResponseMutator)
    adapts(Interface, Interface)
    
    # Type metadata
    classProvides(IResponseMutatorType)
    
    title = _(u"Chain")
    description = _(u"Allows multiple operations to be chained together")
    prefix = 'plone.caching.operations.chain'
    options = ('operations',)
    
    def __init__(self, published, request):
        self.published = published
        self.request = request
        
    def __call__(self, rulename, response):
        options = lookupOptions(self.__class__, rulename)
        
        if options['operations']:
            for operation in options['operations']:
                
                mutator = queryMultiAdapter((self.published, self.request),
                                            IResponseMutator, name=operation)
                
                if mutator is not None:
                    response.addHeader('X-Cache-Chain-Operation', operation)
                    mutator(rulename, response)

