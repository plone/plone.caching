from zope.component import queryUtility
from plone.registry.interfaces import IRegistry

def lookupOption(prefix, rulename, option, default=None):
    """Look up an option for a particular caching operation.
    
    The idea is that a caching operation may read configuration options from
    plone.registry according to the following rules:
    
    * If ${prefix}.${rulename}.${option} exists, get that
    * Otherwise, if ${prefix}.${option} exists, get that
    * Otherwise, return ``default``
    
    This allows an operation to have a default setting, as well as a per-rule
    override.
    """

    registry = queryUtility(IRegistry)
    if registry is None:
        return default
    
    key = "%s.%s.%s" % (prefix, rulename, option,)
    if key in registry.records:
        return registry[key]
    
    key = "%s.%s" % (prefix, option,)
    if key in registry.records:
        return registry[key]
    
    return default
