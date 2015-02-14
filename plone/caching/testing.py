from plone.testing import Layer
from plone.testing.zca import UNIT_TESTING
from z3c.caching.registry import getGlobalRulesetRegistry
from z3c.caching.registry import RulesetRegistry
from zope.component import provideAdapter
import zope.component.testing


class ImplicitRulesetRegistryUnitTestingLayer(Layer):
    """Sets the z3c.caching registry into non-explicit mode.
    Plone uses the explicit mode by default, requiring rules to be registered
    as utilities explicitly.

    The plone.caching unit tests do not register utilities and therefore
    require the ruleset registry to be in non-explicit mode.

    See the plone.app.caching.setuphandlers.enableExplicitMode ZCML
    startup hook.
    """

    defaultBases = (UNIT_TESTING, )

    def testSetUp(self):
        provideAdapter(RulesetRegistry)
        self.disable_explicit_mode()

    def testTearDown(self):
        self.reset_explicit_mode()
        zope.component.testing.tearDown()

    def disable_explicit_mode(self):
        registry = getGlobalRulesetRegistry()
        self._explicit_mode_cache = registry.explicit
        registry.explicit = False

    def reset_explicit_mode(self):
        registry = getGlobalRulesetRegistry()
        if registry is not None:
            registry.explicit = self._explicit_mode_cache


IMPLICIT_RULESET_REGISTRY_UNIT_TESTING = (
    ImplicitRulesetRegistryUnitTestingLayer())
