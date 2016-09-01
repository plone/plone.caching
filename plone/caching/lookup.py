# -*- coding: utf-8 -*-
from plone.caching.interfaces import IRulesetLookup
from z3c.caching.registry import lookup
from zope.component import adapts
from zope.interface import implementer
from zope.interface import Interface


@implementer(IRulesetLookup)
class DefaultRulesetLookup(object):
    """Default ruleset lookup.

    Only override this if you have very special needs. The safest option is
    to use ``z3c.caching`` to set rulesets.
    """
    adapts(Interface, Interface)

    def __init__(self, published, request):
        self.published = published
        self.request = request

    def __call__(self):
        return lookup(self.published)
