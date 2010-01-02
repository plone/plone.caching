plone.caching
=============

This package provides a framework for the management of cache headers, built
atop `z3c.caching`_. It consists of the following elements:

* An interface ``IResponseMutator``, describing components which mutate the
  response for caching purposes. The most common operation will be to set
  cache headers. Response mutators are named multi-adapters on the published
  object (e.g. a view) and the request.
  
* An interface ``ICacheInterceptor``, describing components which intercept
  a request before view rendering (but after traversal and authorisation)
  to provide a cached response. The most common operation will be to set a
  "304 Not Modified" response header and return an empty response, although it
  is also possible to provide a full response body. Cache interceptors are
  named multi-adapters on the published object (e.g. a view) and the request.

* Two interfaces, ``IResponseMutatorType`` and ``ICacheInterceptorType``,
  which are used for utilities describing response mutators and cache
  interceptors, respectively.

* Hooks into the Zope 2 ZPublisher (installed provided ZPublisher is
  available) which will execute response mutators and cache interceptors as
  appropriate.

* Helper functions for looking up configuration options for response mutators
  and cache interceptors in a registry managed by `plone.registry`_

* A response mutator called ``plone.caching.operations.chain``, which can
  be used to chain together multiple response mutators. It will look up the
  option ``plone.caching.operations.chain.${rulename}.operations`` in the
  registry, expecting a list of strings indicating the names of response
  mutators to execute. (${rulename} refers to the name of the caching rule
  set in use - more on this later).

Usage
~~~~~

To use ``plone.caching``, you must first install it into your build and load
its configuration. If you are using Plone, you can do that by installing
`plone.app.caching`_. Otherwise, depend on ``plone.caching`` in your
own package's ``setup.py``::

    install_requires = [
        ...
        'plone.caching',
        ]
        
Then load the package's configuration from your own package's
``configure.zcml``::

    <include package="plone.caching" />

Next, you must ensure that the the cache settings records are installed in
the registry. (``plone.caching`` uses ``plone.registry`` to store various
settings, and provides helpers for caching operations to do the same.)

To use the registry, you must register a (usually local) utility providing
``plone.registry.interfaces.IRegistry``. If you are using Plone, installing
``plone.app.registry`` will do this for you. Otherwise, configure one manually
using the ``zope.component`` API.

In tests, you can do the following::

    from zope.component import provideAdapter
    from plone.registry.interfaces import IRegistry
    from plone.registry import Registry
    
    provideAdapter(Registry(), IRegistry)

Next, you must add the ``plone.caching`` settings to the registry. If you use
`plone.app.caching`_, it will do this for you. Otherwise, you can register 
them like so::

    from zope.component import getUtility
    from plone.registry.interfaces import IRegistry
    from plone.caching.interfaces import ICacheSettings
    
    registry = getUtility(IRegistry)
    registry.registerInterface(ICacheSettings)

Finally, you must turn on the caching engine, by setting the registry value
``plone.caching.interfaces.ICacheSettings.enabled`` to ``True``.
If you are using Plone and have installed `plone.app.caching`_, you can do
this from the caching control panel. In code, you can do::

    registry['plone.caching.interfaces.ICacheSettings.enabled'] = True

Declaring cache rules for a view
--------------------------------

The entry point for caching is a *cache rule set*. A rule set is simply a name
given to a collection of publishable resources, such as views, for caching
purposes. Take a look at `z3c.caching`_ for details, but a simple example may
look like this::

    <configure
        xmlns="http://namespaces.zope.org/zope"
        xmlns:browser="http://namespaces.zope.org/browser"
        xmlns:cache="http://namespaces.zope.org/cache"/>

        <cache:ruleset
            for=".frontpage.FrontpageView"
            ruleset="plone-content-types"
            />

        <browser:page
            for="..interfaces.IFrontpage"
            class=".frontpage.FrontpageView"
            name="frontpage_view"
            template="templates/frontpage_view.pt"
            permission="zope2.View"
            />

    </configure>

Here, the view implemented by the class ``FrontpageView`` is associated with
the rule set ``plone-content-types``.

Elsewhere (or in the same file) the ``plone-content-types`` ruleset should be
declared with a title and description. This is can be used by a UI such as
that provided by `plone.app.caching`_. If "explicit" mode is set in
``z3c.caching``, this is required. By default it is optional::

        <cache:rulesetType
            name="plone-content-types"
            title="Plone content types"
            description="Non-container content types"
            />

Hints:

* Try to re-use existing rule sets rather than invent your own.
* Rule sets inherit according to the same rules as those that apply to
  adapters. Thus, you can register a generic rule set for a generic interface
  or base class, and then override it for a more specific class or interface.
* If you need to modify rule sets declared by packages not under your control,
  you can use an ``overrides.zcml`` file for your project.

Mapping cache rules to response mutators
----------------------------------------

``plone.caching`` maintains a mapping of rule sets to mutator operations in
the registry. This mapping is stored in a dictionary of dotted name (ASCII)
string keys to dotted name string values, under the record
``plone.caching.interfaces.ICacheSettings.mutatorMapping``.

To set the name of the operation to use for the ``plone-content-types`` rule
shown above, a mapping like the following might be used::

    from zope.component import getUtility
    from plone.registry.interfaces import IRegistry
    from plone.caching.interfaces import ICacheSettings
    
    registry = getUtility(IRegistry)
    settings = registry.forInterface(ICacheSettings)
    if settings.mutatorMapping is None: # initialise if not set already
        settings.mutatorMapping = {}
    settings.mutatorMapping['plone-content-types'] = 'my.package.mymutator'

Here, ``my.package.mymutator`` is the name of a caching mutator. We will
see an example of using one shortly.

If you want to use several mutators, you can chain them together using the
``plone.caching.operations.chain`` mutator::

    settings.mutatorMapping['plone-content-types'] = 'plone.caching.operations.chain'
    
    registry['plone.caching.operations.chain.plone-content-types.operations'] = \
        ['my.package.mymutator', 'my.package.anothermutator']

The last line here is setting the ``operations`` option for the chain
mutator, in a way that is specific to the ``plone-content-types`` rule set.
More on the configuration syntax shortly.

If you need to list all response mutators for UI purposes, you can look up
the registered instances of the ``IResponseMutatorType`` utility::

    from zope.component import getUtilitiesFor
    from plone.caching.interfaces import IResponseMutatorType
    
    for name, type_ in getUtilitiesFor(IResponseMutatorType):
        ...

The ``IResponseMutatorType`` utility provides properties like ``title`` and
``description`` to help build a user interface around caching operations.
`plone.app.caching`_ provides just such an interface.

Mapping cache rules to cache interceptors
-----------------------------------------

Cache interceptors are very similar to response mutators, and can be managed
much in the same way. The differences are:

* The mapping setting is called ``interceptorMapping`` instead of
  ``mutatorMapping``
* The type utility interface is ``ICacheInterceptorType`` instead of
  ``IResponseMutatorType``
* There is no "chain" interceptor by default.

Setting options for a response mutator or cache interceptor
-----------------------------------------------------------

``plone.caching`` does not strictly enforce how caching operations configure
themselves, if at all. However, it provides helper functionality to encourage
a pattern based on settings stored in ``plone.registry``. We have already seen
this pattern in use for the chain response mutator above. Let's now take a
closer look.

The chain mutator is implemented by the ``plone.caching.operations.Chain``.
The ``IResponseMutatorType`` or ``ICacheInterceptor`` utility named
``plone.caching.operations.chain`` provides two attributes in addition to the
``title`` and ``description`` attributes mentioned above:

prefix
    A dotted name prefix used for all registry keys. This key must be unique.
    By convention, it is the name of the mutator or interceptor.
options
    A sequence of option names
    
Taken together, these attributes describe the configurable options (if any)
of the caching operation. By default, the two are concatenated, so that if
you have an operation called ``my.package.mymutator``, the prefix is the same
string, and the options are ``('option1', 'option2')``, two registry keys
will be used: ``my.package.mymutator.option1`` and
``my.package.mymutator.option2``. (The type of those records and their value
will obviously depend on how the registry is configured. Typically, the
installation routine for a given operation will create them with sensible
defaults).

If you need to change these settings on a per-cache-rule basis, you can do
so by inserting the cache rule name between the prefix and the option name.
For example, for the cache rule ``my-rule``, the rule-specific version of
``option1`` would be ``my.package.mymutator.my-rule.option1``.

Finally, note that it is generally safe to use caching operations if their
registry keys are not installed. That is, they should fall back on sensible
defaults and not crash.

Writing response mutators and cache interceptors
************************************************

Now that we have seen how to configure cache rules and operations, let's look
at how we can write our own response mutators.

Writing a response mutator
--------------------------

Response mutators are typically used to set cache control response headers.
They consist of two components:

* A named multi-adapter implementing the operation itself
* A named utility providing metadata about the operation

Typically, both of these are implemented within a single class, although this
is not a requirement. Typically, the operation will also look up options in
accordance with the configuration methodology outlines above.

Here is an example of an response mutator that sets a fixed max-age cache
control header. It is registered for any published resource, and for any
HTTP request (but not other types of request.)::

    from zope.interface import implements, classProvides, Interface
    from zope.component import adapts, queryMultiAdapter
    
    from zope.publisher.interfaces.http import IHTTPRequest
    
    from plone.caching.interfaces import IResponseMutator
    from plone.caching.interfaces import IResponseMutatorType
    
    from plone.caching.utils import lookupOptions

    class MaxAge(object):
        implements(IResponseMutator)
        adapts(Interface, IHTTPRequest)
    
        # Type metadata
        classProvides(IResponseMutatorType)
    
        title = _(u"Max age")
        description = _(u"Sets a fixed max age value")
        prefix = 'plone.caching.tests.maxage'
        options = ('maxAge',)
    
        def __init__(self, published, request):
            self.published = published
            self.request = request
        
        def __call__(self, rulename, response):
            options = lookupOptions(self.__class__, rulename)
            maxAge = options['maxAge'] or 3600
            response.setHeader('Cache-Control', 'max-age=3600, must-revalidate' % maxAge)

Note the use of the ``lookupOptions()`` helper method. You can pass this
either a ``IResponseMutatorType`` (or ``ICacheInterceptorType``) instance,
or the name of one (in which case it will be looked up from the utility
registry), as well as the current rule name. It will return a dictionary of
all the options listed (only ``maxAge`` in this case), taking rule set
overrides into account. The options are guaranteed to be there, but will
fall back on a default of ``None`` if not set. 

To register this component in ZCML, we would do::

    <adapter factory=".maxage.MaxAge" name="plone.caching.tests.maxage" />
    <utility component=".maxage.MaxAge" name="plone.caching.tests.maxage" />

Note that by using ``component`` instead of ``factory`` in the ``<utility />``
declaration, we register the class object itself as the utility. The
attributes are provided as class variables for that reason - setting them in
``__init__()``, for example, would not work.

Writing a cache interceptor
---------------------------

Cache interceptors are again similar to response mutators. The main
difference, apart from the timing of their execution, is that they return a
response body. If they return ``None``, the request is *not* intercepted, and
view rendering continues as normal.

Here is a simple example that sends a 304 not modified response always. (This
is probably not very useful, but it serves as an example.)::

    from zope.interface import implements, classProvides, Interface
    from zope.component import adapts, queryMultiAdapter
    
    from zope.publisher.interfaces.http import IHTTPRequest
    
    from plone.caching.interfaces import ICacheInterceptor
    from plone.caching.interfaces import ICacheInterceptorType
    
    from plone.caching.utils import lookupOptions

    class Always304(object):
        implements(IResponseMutator)
        adapts(Interface, IHTTPRequest)
    
        # Type metadata
        classProvides(ICacheInterceptorType)
    
        title = _(u"Always send 304")
        description = _(u"It's not modified, dammit!")
        prefix = 'plone.caching.tests.always304'
        options = ('temporarilyDisable',)
    
        def __init__(self, published, request):
            self.published = published
            self.request = request
        
        def __call__(self, rulename, response):
            options = lookupOptions(self.__class__, rulename)
            if options['temporarilyDisable']:
                return None
            
            response.setStatus(304)
            return u""

Here, we return None to indicate that the request should not be intercepted if
the ``temporarilyDisable`` option is set to ``True``. Otherwise, we modify
the response and return a response body. The return value must be a unicode
string. In this case, an empty string will suffice.

The ZCML registration would look like this::

    <adapter factory=".always.Always304" name="plone.caching.tests.always304" />
    <utility component=".always.Always304" name="plone.caching.tests.always304" />

.. _z3c.caching: http://pypi.python.org/pypi/z3c.caching
.. _plone.registry: http://pypi.python.org/pypi/plone.registry
.. _plone.app.caching: http://pypi.python.org/pypi/plone.app.caching
