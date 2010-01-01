import unittest

import zope.component.testing

from zope.component import provideUtility, getUtility

from plone.registry.interfaces import IRegistry
from plone.registry import Registry, Record
from plone.registry import field

from plone.caching.utils import lookupOption

_marker = object()

class TestLookupOption(unittest.TestCase):
    
    def tearDown(self):
        zope.component.testing.tearDown()
    
    def test_lookupOption_no_registry(self):
        result = lookupOption('plone.caching.tests', 'testrule', 'test', default=_marker)
        self.failUnless(result is _marker)
        
    def test_lookupOption_no_record(self):
        provideUtility(Registry(), IRegistry)
        
        result = lookupOption('plone.caching.tests', 'testrule', 'test', default=_marker)
        self.failUnless(result is _marker)
    
    def test_lookupOption_default(self):
        provideUtility(Registry(), IRegistry)
        registry = getUtility(IRegistry)
        
        registry.records['plone.caching.tests.test']  = Record(field.TextLine(), u"default")
        
        result = lookupOption('plone.caching.tests', 'testrule', 'test', default=_marker)
        self.assertEquals(u"default", result)
    
    def test_lookupOption_override(self):
        provideUtility(Registry(), IRegistry)
        registry = getUtility(IRegistry)
        
        registry.records['plone.caching.tests.test']  = Record(field.TextLine(), u"default")
        registry.records['plone.caching.tests.testrule.test']  = Record(field.TextLine(), u"override")
        
        result = lookupOption('plone.caching.tests', 'testrule', 'test', default=_marker)
        self.assertEquals(u"override", result)
    
def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
