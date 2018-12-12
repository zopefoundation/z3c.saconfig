z3c.saconfig
************

0.16 (unreleased)
=================

- Added support for Python 3.4 and 3.7 [nazrulworld]


0.15 (2018-11-30)
=================

- Added Python 3.5 and 3.6 compatibility [nazrulworld]
- fix: `Issue with python3 compatibility, on zope interface implementation <https://github.com/zopefoundation/z3c.saconfig/issues/4>`_ [nazrulworld]


0.14 (2015-06-29)
=================

- Drop support for sqlalchemy < 0.5
  [oggers]


0.13 (2011-07-26)
=================

- Register engine factory setup using a zcml action


0.12 (2010-09-28)
=================

- EngineCreatedEvent also gets ``engine_args`` and ``engine_kw`` as
  attributes, so that event handlers can potentially differentiate
  between engines.


0.11 (2010-07-05)
=================

- Add pool_size, max_overflow, pool_recycle and pool_timeout options to the
  <engine /> directive. This allows connection pooling options to be defined
  in ZCML.

- works with sqlalchemy >= 0.5 (wouldn't work with sqlalchemy > 5 prior)


0.10 (2010-01-18)
=================

- Support current ZTK code

- engine.echo must default to None for SQLAlchemy to honor
  logging.getLogger("sqlalchemy.engine").setLevel(...)

- Do not enable convert_unicode by default. This option changes
  standard SQLAlchemy behaviour by making String type columns return
  unicode data.  This can be especially painful in Zope2 environments
  where unicode is not always accepted.

- Add a convert_unicode option to the zcml engine statement, allowing
  people who need convert_unicode to enable it.


0.9.1 (2009-08-14)
==================

- Include documentation on PyPI.

- Small documentation tweaks.


0.9 (2009-08-14)
================

- Initial public release.
