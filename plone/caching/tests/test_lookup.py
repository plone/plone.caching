import unittest

import zope.component.testing

from zope.component import adapts, provideUtility, provideAdapter, getUtility
from zope.interface import implements, Interface

from plone.caching.interfaces import IResponseMutator
from plone.caching.interfaces import ICacheInterceptor

from z3c.caching.registry import RulesetRegistry
import z3c.caching.registry

from plone.registry.interfaces import IRegistry

from plone.registry import Registry
from plone.registry.fieldfactory import persistentFieldAdapter

from plone.caching.interfaces import ICacheSettings

from plone.caching.lookup import DefaultOperationLookup

class DummyView(object):
    pass

class DummyResponse(dict):
    
    def addHeader(self, name, value):
        self.setdefault(name, []).append(value)

class DummyRequest(dict):
    def __init__(self, published, response):
        self['PUBLISHED'] = published
        self.response = response

class TestLookupResponseMutator(unittest.TestCase):
    
    def setUp(self):
        provideAdapter(RulesetRegistry)
        provideAdapter(persistentFieldAdapter)
    
    def tearDown(self):
        zope.component.testing.tearDown()
    
    def test_getResponseMutator_no_registry(self):
        view = DummyView()
        request = DummyRequest(view, DummyResponse())
        
        self.assertEquals((None, None, None,),
                DefaultOperationLookup(view, request).getResponseMutator())
        
    def test_getResponseMutator_no_cache_rule(self):
        provideUtility(Registry(), IRegistry)
        registry = getUtility(IRegistry)
        registry.registerInterface(ICacheSettings)
        settings = registry.forInterface(ICacheSettings)
        settings.enabled = True
        
        view = DummyView()
        request = DummyRequest(view, DummyResponse())
        self.assertEquals((None, None, None,),
                DefaultOperationLookup(view, request).getResponseMutator())
        
    def test_getResponseMutator_no_mapping(self):
        provideUtility(Registry(), IRegistry)
        registry = getUtility(IRegistry)
        registry.registerInterface(ICacheSettings)
        settings = registry.forInterface(ICacheSettings)
        settings.enabled = True
        
        z3c.caching.registry.register(DummyView, 'testrule')
        
        view = DummyView()
        request = DummyRequest(view, DummyResponse())
        self.assertEquals(('testrule', None, None,),
                DefaultOperationLookup(view, request).getResponseMutator())
    
    def test_getResponseMutator_operation_not_found(self):
        provideUtility(Registry(), IRegistry)
        registry = getUtility(IRegistry)
        registry.registerInterface(ICacheSettings)
        settings = registry.forInterface(ICacheSettings)
        settings.enabled = True
        
        z3c.caching.registry.register(DummyView, 'testrule')
        settings.mutatorMapping = {'testrule': 'notfound'}
        
        view = DummyView()
        request = DummyRequest(view, DummyResponse())
        self.assertEquals(('testrule', 'notfound', None,),
                DefaultOperationLookup(view, request).getResponseMutator())
    
    def test_getResponseMutator_match(self):
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
        
        (rule, operation, mutator,) = DefaultOperationLookup(view, request).getResponseMutator()
        self.assertEquals('testrule', rule)
        self.assertEquals('mutator', operation)
        self.failUnless(isinstance(mutator, DummyMutator))
    
    def test_getResponseMutator_off_switch(self):
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
        self.assertEquals((None, None, None,), 
                DefaultOperationLookup(view, request).getResponseMutator())

class TestLookupCacheInterceptor(unittest.TestCase):
    
    def setUp(self):
        provideAdapter(RulesetRegistry)
        provideAdapter(persistentFieldAdapter)
    
    def tearDown(self):
        zope.component.testing.tearDown()
    
    def test_getCacheInterceptor_no_registry(self):
        view = DummyView()
        request = DummyRequest(view, DummyResponse())
        
        self.assertEquals((None, None, None,),
                DefaultOperationLookup(view, request).getCacheInterceptor())
        
    def test_getCacheInterceptor_no_cache_rule(self):
        provideUtility(Registry(), IRegistry)
        registry = getUtility(IRegistry)
        registry.registerInterface(ICacheSettings)
        settings = registry.forInterface(ICacheSettings)
        settings.enabled = True
        
        view = DummyView()
        request = DummyRequest(view, DummyResponse())
        self.assertEquals((None, None, None,),
                DefaultOperationLookup(view, request).getCacheInterceptor())
        
    def test_getCacheInterceptor_no_mapping(self):
        provideUtility(Registry(), IRegistry)
        registry = getUtility(IRegistry)
        registry.registerInterface(ICacheSettings)
        settings = registry.forInterface(ICacheSettings)
        settings.enabled = True
        
        z3c.caching.registry.register(DummyView, 'testrule')
        
        view = DummyView()
        request = DummyRequest(view, DummyResponse())
        self.assertEquals(('testrule', None, None,),
                DefaultOperationLookup(view, request).getCacheInterceptor())
    
    def test_getCacheInterceptor_operation_not_found(self):
        provideUtility(Registry(), IRegistry)
        registry = getUtility(IRegistry)
        registry.registerInterface(ICacheSettings)
        settings = registry.forInterface(ICacheSettings)
        settings.enabled = True
        
        z3c.caching.registry.register(DummyView, 'testrule')
        settings.interceptorMapping = {'testrule': 'notfound'}
        
        view = DummyView()
        request = DummyRequest(view, DummyResponse())
        self.assertEquals(('testrule', 'notfound', None,),
                DefaultOperationLookup(view, request).getCacheInterceptor())
    
    def test_getCacheInterceptor_match(self):
        provideUtility(Registry(), IRegistry)
        registry = getUtility(IRegistry)
        registry.registerInterface(ICacheSettings)
        settings = registry.forInterface(ICacheSettings)
        settings.enabled = True
        
        z3c.caching.registry.register(DummyView, 'testrule')
        settings.interceptorMapping = {'testrule': 'interceptor'}
        
        class DummyInterceptor(object):
            implements(ICacheInterceptor)
            adapts(Interface, Interface)
            
            def __init__(self, published, request):
                self.published = published
                self.request = request
            
            def __call__(self, rulename, response):
                return False
        
        provideAdapter(DummyInterceptor, name="interceptor")
        
        view = DummyView()
        request = DummyRequest(view, DummyResponse())
        
        (rule, operation, interceptor,) = DefaultOperationLookup(view, request).getCacheInterceptor()
        self.assertEquals('testrule', rule)
        self.assertEquals('interceptor', operation)
        self.failUnless(isinstance(interceptor, DummyInterceptor))
    
    def test_getCacheInterceptor_off_switch(self):
        provideUtility(Registry(), IRegistry)
        registry = getUtility(IRegistry)
        registry.registerInterface(ICacheSettings)
        settings = registry.forInterface(ICacheSettings)
        settings.enabled = False
        
        z3c.caching.registry.register(DummyView, 'testrule')
        settings.mutatorMapping = {'testrule': 'mutator'}
        
        class DummyInterceptor(object):
            implements(ICacheInterceptor)
            adapts(Interface, Interface)
            
            def __init__(self, published, request):
                self.published = published
                self.request = request
            
            def __call__(self, rulename, response):
                return False
        
        provideAdapter(DummyInterceptor, name="interceptor")
        
        view = DummyView()
        request = DummyRequest(view, DummyResponse())
        self.assertEquals((None, None, None,),
                DefaultOperationLookup(view, request).getCacheInterceptor())

def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)