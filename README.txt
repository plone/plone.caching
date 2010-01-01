plone.caching
=============

This package provides a framework for the management of cache headers, built
atop `z3c.caching`_. It consists of the following elements:

* An interface ``IResponseMutator``, describing components which mutate the
  response for caching purposes. The most common operation will be to set
  cache headers. Response mutators are named multi-adapters on the published
  object (e.g. a view) and the request.
  
* An interface ``ICacheInterceptor``, describing components which intercept
  a request to provide a cached response. The most common operation will be
  to set a "304 Not Modified" response header and return an empty response,
  although it is also possible to provide a full response body. Cache
  interceptors are named multi-adapters on the published object (e.g. a view)
  and the request.

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
  mutators to execute.

Declaring cache rules for a view
--------------------------------

Enabling caching
----------------

Mapping cache rules to response mutators
----------------------------------------

Mapping cache rules to cache interceptors
-----------------------------------------

Setting options for a response mutator or cache interceptor
-----------------------------------------------------------

Writing a response mutator
--------------------------

Writing a cache interceptor
---------------------------

.. _z3c.caching: http://pypi.python.org/pypi/z3c.caching
.. _plone.registry: http://pypi.python.org/pypi/plone.registry
