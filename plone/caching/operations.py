from zope.interface import implements, Interface
from zope.component import adapts

from z3c.caching.interfaces import IResponseMutator

from plone.caching.lookup import getResponseMutator
from plone.caching.utils import lookupOption

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
    
    prefix = 'plone.caching.operations.chain'
    
    def __init__(self, published, request):
        self.published = published
        self.request = request
        
    def __call__(self, rulename, response):
        operations = lookupOption(self.prefix, rulename, 'operations', [])
        for operation in operations:
            oprulename, opname, mutator = getResponseMutator(self.published, self.request)
            
            response.addHeader('X-Cache-Chain-Operation', opname)
            operation(rulename, response)

