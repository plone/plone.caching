import unittest

import zope.component.testing

from zope.component import adapts, provideUtility, provideAdapter, getUtility
from zope.interface import implements, Interface

from z3c.caching.registry import RulesetRegistry
import z3c.caching.registry

from plone.registry.interfaces import IRegistry

from plone.registry import Registry
from plone.registry.fieldfactory import persistentFieldAdapter

from plone.caching.interfaces import IResponseMutator
from plone.caching.interfaces import ICacheSettings

from plone.caching.hooks import mutateResponse

class DummyView(object):
    pass

class DummyResponse(dict):
    
    def addHeader(self, name, value):
        self.setdefault(name, []).append(value)

class DummyRequest(dict):
    def __init__(self, published, response):
        self['PUBLISHED'] = published
        self.response = response

class DummyEvent(object):
    def __init__(self, request):
        self.request = request

class TestHooks(unittest.TestCase):
    
    def setUp(self):
        provideAdapter(RulesetRegistry)
        provideAdapter(persistentFieldAdapter)
    
    def tearDown(self):
        zope.component.testing.tearDown()
    
    def test_mutateResponse_no_published_object(self):
        provideUtility(Registry(), IRegistry)
        registry = getUtility(IRegistry)
        registry.registerInterface(ICacheSettings)
        settings = registry.forInterface(ICacheSettings)
        settings.enabled = True
        
        view = DummyView()
        request = DummyRequest(view, DummyResponse())
        
        mutateResponse(DummyEvent(request))
        self.assertEquals({'PUBLISHED': view}, dict(request))
        self.assertEquals({}, dict(request.response))
    
    def test_mutateResponse_no_registry(self):
        view = DummyView()
        request = DummyRequest(view, DummyResponse())
        
        mutateResponse(DummyEvent(request))
        
        self.assertEquals({'PUBLISHED': view}, dict(request))
        self.assertEquals({}, dict(request.response))
    
    def test_mutateResponse_no_cache_rule(self):
        provideUtility(Registry(), IRegistry)
        registry = getUtility(IRegistry)
        registry.registerInterface(ICacheSettings)
        settings = registry.forInterface(ICacheSettings)
        settings.enabled = True
        
        view = DummyView()
        request = DummyRequest(view, DummyResponse())
        mutateResponse(DummyEvent(request))
        self.assertEquals({'PUBLISHED': view}, dict(request))
        self.assertEquals({}, dict(request.response))
        
    def test_mutateResponse_no_mapping(self):
        provideUtility(Registry(), IRegistry)
        registry = getUtility(IRegistry)
        registry.registerInterface(ICacheSettings)
        settings = registry.forInterface(ICacheSettings)
        settings.enabled = True
        
        z3c.caching.registry.register(DummyView, 'testrule')
        
        view = DummyView()
        request = DummyRequest(view, DummyResponse())
        mutateResponse(DummyEvent(request))
        self.assertEquals({'PUBLISHED': view}, dict(request))
        self.assertEquals({}, dict(request.response))
    
    def test_mutateResponse_operation_not_found(self):
        provideUtility(Registry(), IRegistry)
        registry = getUtility(IRegistry)
        registry.registerInterface(ICacheSettings)
        settings = registry.forInterface(ICacheSettings)
        settings.enabled = True
        
        z3c.caching.registry.register(DummyView, 'testrule')
        settings.mutatorMapping = {'testrule': 'notfound'}
        
        view = DummyView()
        request = DummyRequest(view, DummyResponse())
        mutateResponse(DummyEvent(request))
        self.assertEquals({'PUBLISHED': view}, dict(request))
        self.assertEquals({}, dict(request.response))
    
    def test_mutateResponse_match(self):
        provideUtility(Registry(), IRegistry)
        registry = getUtility(IRegistry)
        registry.registerInterface(ICacheSettings)
        settings = registry.forInterface(ICacheSettings)
        settings.enabled = True
        
        z3c.caching.registry.register(DummyView, 'testrule')
        settings.mutatorMapping = {'testrule': 'mutator'}
        
        class DummyMutator(object):
            implements(IResponseMutator)
            adapts(Interface, Interface)
            
            def __init__(self, published, request):
                self.published = published
                self.request = request
            
            def __call__(self, rulename, response):
                response.addHeader('X-Cache-Foo', 'test')
        
        provideAdapter(DummyMutator, name="mutator")
        
        view = DummyView()
        request = DummyRequest(view, DummyResponse())
        mutateResponse(DummyEvent(request))
        self.assertEquals({'PUBLISHED': view}, dict(request))
        self.assertEquals({'X-Cache-Rule': ['testrule'],
                           'X-Cache-Operation': ['mutator'],
                           'X-Cache-Foo': ['test']}, dict(request.response))
    
    def test_mutateResponse_off_switch(self):
        provideUtility(Registry(), IRegistry)
        registry = getUtility(IRegistry)
        registry.registerInterface(ICacheSettings)
        settings = registry.forInterface(ICacheSettings)
        settings.enabled = False
        
        z3c.caching.registry.register(DummyView, 'testrule')
        settings.mutatorMapping = {'testrule': 'mutator'}
        
        class DummyMutator(object):
            implements(IResponseMutator)
            adapts(Interface, Interface)
            
            def __init__(self, published, request):
                self.published = published
                self.request = request
            
            def __call__(self, rulename, response):
                response['X-Mutated'] = rulename
        
        provideAdapter(DummyMutator, name="mutator")
        
        view = DummyView()
        request = DummyRequest(view, DummyResponse())
        mutateResponse(DummyEvent(request))
        self.assertEquals({'PUBLISHED': view}, dict(request))
        self.assertEquals({}, dict(request.response))
    
def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)