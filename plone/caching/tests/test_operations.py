import unittest

import zope.component.testing

from zope.interface import implements
from zope.interface import Interface
from z3c.caching.registry import RulesetRegistry

from zope.component import provideUtility
from zope.component import provideAdapter
from zope.component import adapts

from plone.registry.interfaces import IRegistry
from plone.registry import Registry, Record
from plone.registry import field

from plone.caching.operations import Chain
from plone.caching.interfaces import IResponseMutator

_marker = object()

class DummyView(object):
    pass

class DummyResponse(dict):
    
    def addHeader(self, name, value):
        self.setdefault(name, []).append(value)

class DummyRequest(dict):
    def __init__(self, published, response):
        self['PUBLISHED'] = published
        self.response = response


class TestChain(unittest.TestCase):
    
    def setUp(self):
        self.registry = Registry()
        provideUtility(self.registry, IRegistry)
        provideAdapter(RulesetRegistry)
    
    def tearDown(self):
        zope.component.testing.tearDown()
    
    def test_no_option(self):
        view = DummyView()
        request = DummyRequest(view, DummyResponse())
        
        chain = Chain(view, request)
        chain('testrule', request.response)
        
        self.assertEquals({'PUBLISHED': view}, dict(request))
        self.assertEquals({}, dict(request.response))
    
    def test_operations_list_not_set(self):
        
        self.registry.records["%s.operations" % Chain.prefix] = Record(field.List())
        
        view = DummyView()
        request = DummyRequest(view, DummyResponse())
        
        chain = Chain(view, request)
        chain('testrule', request.response)
        
        self.assertEquals({'PUBLISHED': view}, dict(request))
        self.assertEquals({}, dict(request.response))
    
    def test_operations_empty(self):
        
        self.registry.records["%s.operations" % Chain.prefix] = Record(field.List(), [])
        
        view = DummyView()
        request = DummyRequest(view, DummyResponse())
        
        chain = Chain(view, request)
        chain('testrule', request.response)
        
        self.assertEquals({'PUBLISHED': view}, dict(request))
        self.assertEquals({}, dict(request.response))
    
    def test_chained_operations_not_found(self):
        
        self.registry.records["%s.operations" % Chain.prefix] = Record(field.List(), ['op1'])
        
        view = DummyView()
        request = DummyRequest(view, DummyResponse())
        
        chain = Chain(view, request)
        chain('testrule', request.response)
        
        self.assertEquals({'PUBLISHED': view}, dict(request))
        self.assertEquals({}, dict(request.response))
    
    def test_multiple_operations_one_found(self):
        self.registry.records["%s.operations" % Chain.prefix] = Record(field.List(), ['op1', 'op2'])
        
        view = DummyView()
        request = DummyRequest(view, DummyResponse())
        
        class DummyMutator(object):
            implements(IResponseMutator)
            adapts(Interface, Interface)
            
            def __init__(self, published, request):
                self.published = published
                self.request = request
            
            def __call__(self, rulename, response):
                response['X-Mutated'] = rulename
        
        provideAdapter(DummyMutator, name="op2")
        
        chain = Chain(view, request)
        chain('testrule', request.response)
        
        self.assertEquals({'PUBLISHED': view}, dict(request))
        self.assertEquals({'X-Mutated': 'testrule',
                           'X-Cache-Chain-Operation': ['op2']}, dict(request.response))

def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
