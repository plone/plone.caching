Changelog
=========

.. You should *NOT* be adding new change log entries to this file.
   You should create a file in the news directory instead.
   For helpful instructions, please see:
   https://github.com/plone/plone.releaser/blob/master/ADD-A-NEWS-ITEM.rst

.. towncrier release notes start

2.0.0 (2023-04-15)
------------------

Breaking changes:


- Drop python 2 support.
  [gforcada] (#1)


Internal:


- Update configuration files.
  [plone devs] (3b8337e6)


1.2.2 (2020-04-20)
------------------

Bug fixes:


- Minor packaging updates. (#1)


1.2.1 (2018-11-29)
------------------

Bug fixes:

- Remove five.globalrequest usage.
  [gforcada]

1.2.0 (2018-09-28)
------------------

New features:

- Add support for Python 3.
  [pbauer]

Bug fixes:

- Fix caching and tests in python 3
  [ale-rt, pbauer]


1.1.2 (2016-09-16)
------------------

Bug fixes:

- Cleanup: isort, readability, pep8, utf8-headers.
  [jensens]


1.1.1 (2016-08-12)
------------------

Bug fixes:

- Use zope.interface decorator.
  [gforcada]


1.1.0 (2016-05-18)
------------------

Fixes:

- Use plone i18n domain.  [klinger]


1.0.1 (2015-03-21)
------------------

- Fix ruleset registry test isolation so that is no longer order dependent.
  [jone]


1.0 - 2011-05-13
----------------

- Release 1.0 Final.
  [esteele]

- Add MANIFEST.in.
  [WouterVH]


1.0b2 - 2011-02-10
------------------

- Updated tests to reflect operation parameter overrides can now use
  plone.registry FieldRefs. Requires plone.registry >= 1.0b3.
  [optilude]

- Removed monkey patches unneeded since Zope 2.12.4.
  [optilude]


1.0b1 - 2010-08-04
------------------

- Preparing release to coincide with plone.app.caching 1.0b1
  [optilude]


1.0a1 - 2010-04-22
------------------

- Initial release
  [optilude, newbery]
