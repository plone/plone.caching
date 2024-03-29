from plone.caching.interfaces import ICachingOperation
from plone.caching.operations import Chain
from plone.caching.testing import IMPLICIT_RULESET_REGISTRY_UNIT_TESTING
from plone.registry import field
from plone.registry import Record
from plone.registry import Registry
from plone.registry.interfaces import IRegistry
from zope.component import adapter
from zope.component import provideAdapter
from zope.component import provideUtility
from zope.interface import implementer
from zope.interface import Interface

import unittest


_marker = object()


class DummyView:
    pass


class DummyResponse(dict):
    def addHeader(self, name, value):
        self.setdefault(name, []).append(value)

    def setHeader(self, name, value):
        self[name] = value


class DummyRequest(dict):
    def __init__(self, published, response):
        self["PUBLISHED"] = published
        self.response = response


class TestChain(unittest.TestCase):
    layer = IMPLICIT_RULESET_REGISTRY_UNIT_TESTING

    def setUp(self):
        self.registry = Registry()
        provideUtility(self.registry, IRegistry)

    def test_no_option(self):
        view = DummyView()
        request = DummyRequest(view, DummyResponse())

        chain = Chain(view, request)
        ret = chain.interceptResponse("testrule", request.response)
        chain.modifyResponse("testrule", request.response)

        self.assertEqual(None, ret)
        self.assertEqual({"PUBLISHED": view}, dict(request))
        self.assertEqual({}, dict(request.response))

    def test_operations_list_not_set(self):
        self.registry.records[f"{Chain.prefix}.operations"] = Record(
            field.List(value_type=field.Text())
        )

        view = DummyView()
        request = DummyRequest(view, DummyResponse())

        chain = Chain(view, request)
        ret = chain.interceptResponse("testrule", request.response)
        chain.modifyResponse("testrule", request.response)

        self.assertEqual(None, ret)
        self.assertEqual({"PUBLISHED": view}, dict(request))
        self.assertEqual({}, dict(request.response))

    def test_operations_empty(self):
        self.registry.records[f"{Chain.prefix}.operations"] = Record(
            field.List(value_type=field.Text()), []
        )

        view = DummyView()
        request = DummyRequest(view, DummyResponse())

        chain = Chain(view, request)
        ret = chain.interceptResponse("testrule", request.response)
        chain.modifyResponse("testrule", request.response)

        self.assertEqual(None, ret)
        self.assertEqual({"PUBLISHED": view}, dict(request))
        self.assertEqual({}, dict(request.response))

    def test_chained_operations_not_found(self):
        self.registry.records[f"{Chain.prefix}.operations"] = Record(
            field.List(value_type=field.Text()), ["op1"]
        )

        view = DummyView()
        request = DummyRequest(view, DummyResponse())

        chain = Chain(view, request)
        chain.modifyResponse("testrule", request.response)

        self.assertEqual({"PUBLISHED": view}, dict(request))
        self.assertEqual({}, dict(request.response))

    def test_multiple_operations_one_found(self):
        self.registry.records[f"{Chain.prefix}.operations"] = Record(
            field.List(value_type=field.Text()), ["op1", "op2"]
        )

        view = DummyView()
        request = DummyRequest(view, DummyResponse())

        @implementer(ICachingOperation)
        @adapter(Interface, Interface)
        class DummyOperation:
            def __init__(self, published, request):
                self.published = published
                self.request = request

            def interceptResponse(self, rulename, response):
                return "foo"

            def modifyResponse(self, rulename, response):
                response["X-Mutated"] = rulename

        provideAdapter(DummyOperation, name="op2")

        chain = Chain(view, request)
        ret = chain.interceptResponse("testrule", request.response)

        self.assertEqual("foo", ret)
        self.assertEqual({"PUBLISHED": view}, dict(request))
        self.assertEqual({"X-Cache-Chain-Operations": "op2"}, dict(request.response))

        request = DummyRequest(view, DummyResponse())
        chain = Chain(view, request)
        chain.modifyResponse("testrule", request.response)

        self.assertEqual({"PUBLISHED": view}, dict(request))
        self.assertEqual(
            {"X-Mutated": "testrule", "X-Cache-Chain-Operations": "op2"},
            dict(request.response),
        )

    def test_multiple_operations_multiple_found(self):
        self.registry.records[f"{Chain.prefix}.operations"] = Record(
            field.List(value_type=field.Text()), ["op1", "op2"]
        )

        view = DummyView()
        request = DummyRequest(view, DummyResponse())

        @implementer(ICachingOperation)
        @adapter(Interface, Interface)
        class DummyOperation1:
            def __init__(self, published, request):
                self.published = published
                self.request = request

            def interceptResponse(self, rulename, response):
                return "foo"

            def modifyResponse(self, rulename, response):
                response["X-Mutated-1"] = rulename

        provideAdapter(DummyOperation1, name="op1")

        @implementer(ICachingOperation)
        @adapter(Interface, Interface)
        class DummyOperation2:
            def __init__(self, published, request):
                self.published = published
                self.request = request

            def interceptResponse(self, rulename, response):
                return "bar"

            def modifyResponse(self, rulename, response):
                response["X-Mutated-2"] = rulename

        provideAdapter(DummyOperation2, name="op2")

        chain = Chain(view, request)
        ret = chain.interceptResponse("testrule", request.response)

        self.assertEqual("foo", ret)
        self.assertEqual({"PUBLISHED": view}, dict(request))
        self.assertEqual({"X-Cache-Chain-Operations": "op1"}, dict(request.response))

        request = DummyRequest(view, DummyResponse())
        chain = Chain(view, request)
        chain.modifyResponse("testrule", request.response)

        self.assertEqual({"PUBLISHED": view}, dict(request))
        self.assertEqual(
            {
                "X-Mutated-1": "testrule",
                "X-Mutated-2": "testrule",
                "X-Cache-Chain-Operations": "op1; op2",
            },
            dict(request.response),
        )


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
