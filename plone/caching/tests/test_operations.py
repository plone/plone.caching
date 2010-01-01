import unittest

import zope.component.testing

from zope.component import provideUtility, getUtility

from plone.registry.interfaces import IRegistry
from plone.registry import Registry, Record
from plone.registry import field

from plone.caching.operations import Chain

_marker = object()

class TestChain(unittest.TestCase):
    
    def setUp(self):
        self.registry = Registry()
        provideUtility(registry, IRegistry)
    
    def tearDown(self):
        zope.component.testing.tearDown()
    
    # TODO - complete tests
    
def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
