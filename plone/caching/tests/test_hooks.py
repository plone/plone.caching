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
from plone.caching.interfaces import ICacheInterceptor

from plone.caching.interfaces import ICacheSettings

from plone.caching.lookup import DefaultRulesetLookup

from plone.caching.hooks import mutateResponse, intercept
from plone.caching.hooks import Intercepted

class DummyView(object):
    pass

class DummyResource(object):
    def index_html(self):
        return 'binary data'

class DummyResponse(dict):
    
    locked = None
    
    def addHeader(self, name, value):
        self.setdefault(name, []).append(value)
    
    def setStatus(self, value, lock=None):
        self.status = value
        if lock is not None:
            self.locked = lock
    def getStatus(self):
        return self.status
    
class DummyRequest(dict):
    def __init__(self, published, response):
        self['PUBLISHED'] = published
        self.response = response

class DummyEvent(object):
    def __init__(self, request):
        self.request = request

class TestMutateResponse(unittest.TestCase):
    
    def setUp(self):
        provideAdapter(RulesetRegistry)
        provideAdapter(DefaultRulesetLookup)
        provideAdapter(persistentFieldAdapter)
    
    def tearDown(self):
        zope.component.testing.tearDown()
    
    def test_no_published_object(self):
        provideUtility(Registry(), IRegistry)
        registry = getUtility(IRegistry)
        registry.registerInterface(ICacheSettings)
        settings = registry.forInterface(ICacheSettings)
        settings.enabled = True
        
        request = DummyRequest(None, DummyResponse())
        
        mutateResponse(DummyEvent(request))
        self.assertEquals({'PUBLISHED': None}, dict(request))
        self.assertEquals({}, dict(request.response))
    
    def test_no_registry(self):
        view = DummyView()
        request = DummyRequest(view, DummyResponse())
        
        mutateResponse(DummyEvent(request))
        
        self.assertEquals({'PUBLISHED': view}, dict(request))
        self.assertEquals({}, dict(request.response))
    
    def test_no_records(self):
        provideUtility(Registry(), IRegistry)
        view = DummyView()
        request = DummyRequest(view, DummyResponse())
        
        mutateResponse(DummyEvent(request))
        
        self.assertEquals({'PUBLISHED': view}, dict(request))
        self.assertEquals({}, dict(request.response))
    
    def test_no_cache_rule(self):
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
        
    def test_no_mapping(self):
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
    
    def test_operation_not_found(self):
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
    
    def test_match(self):
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
                           'X-Cache-Mutator': ['mutator'],
                           'X-Cache-Foo': ['test']}, dict(request.response))
    
    def test_match_method(self):
        provideUtility(Registry(), IRegistry)
        registry = getUtility(IRegistry)
        registry.registerInterface(ICacheSettings)
        settings = registry.forInterface(ICacheSettings)
        settings.enabled = True
        
        z3c.caching.registry.register(DummyResource, 'testrule')
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
        
        resource = DummyResource()
        request = DummyRequest(resource.index_html, DummyResponse())
        mutateResponse(DummyEvent(request))
        self.assertEquals({'PUBLISHED': resource.index_html}, dict(request))
        self.assertEquals({'X-Cache-Rule': ['testrule'],
                           'X-Cache-Mutator': ['mutator'],
                           'X-Cache-Foo': ['test']}, dict(request.response))
    
    def test_off_switch(self):
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

class TestIntercept(unittest.TestCase):
    
    def setUp(self):
        provideAdapter(RulesetRegistry)
        provideAdapter(DefaultRulesetLookup)
        provideAdapter(persistentFieldAdapter)
    
    def tearDown(self):
        zope.component.testing.tearDown()
    
    def test_no_published_object(self):
        provideUtility(Registry(), IRegistry)
        registry = getUtility(IRegistry)
        registry.registerInterface(ICacheSettings)
        settings = registry.forInterface(ICacheSettings)
        settings.enabled = True
        
        request = DummyRequest(None, DummyResponse())
        
        intercept(DummyEvent(request))
        self.assertEquals({'PUBLISHED': None}, dict(request))
        self.assertEquals({}, dict(request.response))
    
    def test_no_registry(self):
        view = DummyView()
        request = DummyRequest(view, DummyResponse())
        
        intercept(DummyEvent(request))
        
        self.assertEquals({'PUBLISHED': view}, dict(request))
        self.assertEquals({}, dict(request.response))
    
    def test_no_records(self):
        provideUtility(Registry(), IRegistry)
        
        view = DummyView()
        request = DummyRequest(view, DummyResponse())
        
        intercept(DummyEvent(request))
        
        self.assertEquals({'PUBLISHED': view}, dict(request))
        self.assertEquals({}, dict(request.response))
    
    
    def test_no_cache_rule(self):
        provideUtility(Registry(), IRegistry)
        registry = getUtility(IRegistry)
        registry.registerInterface(ICacheSettings)
        settings = registry.forInterface(ICacheSettings)
        settings.enabled = True
        
        view = DummyView()
        request = DummyRequest(view, DummyResponse())
        intercept(DummyEvent(request))
        
        self.assertEquals({'PUBLISHED': view}, dict(request))
        self.assertEquals({}, dict(request.response))
        
    def test_no_mapping(self):
        provideUtility(Registry(), IRegistry)
        registry = getUtility(IRegistry)
        registry.registerInterface(ICacheSettings)
        settings = registry.forInterface(ICacheSettings)
        settings.enabled = True
        
        z3c.caching.registry.register(DummyView, 'testrule')
        
        view = DummyView()
        request = DummyRequest(view, DummyResponse())
        intercept(DummyEvent(request))
        
        self.assertEquals({'PUBLISHED': view}, dict(request))
        self.assertEquals({}, dict(request.response))
    
    def test_operation_not_found(self):
        provideUtility(Registry(), IRegistry)
        registry = getUtility(IRegistry)
        registry.registerInterface(ICacheSettings)
        settings = registry.forInterface(ICacheSettings)
        settings.enabled = True
        
        z3c.caching.registry.register(DummyView, 'testrule')
        settings.interceptorMapping = {'testrule': 'notfound'}
        
        view = DummyView()
        request = DummyRequest(view, DummyResponse())
        intercept(DummyEvent(request))
        
        self.assertEquals({'PUBLISHED': view}, dict(request))
        self.assertEquals({}, dict(request.response))
    
    def test_match_abort(self):
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
                response.addHeader('X-Cache-Foo', 'test')
                return None
        
        provideAdapter(DummyInterceptor, name="interceptor")
        
        view = DummyView()
        request = DummyRequest(view, DummyResponse())
        intercept(DummyEvent(request))
        self.assertEquals({'PUBLISHED': view}, dict(request))
        self.assertEquals({'X-Cache-Rule': ['testrule'],
                           'X-Cache-Interceptor': ['interceptor'],
                           'X-Cache-Foo': ['test']}, dict(request.response))
    
    def test_match_body(self):
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
                response.addHeader('X-Cache-Foo', 'test')
                response.setStatus(304)
                return u"dummy"
        
        provideAdapter(DummyInterceptor, name="interceptor")
        
        view = DummyView()
        request = DummyRequest(view, DummyResponse())
        try:
            intercept(DummyEvent(request))
            self.fail()
        except Intercepted, e:
            self.assertEquals(u"dummy", e.responseBody)
            self.assertEquals(304, e.status)
            self.assertEquals(304, request.response.status)
            self.assertEquals(True, request.response.locked)
        except Exception, e:
            self.fail(str(e))
            
        self.assertEquals({'PUBLISHED': view}, dict(request))
        self.assertEquals({'X-Cache-Rule': ['testrule'],
                           'X-Cache-Interceptor': ['interceptor'],
                           'X-Cache-Foo': ['test']}, dict(request.response))
    
    def test_match_body_method(self):
        provideUtility(Registry(), IRegistry)
        registry = getUtility(IRegistry)
        registry.registerInterface(ICacheSettings)
        settings = registry.forInterface(ICacheSettings)
        settings.enabled = True
        
        z3c.caching.registry.register(DummyResource, 'testrule')
        settings.interceptorMapping = {'testrule': 'interceptor'}
        
        class DummyInterceptor(object):
            implements(ICacheInterceptor)
            adapts(Interface, Interface)
            
            def __init__(self, published, request):
                self.published = published
                self.request = request
            
            def __call__(self, rulename, response):
                response.addHeader('X-Cache-Foo', 'test')
                response.setStatus(200)
                return u"dummy"
        
        provideAdapter(DummyInterceptor, name="interceptor")
        
        resource = DummyResource()
        request = DummyRequest(resource.index_html, DummyResponse())
        try:
            intercept(DummyEvent(request))
            self.fail()
        except Intercepted, e:
            self.assertEquals(u"dummy", e.responseBody)
            self.assertEquals(200, e.status)
            self.assertEquals(200, request.response.status)
            self.assertEquals(True, request.response.locked)
        except Exception, e:
            self.fail(str(e))
            
        self.assertEquals({'PUBLISHED': resource.index_html}, dict(request))
        self.assertEquals({'X-Cache-Rule': ['testrule'],
                           'X-Cache-Interceptor': ['interceptor'],
                           'X-Cache-Foo': ['test']}, dict(request.response))

    def test_off_switch(self):
        provideUtility(Registry(), IRegistry)
        registry = getUtility(IRegistry)
        registry.registerInterface(ICacheSettings)
        settings = registry.forInterface(ICacheSettings)
        settings.enabled = False
        
        z3c.caching.registry.register(DummyView, 'testrule')
        settings.interceptorMapping = {'testrule': 'interceptor'}
        
        class DummyInterceptor(object):
            implements(ICacheInterceptor)
            adapts(Interface, Interface)
            
            def __init__(self, published, request):
                self.published = published
                self.request = request
            
            def __call__(self, rulename, response):
                response.addHeader('X-Cache-Foo', 'test')
                return u"dummy"
        
        provideAdapter(DummyInterceptor, name="interceptor")
        
        view = DummyView()
        request = DummyRequest(view, DummyResponse())
        intercept(DummyEvent(request))
        self.assertEquals({'PUBLISHED': view}, dict(request))
        self.assertEquals({}, dict(request.response))
    
def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)