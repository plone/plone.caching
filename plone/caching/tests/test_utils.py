from plone.caching.interfaces import ICachingOperationType
from plone.caching.utils import lookupOption
from plone.caching.utils import lookupOptions
from plone.registry import field
from plone.registry import FieldRef
from plone.registry import Record
from plone.registry import Registry
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from zope.component import provideUtility
from zope.interface import provider

import unittest
import zope.component.testing


_marker = object()


class TestLookupOption(unittest.TestCase):
    def tearDown(self):
        zope.component.testing.tearDown()

    def test_lookupOption_no_registry(self):
        result = lookupOption(
            "plone.caching.tests", "testrule", "test", default=_marker
        )
        self.assertTrue(result is _marker)

    def test_lookupOption_no_record(self):
        provideUtility(Registry(), IRegistry)

        result = lookupOption(
            "plone.caching.tests", "testrule", "test", default=_marker
        )
        self.assertTrue(result is _marker)

    def test_lookupOption_default(self):
        provideUtility(Registry(), IRegistry)
        registry = getUtility(IRegistry)

        registry.records["plone.caching.tests.test"] = Record(
            field.TextLine(), "default"
        )

        result = lookupOption(
            "plone.caching.tests", "testrule", "test", default=_marker
        )
        self.assertEqual("default", result)

    def test_lookupOption_override(self):
        provideUtility(Registry(), IRegistry)
        registry = getUtility(IRegistry)

        registry.records["plone.caching.tests.test"] = r = Record(
            field.TextLine(), "default"
        )
        registry.records["plone.caching.tests.testrule.test"] = Record(
            FieldRef(r.__name__, r.field), "override"
        )

        result = lookupOption(
            "plone.caching.tests", "testrule", "test", default=_marker
        )
        self.assertEqual("override", result)


class TestLookupOptions(unittest.TestCase):
    def tearDown(self):
        zope.component.testing.tearDown()

    def test_lookupOptions_no_registry(self):
        @provider(ICachingOperationType)
        class DummyOperation:
            title = ""
            description = ""
            prefix = "plone.caching.tests"
            options = (
                "test1",
                "test2",
            )

        result = lookupOptions(DummyOperation, "testrule", default=_marker)
        self.assertEqual({"test1": _marker, "test2": _marker}, result)

    def test_lookupOptions_no_records(self):
        provideUtility(Registry(), IRegistry)

        @provider(ICachingOperationType)
        class DummyOperation:
            title = ""
            description = ""
            prefix = "plone.caching.tests"
            options = (
                "test1",
                "test2",
            )

        result = lookupOptions(DummyOperation, "testrule", default=_marker)
        self.assertEqual({"test1": _marker, "test2": _marker}, result)

    def test_lookupOptions_default(self):
        provideUtility(Registry(), IRegistry)
        registry = getUtility(IRegistry)

        registry.records["plone.caching.tests.test2"] = Record(field.TextLine(), "foo")

        @provider(ICachingOperationType)
        class DummyOperation:
            title = ""
            description = ""
            prefix = "plone.caching.tests"
            options = (
                "test1",
                "test2",
            )

        result = lookupOptions(DummyOperation, "testrule", default=_marker)
        self.assertEqual({"test1": _marker, "test2": "foo"}, result)

    def test_lookupOptions_override(self):
        provideUtility(Registry(), IRegistry)
        registry = getUtility(IRegistry)

        registry.records["plone.caching.tests.test1"] = Record(field.TextLine(), "foo")
        registry.records["plone.caching.tests.test2"] = Record(field.TextLine(), "bar")
        registry.records["plone.caching.tests.testrule.test2"] = Record(
            field.TextLine(), "baz"
        )

        @provider(ICachingOperationType)
        class DummyOperation:
            title = ""
            description = ""
            prefix = "plone.caching.tests"
            options = (
                "test1",
                "test2",
            )

        result = lookupOptions(DummyOperation, "testrule", default=_marker)
        self.assertEqual({"test1": "foo", "test2": "baz"}, result)

    def test_lookupOptions_named(self):
        provideUtility(Registry(), IRegistry)
        registry = getUtility(IRegistry)

        registry.records["plone.caching.tests.test2"] = Record(field.TextLine(), "foo")

        @provider(ICachingOperationType)
        class DummyOperation:
            title = ""
            description = ""
            prefix = "plone.caching.tests"
            options = (
                "test1",
                "test2",
            )

        provideUtility(DummyOperation, name="plone.caching.tests")

        result = lookupOptions("plone.caching.tests", "testrule", default=_marker)
        self.assertEqual({"test1": _marker, "test2": "foo"}, result)


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
