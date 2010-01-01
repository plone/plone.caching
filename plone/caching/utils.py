from zope.component import queryUtility, getUtility

from plone.registry.interfaces import IRegistry
from plone.caching.interfaces import ICacheOperationType

def lookupOptions(type_, rulename, default=None):
    """Look up all options for a given caching operation type, returning
    a dictionary. They keys of the dictionary will be the items in the
    ``options`` tuple of an ``ICacheOperationType``.
    
    ``type`` should either be a ``ICacheOperationType`` instance or the name
    of one.
    
    ``rulename`` is the name of the rule being executed.
    
    ``default`` is the default value to use for options that cannot be found.
    """
    
    if not ICacheOperationType.providedBy(type_):
        type_ = getUtility(ICacheOperationType, name=type_)
    
    options = {}
    registry = queryUtility(IRegistry)
    
    for option in getattr(type_, 'options', ()):
        options[option] = lookupOption(type_.prefix, rulename, option, default, registry)
    
    return options

def lookupOption(prefix, rulename, option, default=None, _registry=None):
    """Look up an option for a particular caching operation.
    
    The idea is that a caching operation may read configuration options from
    plone.registry according to the following rules:
    
    * If ${prefix}.${rulename}.${option} exists, get that
    * Otherwise, if ${prefix}.${option} exists, get that
    * Otherwise, return ``default``
    
    This allows an operation to have a default setting, as well as a per-rule
    override.
    """
    
    # Avoid looking this up multiple times if we are being called from lookupOptions
    registry = _registry
    
    if registry is None:
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

