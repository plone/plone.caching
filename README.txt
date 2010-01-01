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



.. _z3c.caching: http://pypi.python.org/pypi/z3c.caching

