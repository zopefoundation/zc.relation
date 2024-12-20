=======
Changes
=======


2.2 (unreleased)
================

- Nothing changed yet.


2.1 (2024-12-09)
================

- Add support for Python 3.12, 3.13.

- Drop support for Python 3.7.


2.0 (2023-04-05)
================

- Drop support for Python 2.7, 3.5, 3.6.
  [ale-rt]

- Fix the dependency on the ZODB, we just need to depend on the BTrees package.
  Refs. #11.
  [ale-rt]


1.2 (2023-03-28)
================

- Adapt code for PEP-479 (Change StopIteration handling inside generators).
  See: https://peps.python.org/pep-0479.
  Fixes #11.
  [ale-rt]


1.1.post2 (2018-06-18)
======================

- Another attempt to fix PyPI page by using correct expected metadata syntax.


1.1.post1 (2018-06-18)
======================

- Fix PyPI page by using correct ReST syntax.


1.1 (2018-06-15)
================

- Add support for Python 3.5 and 3.6.


1.0 (2008-04-23)
================

This is the initial release of the zc.relation package.  However, it
represents a refactoring of another package, zc.relationship.  This
package contains only a modified version of the relation(ship) index,
now called a catalog. The refactored version of zc.relationship index
relies on (subclasses) this catalog. zc.relationship also maintains a
backwards-compatible subclass.

This package only relies on the ZODB, zope.interface, and zope.testing
software, and can be used inside or outside of a standard ZODB database.
The software does have to be there, though (the package relies heavily
on the ZODB BTrees package).

If you would like to switch a legacy zc.relationship index to a
zc.relation catalog, try this trick in your generations script.
Assuming the old index is ``old``, the following line should create
a new zc.relation catalog with your legacy data:

    >>> new = old.copy(zc.relation.Catalog)

Why is the same basic data structure called a catalog now?  Because we
exposed the ability to mutate the data structure, and what you are really
adding and removing are indexes.  It didn't make sense to put an index in
an index, but it does make sense to put an index in a catalog.  Thus, a
name change was born.

The catalog in this package has several incompatibilities from the earlier
zc.relationship index, and many new features.  The zc.relationship package
maintains a backwards-compatible subclass.  The following discussion
compares the zc.relation catalog with the zc.relationship 1.x index.

Incompatibilities with zc.relationship 1.x index
------------------------------------------------

The two big changes are that method names now refer to ``Relation`` rather
than ``Relationship``; and the catalog is instantiated slightly differently
from the index.  A few other changes are worth your attention.  The
following list attempts to highlight all incompatibilities.

:Big incompatibilities:

    - ``findRelationshipTokenSet`` and ``findValueTokenSet`` are renamed, with
      some slightly different semantics, as ``getRelationTokens`` and
      ``getValueTokens``.  The exact same result as
      ``findRelationTokenSet(query)`` can be obtained with
      ``findRelationTokens(query, 1)`` (where 1 is maxDepth).  The same
      result as ``findValueTokenSet(reltoken, name)`` can be obtained with
      ``findValueTokens(name, {zc.relation.RELATION: reltoken}, 1)``.

    - ``findRelations`` replaces ``findRelatonships``.  The new method will use
      the defaultTransitiveQueriesFactory if it is set and maxDepth is not 1.
      It shares the call signature of ``findRelationChains``.

    - ``isLinked`` is now ``canFind``.

    - The catalog instantiation arguments have changed from the old index.

      * ``load`` and ``dump`` (formerly ``loadRel`` and ``dumpRel``,
        respectively) are now required arguments for instantiation.

      * The only other optional arguments are ``btree`` (was ``relFamily``) and
        ``family``. You now specify what elements to index with
        ``addValueIndex``

      * Note also that ``addValueIndex`` defaults to no load and dump function,
        unlike the old instantiation options.

    - query factories are different.  See ``IQueryFactory`` in the interfaces.

      * they first get (query, catalog, cache) and then return a getQueries
        callable that gets relchains and yields queries; OR None if they
        don't match.

      * They must also handle an empty relchain.  Typically this should
        return the original query, but may also be used to mutate the
        original query.

      * They are no longer thought of as transitive query factories, but as
        general query mutators.

:Medium:

    - The catalog no longer inherits from
      zope.app.container.contained.Contained.

    - The index requires ZODB 3.8 or higher.

:Small:

    - ``deactivateSets`` is no longer an instantiation option (it was broken
      because of a ZODB bug anyway, as had been described in the
      documentation).

Changes and new features
------------------------

- The catalog now offers the ability to index certain
  searches.  The indexes must be explicitly instantiated and registered
  you want to optimize. This can be used when searching for values, when
  searching for relations, or when determining if two objects are
  linked.  It cannot be used for relation chains. Requesting an index
  has the usual trade-offs of greater storage space and slower write
  speed for faster search speed.  Registering a search index is done
  after instantiation time; you can iteratate over the current settings
  used, and remove them.  (The code path expects to support legacy
  zc.relationship index instances for all of these APIs.)

- You can now specify new values after the catalog has been created, iterate
  over the settings used, and remove values.

- The catalog has a copy method, to quickly make new copies without actually
  having to reindex the relations.

- query arguments can now specify multiple values for a given name by
  using zc.relation.catalog.any(1, 2, 3, 4) or
  zc.relation.catalog.Any((1, 2, 3, 4)).

- The catalog supports specifying indexed values by passing callables rather
  than interface elements (which are also still supported).

- ``findRelations`` and new method ``findRelationTokens`` can find
  relations transitively and intransitively.  ``findRelationTokens``
  when used intransitively repeats the legacy zc.relationship index
  behavior of ``findRelationTokenSet``.
  (``findRelationTokenSet`` remains in the API, not deprecated, a companion
  to ``findValueTokenSet``.)

- in findValues and findValueTokens, ``query`` argument is now optional.  If
  the query evaluates to False in a boolean context, all values, or value
  tokens, are returned.  Value tokens are explicitly returned using the
  underlying BTree storage.  This can then be used directly for other BTree
  operations.

- Completely new docs.  Unfortunately, still really not good enough.

- The package has drastically reduced direct dependecies from zc.relationship:
  it is now more clearly a ZODB tool, with no other Zope dependencies than
  zope.testing and zope.interface.

- Listeners allow objects to listen to messages from the catalog (which can
  be used directly or, for instance, to fire off events).

- You can search for relations, using a key of zc.relation.RELATION...which is
  really an alias for None. Sorry. But hey, use the constant! I think it is
  more readable.

- tokenizeQuery (and resolveQuery) now accept keyword arguments as an
  alternative to a normal dict query.  This can make constructing the query
  a bit more attractive (i.e., ``query = catalog.tokenizeQuery;
  res = catalog.findValues('object', query(subject=joe, predicate=OWNS))``).
