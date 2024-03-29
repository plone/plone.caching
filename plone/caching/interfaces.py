from zope import schema
from zope.interface import Interface

import zope.i18nmessageid


_ = zope.i18nmessageid.MessageFactory("plone")

X_CACHE_RULE_HEADER = "X-Cache-Rule"
X_CACHE_OPERATION_HEADER = "X-Cache-Operation"


class ICacheSettings(Interface):
    """Settings expected to be found in plone.registry"""

    enabled = schema.Bool(
        title=_("Globally enabled"),
        description=_("If not set, no caching operations will be attempted"),
        default=False,
    )

    operationMapping = schema.Dict(
        title=_("Rule set/operation mapping"),
        description=_("Maps rule set names to operation names"),
        key_type=schema.DottedName(title=_("Rule set name")),
        value_type=schema.DottedName(title=_("Caching operation name")),
    )


#
#  Cache operations
#


class ICachingOperation(Interface):
    """Represents a caching operation, typically setting of response headers
    and/or returning of an intercepted response.

    Should be registered as a named multi-adapter from a cacheable object
    (e.g. a view, or just Interface for a general operation) and the request.
    """

    def interceptResponse(ruleset, response):
        """Intercept the response if appropriate.

        May modify the response if required, e.g. by setting headers.

        Return None if the request should *not* be interrupted. Otherwise,
        return a new response body as a unicode string. For simple 304
        responses, returning ``u""`` will suffice.

        ``rulset`` is the name of the caching ruleset that was matched. It may
        be ``None``. ``response`` is the current HTTP response.

        The response body should *not* be modified.
        """

    def modifyResponse(ruleset, response):
        """Modify the response. ``rulset`` is the name of the caching ruleset
        that was matched. It may be ``None``. ``response`` is the current
        HTTP response. You may modify its headers and inspect it as required.

        The response body should *not* be modified. If you need to do that,
        either use ``plone.transformchain`` to add a new transformer, or use
        the ``interceptResponse()`` method.
        """


#
# Cache operation *types* (for UI support)
#


class ICachingOperationType(Interface):
    """A named utility which is used to provide UI support for caching
    operations. The name should correspond to the operation adapter name.

    The usual pattern is::

        from plone.caching.interfaces import ICachingOperation
        from plone.caching.interfaces import ICachingOperationType
        from plone.caching.utils import lookupOptions
        from zope.component import adapter
        from zope.interface import implementer
        from zope.interface import Interface
        from zope.interface import provider


        @implementer(ICachingOperation)
        @adapter(Interface, Interface)
        @provider(ICachingOperationType)
        class SomeOperation(object):

            title = u"Some operation"
            description = u"Operation description"
            prefix = 'my.package.operation1'
            options = ('option1', 'option2')

            def __init__(self, published, request):
                self.published = published
                self.request = request

            def __call__(self, rulename, response):
                options = lookupOptions(SomeOperation, rulename)
                ...

    This defines an adapter factory (the class), which itself provides
    information about the type of operation. In ZCML, these would be
    registered with::

        <adapter factory=".ops.SomeOperation" name="my.package.operation1" />
        <utility component=".ops.SomeOperation" name="my.package.operation1" />

    Note that the use of *component* for the ``<utility />`` registration - we
    are registering the class as a utility. Also note that the utility and
    adapter names must match. By convention, the option prefix should be the
    same as the adapter/utility name.

    You could also register an instance as a utility, of course.
    """

    title = schema.TextLine(
        title=_("Title"),
        description=_("A descriptive title for the operation"),
    )

    description = schema.Text(
        title=_("Description"),
        description=_("A longer description for the operation"),
        required=False,
    )

    prefix = schema.DottedName(
        title=_("Registry prefix"),
        description=_(
            "Prefix for records in the registry pertaining to "
            "this operation. This, alongside the next "
            "parameter, allows the user interface to present "
            "relevant configuration options for this "
            "operation."
        ),
        required=False,
    )

    options = schema.Tuple(
        title=_("Registry options"),
        description=_(
            "A tuple of options which can be used to "
            "configure this operation. An option is looked "
            "up in the registry by concatenating the prefix "
            "with the option name, optionally preceded by "
            "the rule set name, to allow per-rule overrides."
        ),
        value_type=schema.DottedName(),
        required=False,
    )


#
# Internal abstractions
#


class IRulesetLookup(Interface):
    """Abstraction for the lookup of response rulesets from published objects.
    This is an unnamed multi- adapter from (published, request).

    The main reason for needing this is that some publishable resources cannot
    be adequately mapped to a rule set by context type alone. In particular,
    Zope page templates in skin layers or created through the web can only be
    distinguished by their name, and cache rules may vary depending on how
    they are acquired.

    We don't implement anything other than the default ``z3c.caching`` lookup
    in this package, and would expect the use of a custom ``IRulesetLookup``
    to be a last resort for integrators.
    """

    def __call__():
        """Get the ruleset for the adapted published object and request.

        Returns a ruleset name (a string) or None.
        """
