================
Relation Catalog
================

.. contents::
   :local:

Overview
========

The relation catalog can be used to optimize intransitive and transitive
searches for N-ary relations of finite, preset dimensions; can be used
in the ZODB or standalone (though it uses ZODB classes--BTrees and
persistent.Persistent--so the ZODB software must be present); and can be
used with variable definitions of transitive behavior. It is a generic,
relatively policy-free tool.  It is expected to be used primarily as an
engine for more specialized and constrained tools and APIs.  Three such
tools are zc.relationship containers, plone.relations containers, and
zc.vault.  The documents in the package, including this one, describe
other possible uses.

The relation catalog uses the model that relations are full-fledged
objects that are indexed for optimized searches.  It takes a very
precise view of the world: instantiation requires multiple arguments
specifying the configuration; and using the catalog requires that you
acknowledge that the relations and their associated indexed values are
usually tokenized within the catalog, via tokenizers and resolvers you
specify.  This precision trades some ease-of-use for the possibility of
flexibility, power, and efficiency.  That said, the catalog's API is
intended to be consistent, and to largely adhere to "there's only one
way to do it".

Setting Up a Relation Catalog
=============================

Creating the Catalog
--------------------

Imagine a two way relation from one value to another.  Let's say that we
are modeling a relation of people to their supervisors: an employee may
have a single supervisor.  For this first example, the relation between
employee and supervisor will be intrinsic: the employee has a pointer to
the supervisor, and the employee object itself represents the relation.

Let's say further, for simplicity, that employee names are unique and
can be used to represent employees.  We can use names as our "tokens". 
Tokens are similar to the primary key in a relational database, or in
intid or keyreference in Zope 3--some way to uniquely identify an
object, which sorts reliably and can be resolved to the object given the
right context.  For speed, integers make the best tokens; followed by other
immutables like strings; followed by non-persistent objects; followed by
persistent objects.

Here is our toy `Employee` example class.

    >>> employees = {} # we'll use this to resolve the "name" tokens
    >>> class Employee(object):
    ...     def __init__(self, name, supervisor=None):
    ...         if name in employees:
    ...             raise ValueError('employee with same name already exists')
    ...         self.name = name # expect this to be readonly
    ...         self.supervisor = supervisor
    ...         employees[name] = self
    ...     # the next parts just make the tests prettier
    ...     def __repr__(self):
    ...         return '<Employee instance "' + self.name + '">'
    ...     def __cmp__(self, other):
    ...         # pukes if other doesn't have name
    ...         return cmp(self.name, other.name)
    ...

So, we need to define how to turn employees into their tokens.

The function to tokenize, or "dump", gets the object to be tokenized;
and, because it helps sometimes to provide context, the catalog; and a
dictionary that will be shared for a given search.  The dictionary can
be used as a cache for optimizations (for instance, to stash a utility
that you looked up).

For this example, our function is trivial: we said the token would be
the employee's name.

    >>> def dumpEmployees(emp, catalog, cache):
    ...     return emp.name
    ...

If you store the relation catalog persistently (e.g., in the ZODB) be aware
that the callables you provide must be picklable--a module-level function,
for instance.

We also need a way to turn tokens into employees, or "load".

The "load" functions get the token to be resolved; the catalog, for
context; and a dict cache, for optimizations of subsequent calls.

You might have noticed in our Employee __init__ that we keep a mapping
of name to object in the `employees` global dict (defined right above
the class definition).  We'll use that for resolving the tokens.  

    >>> def loadEmployees(token, catalog, cache):
    ...     return employees[token]
    ...

Now we know enough to get started with a catalog.  We'll instantiate it
by specifying how to tokenize relations, and what kind of BTree modules
should be used to hold the tokens.

    >>> import zc.relation.catalog
    >>> import BTrees
    >>> catalog = zc.relation.catalog.Catalog(dumpEmployees, loadEmployees,
    ...                               relFamily=BTrees.family32.OI)

[#verifyObjectICatalog]_ [#legacy]_ We can't do very much searching with it so far though,
because the catalog doesn't have any indexes.  In this example, the
relationship itself represents the employee, so we won't need to index
that separately.  But we do need a way to tell the catalog how to find
the other end of the relationship, the supervisor.

You can specify this to the catalog with a zope.interface attribute or
method, or with a callable.  We'll use a callable for now.  It takes the
indexed relationship and the catalog for context.

    >>> def supervisor(emp, catalog):
    ...     return emp.supervisor # None or another employee
    ...

Then we'll use that to tell the catalog to add an index for
`supervisor`.  We'll also specify how to tokenize and store those
values: in this case, the same way as the relations themselves.  We
could also specify the name to call the index, but it will default to
the __name__ of the function (or interface element), which will work
just fine for us now.

    >>> catalog.addValueIndex(supervisor, dumpEmployees, loadEmployees,
    ...                       btree=BTrees.family32.OI)

Now we have an index [#addValueIndexExceptions]_.

    >>> [info['name'] for info in catalog.iterValueIndexInfo()]
    ['supervisor']

Adding Relations
----------------

Now let's create a few employees.  All but one will have supervisors. 
If you recall our toy Employee class, the first argument to the
constructor is the employee name (and therefore the token), and the
optional second argument is the supervisor.

    >>> a = Employee('Alice')
    >>> b = Employee('Betty', a)
    >>> c = Employee('Chuck', a)
    >>> d = Employee('Diane', b)
    >>> e = Employee('Edgar', b)
    >>> f = Employee('Frank', c)
    >>> g = Employee('Galyn', c)
    >>> h = Employee('Howie', d)

Here is a diagram of the hierarchy.

::

                Alice
             __/     \__
        Betty           Chuck
        /   \           /   \
    Diane   Edgar   Frank   Galyn
      |
    Howie

Let's tell the catalog about the relations.

    >>> for emp in (a,b,c,d,e,f,g,h):
    ...     catalog.index(emp)
    ...

Searching
=========

Queries, `findRelations`, and special query values
--------------------------------------------------

So who works for Alice?  That means we want to get the relations--the
employees--with a `supervisor` of Alice.

The heart of a question to the catalog is a query.  A query is spelled
as a dictionary.  The main idea is simply that keys in a dictionary
specify index names, and the values specify the constraints.

The values in a query are always expressed with tokens.  The catalog has
several helpers to make this less onerous, but for now let's take
advantage of the fact that our tokens are easily comprehensible.

    >>> sorted(catalog.findRelations({'supervisor': 'Alice'}))
    [<Employee instance "Betty">, <Employee instance "Chuck">]

Alice is the direct (intransitive) boss of Betty and Chuck.

What if you want to ask "who doesn't report to anyone?"  Then you want to
ask for a relation in which the supervisor is None.

    >>> list(catalog.findRelations({'supervisor': None}))
    [<Employee instance "Alice">]

Alice is the only employee who doesn't report to anyone.

What if you want to ask "who reports to Diane or Chuck?"  Then you use the
zc.relation `Any` class or `any` function to pass the multiple values.

    >>> sorted(catalog.findRelations(
    ...     {'supervisor': zc.relation.catalog.any('Diane', 'Chuck')}))
    ... # doctest: +NORMALIZE_WHITESPACE
    [<Employee instance "Frank">, <Employee instance "Galyn">,
     <Employee instance "Howie">]

Frank, Galyn, and Howie each report to either Diane or Chuck.[#any]_

It is worth a quick mention here that the catalog always has parallel
search methods, one for finding objects, as seen above, and one for
finding tokens.  Finding tokens can be much more efficient, especially if
the result from the relation catalog is just one step along the
path of finding your desired result.  But finding objects is simpler for
some common cases.  Here's a quick example of the same query, getting
tokens rather than objects.

    >>> sorted(catalog.findRelationTokens({'supervisor': 'Alice'}))
    ['Betty', 'Chuck']
    >>> sorted(catalog.findRelationTokens({'supervisor': None}))
    ['Alice']
    >>> sorted(catalog.findRelationTokens(
    ...     {'supervisor': zc.relation.catalog.any('Diane', 'Chuck')}))
    ['Frank', 'Galyn', 'Howie']

`findValues` and the `None` query key
-------------------------------------

So how do we find who an employee's supervisor is?  Well, in this case,
look at the attribute on the employee!  If you can use an attribute that
will usually be a win in the ZODB.  

    >>> h.supervisor
    <Employee instance "Diane">

Again, as we mentioned at the start of this first example, the knowledge
of a supervisor is "intrinsic" to the employee instance.  It is
possible, and even easy, to ask the catalog this kind of question, but
the catalog syntax is more geared to "extrinsic" relations, such as the
one from the supervisor to the employee: the connection between a
supervisor object and its employees is extrinsic to the supervisor, so
you actually might want a catalog to find it!

However, we will explore the syntax very briefly, because it introduces an
important pair of search methods, and because it is a a stepping stone
to our first transitive search.

So, o relaton catalog, who is Howie's supervisor?  

To ask this question we want to get the indexed values off of the
relations: `findValues`. In its simplest form, the arguments are the
index name of the values you want, and a query to find the relationships
that have the desired values.

What about the query?  Above, we noted that the keys in a query are the
names of the indexes to search.  However, in this case, we don't want to
search one or more indexes for matching relationships, as usual, but
actually specify a relationship: Howie.

We do not have an index name.  The key, then, is `None`: no index name,
just relationship tokens.  For our current example, that would mean the
query is `{None: 'Howie'}`.

    >>> list(catalog.findValues('supervisor', {None: 'Howie'}))[0]
    <Employee instance "Diane">

Congratulations, you just found an obfuscated and comparitively
inefficient way to write `howie.supervisor`! [#intrinsic_search]_
[#findValuesExceptions]_

Slightly more usefully, you can use other query keys along with None.
    
    >>> sorted(catalog.findRelationTokens(
    ...     {None: zc.relation.catalog.any('Betty', 'Alice', 'Chuck'),
    ...      'supervisor': 'Alice'}))
    ['Betty', 'Chuck']

Transitive Searching, Query Factories, and `maxDepth`
----------------------------------------------------------------

What about transitive searching?  Well, you need to tell the catalog how to
walk the tree.  In simple (and very common) cases like this, the
zc.relation.queryfactory.TransposingTransitive will do the trick.

A transitive query factory is just a callable that the catalog uses to
ask "I got this query, and here are the results I found. I'm supposed to
walk another step transitively, so what query should I search for next?"
Writing a factory is more complex than we want to talk about right now,
but using the TransposingTransitiveQueryFactory is easy. You just tell
it the two query names it should transpose for walking in either
direction.

For instance, here we just want to tell the factory to transpose the two
keys we've used, None and 'supervisor'.  Let's make a factory, use it
in a query for a couple of transitive searches, and then, if you want,
you can read through a footnote to talk through what is happening.

Here's the factory.

    >>> import zc.relation.queryfactory
    >>> factory = zc.relation.queryfactory.TransposingTransitive(
    ...     None, 'supervisor')

Now `factory` is just a callable.  Let's let it help answer a couple of
questions.

Who are all of Howie's supervisors transitively (this looks up in the
diagram)?

    >>> list(catalog.findValues('supervisor', {None: 'Howie'},
    ...      queryFactory=factory))
    ... # doctest: +NORMALIZE_WHITESPACE
    [<Employee instance "Diane">, <Employee instance "Betty">,
     <Employee instance "Alice">]

Who are all of the people Betty supervises transitively, breadth first (this
looks down in the diagram)?

    >>> people = list(catalog.findRelations(
    ...     {'supervisor': 'Betty'}, queryFactory=factory))
    >>> sorted(people[:2])
    [<Employee instance "Diane">, <Employee instance "Edgar">]
    >>> people[2]
    <Employee instance "Howie">

Yup, that looks right.  So how did that work?  If you care, read this
footnote. [#I_care]_
    
This transitive factory is really the only transitive factory you would
want for this particular catalog, so it probably is safe to wire it in
as a default.  You can add multiple query factories to match different
queries using `addDefaultQueryFactory`.

    >>> catalog.addDefaultQueryFactory(factory)

Now all searches are transitive by default.

    >>> list(catalog.findValues('supervisor', {None: 'Howie'}))
    ... # doctest: +NORMALIZE_WHITESPACE
    [<Employee instance "Diane">, <Employee instance "Betty">,
     <Employee instance "Alice">]
    >>> people = list(catalog.findRelations({'supervisor': 'Betty'}))
    >>> sorted(people[:2])
    [<Employee instance "Diane">, <Employee instance "Edgar">]
    >>> people[2]
    <Employee instance "Howie">

We can force a non-transitive search, or a specific search depth, with
maxDepth [#needs_a_transitive_queries_factory]_.

    >>> list(catalog.findValues('supervisor', {None: 'Howie'}, maxDepth=1))
    [<Employee instance "Diane">]
    >>> sorted(catalog.findRelations({'supervisor': 'Betty'}, maxDepth=1))
    [<Employee instance "Diane">, <Employee instance "Edgar">]

[#maxDepthExceptions]_ We'll introduce some other available search
arguments later in this document and in other documents.  It's important
to note that *all search methods share the same arguments as
`findRelations`*.  `findValues` and `findValueTokens` only add the
initial argument of specifying the desired value.

We've looked at two search methods so far: the `findValues` and
`findRelations` methods help you ask what is related.  But what if you
want to know *how* things are transitively related?

`findRelationshipChains` and `targetQuery`
------------------------------------------

Another search method, `findRelationChains`, helps you discover how
things are transitively related.  

The method name says "find relation chains".  But what is a "relation
chain"?  In this API, it is a transitive path of relations.  For
instance, what's the chain of command above Howie?  `findRelationChains`
will return each unique path.

    >>> list(catalog.findRelationChains({None: 'Howie'}))
    ... # doctest: +NORMALIZE_WHITESPACE
    [(<Employee instance "Howie">,),
     (<Employee instance "Howie">, <Employee instance "Diane">),
     (<Employee instance "Howie">, <Employee instance "Diane">,
      <Employee instance "Betty">),
     (<Employee instance "Howie">, <Employee instance "Diane">,
     <Employee instance "Betty">, <Employee instance "Alice">)]

Look at that result carefully.  Notice that the result is an iterable of
tuples.  Each tuple is a unique chain, which may be a part of a
subsequent chain.  In this case, the last chain is the longest and the
most comprehensive.

What if we wanted to see all the paths from Alice?  That will be one
chain for each supervised employee, because it shows all possible paths.

    >>> sorted(catalog.findRelationChains(
    ...     {'supervisor': 'Alice'}))
    ... # doctest: +NORMALIZE_WHITESPACE
    [(<Employee instance "Betty">,),
     (<Employee instance "Betty">, <Employee instance "Diane">),
     (<Employee instance "Betty">, <Employee instance "Diane">,
      <Employee instance "Howie">),
     (<Employee instance "Betty">, <Employee instance "Edgar">),
     (<Employee instance "Chuck">,),
     (<Employee instance "Chuck">, <Employee instance "Frank">),
     (<Employee instance "Chuck">, <Employee instance "Galyn">)]

That's all the paths--all the chains--from Alice.  We sorted the results,
but normaly they would be breadth first.

But what if we wanted to just find the paths from one query result to
another query result--say, we wanted to know the chain of command from Alice
down to Howie?  Then we can specify a `targetQuery` that specifies the
characteristics of our desired end point (or points).

    >>> list(catalog.findRelationChains(
    ...     {'supervisor': 'Alice'}, targetQuery={None: 'Howie'}))
    ... # doctest: +NORMALIZE_WHITESPACE
    [(<Employee instance "Betty">, <Employee instance "Diane">,
      <Employee instance "Howie">)]

So, Betty supervises Diane, who supervises Howie.

Note that `targetQuery` now joins `maxDepth` in our collection of shared
search arguments that we have introduced.

`filter` and `targetFilter`
---------------------------

We can take a quick look now at the last of the two shared search arguments:
filter and targetFilter.  These two are similar in that they both are
callables that can approve or reject given relations in a search based on
whatever logic you can code.  They differ in that `filter` stops any further
transitive searches from the relation, while `targetFilter` merely omits the
given result but allows further search from it.  Like `targetQuery`, then,
`targetFilter` is good when you want to specify the other end of a path.

As an example, let's say we only want to return female employees.

    >>> female_employees = ('Alice', 'Betty', 'Diane', 'Galyn')
    >>> def female_filter(relchain, query, catalog, cache):
    ...     return relchain[-1] in female_employees
    ...

Here are all the female employees supervised by Alice transitively, using
`targetFilter`.

    >>> list(catalog.findRelations({'supervisor': 'Alice'},
    ...                            targetFilter=female_filter))
    ... # doctest: +NORMALIZE_WHITESPACE
    [<Employee instance "Betty">, <Employee instance "Diane">,
     <Employee instance "Galyn">]

Here are all the female employees supervised by Chuck.

    >>> list(catalog.findRelations({'supervisor': 'Chuck'},
    ...                            targetFilter=female_filter))
    [<Employee instance "Galyn">]

The same method used as a filter will only return females directly
supervised by other females--not Galyn, in this case.

    >>> list(catalog.findRelations({'supervisor': 'Alice'},
    ...                            filter=female_filter))
    [<Employee instance "Betty">, <Employee instance "Diane">]

These can be combined with one another, and with the other search
arguments [#filter]_.

Search indexes
--------------

Without setting up any additional indexes, the transitive behavior of
the `findRelations` and `findValues` methods essentially relies on the
brute force searches of `findRelationChains`.  Results are iterables
that are gradually computed.  For instance, let's repeat the question
"Whom does Betty supervise?".  Notice that `res` first populates a list
with three members, but then does not populate a second list.  The
iterator has been exhausted.

    >>> res = catalog.findRelationTokens({'supervisor': 'Betty'})
    >>> unindexed = sorted(res)
    >>> len(unindexed)
    3
    >>> len(list(res)) # iterator is exhausted
    0

The brute force of this aproach can be sufficient in many cases, but
sometimes speed for these searches is critical.  In these cases, you can
add a "search index".  A search index speeds up the result of one or
more precise searches by indexing the results.  Search indexes can
affect the results of searches with a queryFactory in `findRelations`,
`findValues`, and the soon-to-be-introduced `canFind`, but they do not
affect `findRelationChains`.

The zc.relation package currently includes two kinds of search indexes,
one for indexing relation searches and one for indexing value searches.
They only help for searches with an unlimited maxDepth (the default).
Other search index implementations and approaches may be added in the
future.  

Here's a very brief example of adding a search index for the transitive
searches seen above that specify a 'supervisor'.

    >>> import zc.relation.searchindex
    >>> catalog.addSearchIndex(
    ...     zc.relation.searchindex.TransposingTransitive(
    ...         'supervisor', None))

The `None` describes how to walk back up the chain.  Search indexes are 
explained in reasonable detail in searchindex.txt.

Now that we have added the index, we can search again.  The result this
time is already computed, so, at least when you ask for tokens, it
is repeatable.

    >>> res = catalog.findRelationTokens({'supervisor': 'Betty'})
    >>> len(list(res))
    3
    >>> len(list(res))
    3
    >>> sorted(res) == unindexed
    True

Note that the breadth-first sorting is lost when an index is used [#updates]_.

Transitive cycles (and updating and removing relations)
-------------------------------------------------------

The transitive searches and the provided search indexes can handle
cycles.  Cycles are less likely in the current example than some others,
but we can stretch the case a bit: imagine a "king in disguise", in
which someone at the top works lower in the hierarchy.  Perhaps Alice
works for Zane, who works for Betty, who works for Alice.  Artificial,
but easy enough to draw::

            ______
           /      \
          /     Zane
         /        |
        /       Alice
       /     __/     \__
      / Betty__         Chuck
      \-/  /   \         /   \
         Diane Edgar Frank   Galyn
          |
        Howie

Easy to create too.

    >>> z = Employee('Zane', b)
    >>> a.supervisor = z

Now we have a cycle.  Of course, we have not yet told the catalog about it.
`index` can be used both to reindex Alice and index Zane.

    >>> catalog.index(a)
    >>> catalog.index(z)

Now, if we ask who works for Betty, we get the entire tree.  (We'll ask
for tokens, just so that the result is smaller to look at.) [#same_set]_

    >>> sorted(catalog.findRelationTokens({'supervisor': 'Betty'}))
    ... # doctest: +NORMALIZE_WHITESPACE
    ['Alice', 'Betty', 'Chuck', 'Diane', 'Edgar', 'Frank', 'Galyn', 'Howie',
     'Zane']

If we ask for the supervisors of Frank, it will include Betty.

    >>> list(catalog.findValueTokens('supervisor', {None: 'Frank'}))
    ['Chuck', 'Alice', 'Zane', 'Betty']

Paths returned by `findRelationChains` are marked with special interfaces, and
special metadata, to show the chain.

    >>> res = list(catalog.findRelationChains({None: 'Frank'}))
    >>> len(res)
    5
    >>> import zc.relation.interfaces
    >>> [zc.relation.interfaces.ICircularRelationPath.providedBy(r)
    ...  for r in res]
    [False, False, False, False, True]

Here's the last chain:
    
    >>> res[-1] # doctest: +NORMALIZE_WHITESPACE
    cycle(<Employee instance "Frank">, <Employee instance "Chuck">,
          <Employee instance "Alice">, <Employee instance "Zane">,
          <Employee instance "Betty">)

The chain's 'cycled' attribute has a list of queries that create a cycle.
If you run the query, or queries, you see where the cycle would
restart--where the path would have started to overlap.  Sometimes the query
results will include multiple cycles, and some paths that are not cycles.
In this case, there's only a single cycled query, which results in a single
cycled relation.

    >>> len(res[4].cycled)
    1

    >>> list(catalog.findRelations(res[4].cycled[0], maxDepth=1))
    [<Employee instance "Alice">]


To remove this craziness [#reverse_lookup]_, we can unindex Zane, and change
and reindex Alice.

    >>> a.supervisor = None
    >>> catalog.index(a)

    >>> list(catalog.findValueTokens('supervisor', {None: 'Frank'}))
    ['Chuck', 'Alice']

    >>> catalog.unindex(z)

    >>> sorted(catalog.findRelationTokens({'supervisor': 'Betty'}))
    ['Diane', 'Edgar', 'Howie']

`canFind`
---------

We're to the last search method: `canFind`.  We've gotten values and
relations, but what if you simply want to know if there is any
connection at all?  For instance, is Alice a supervisor of Howie? Is
Chuck?  To answer these questions, you can use the `canFind` method
combined with the `targetQuery` search argument.

The `canFind` method takes the same arguments as findRelations.  However,
it simply returns a boolean about whether the search has any results.  This
is a convenience that also allows some extra optimizations.

Does Betty supervise anyone?

    >>> catalog.canFind({'supervisor': 'Betty'})
    True

What about Howie?

    >>> catalog.canFind({'supervisor': 'Howie'})
    False

What about...Zane (not an employee)?

    >>> catalog.canFind({'supervisor': 'Zane'})
    False

If we want to know if Alice or Chuck supervise Howie, then we want to specify
characteristics of two points on a path.  To ask a question about the other
end of a path, use `targetQuery`.

Is Alice a supervisor of Howie?

    >>> catalog.canFind({'supervisor': 'Alice'}, targetQuery={None: 'Howie'})
    True

Is Chuck a supervisor of Howie?

    >>> catalog.canFind({'supervisor': 'Chuck'}, targetQuery={None: 'Howie'})
    False

Is Howie Alice's employee?

    >>> catalog.canFind({None: 'Howie'}, targetQuery={'supervisor': 'Alice'})
    True

Is Howie Chuck's employee?

    >>> catalog.canFind({None: 'Howie'}, targetQuery={'supervisor': 'Chuck'})
    False

(Note that, if your relations describe a hierarchy, searching up a
hierarchy is usually more efficient, so the second pair of questions is
generally preferable to the first in that case.  However, if you install
a search index for either direction of the query, `canFind` can use
it efficiently either way)

Conclusion
==========

Review
------

That brings us to the end of our introductory example.  Let's review, and
then look at where you can go from here.

- The relation catalog indexes relations.  The relations can be one-way,
  as we've seen here, with the employee relation pointing to the supervisor.
  They can also be two-way, three-way, or N-way, as long as you tell the
  catalog to index the different values.

- Relations and their values are stored as tokens.  Integers are the most
  efficient tokens, but others can work find too.  The index has methods to
  help you work with tokens, but we did not explore them here.

- Relations are indexed with `index`.  We didn't look at this, but relations
  do not have to have all indexed values, which means they can be a
  heterogeneous set of relations, allowing indexing of interesting data
  structures.

- You add value indexes to relation catalogs to be able to search.  Values
  can be identified with callables (which we saw) or interface elements
  (which we did not see).

- As we've seen here, relations are assumed to be between single values.
  However, they do not have to be, as can be seen elsewhere (hint: use
  the `multiple` argument in `addValueIndex`).

- You search transitively by using a query factory.  The
  zc.relation.queryfactory.TransposingTransitive is a good common case
  factory that lets you walk up and down a hierarchy.  Query factories can
  do other tricks too, which we did not see.

- You can set up searches indexes to speed up specific transitive searches.

- We looked at the primary search methods that return objects as opposed to
  tokens.
  
    * `findRelations` returns relations that match the search.
    
    * `findValues` returns values for the relations that match the search.
    
    * `findRelationChains` returns the transitive paths that match the search.
    
    * `canFind` returns a boolean about whether anything matches the search.
  
  We also discussed the fact that users who want to get tokens back from
  searches can.  We did not give much of an example of this.  The parallel
  methods are `findRelationTokens`, `findValueTokens`, and
  `findRelationTokenChains`.

- Queries are formed with dicts.  The keys are the names of the indexes
you want to search, or, for the special case of precise relationships,
None. The values are the tokens of the results you want to match; or
None, indicating relations that have None as a value (or no values, if
it is a multiple).  Search values can use zc.relation.catalog.any or
zc.relation.catalog.Any to specify multiple (non-None) results to match
for a given key.

As you can tell by the holes we mentioned in the overview, there's more
to cover.  Hopefully, this will be enough to get your feet wet, though,
and maybe start to use the catalog.

Next Steps
----------

If you want to read more, next steps depend on how you like to learn.  Here
are some of the other documents in the zc.relation package.

:tokens.txt:
    This document explores the details of tokens.  All God's chillun
    love tokens, at least if God's chillun are writing non-toy apps
    using zc.relation.  It includes discussion of the token helpers that
    the catalog provides, how to use zope.app.intid-like registries with
    zc.relation, how to use tokens to "join" query results reasonably
    efficiently, and how to index joins.

:searchindex.txt:
    Queries factories and search indexes: from basics to nitty gritty details.

:optimization.txt:
    Best practices for optimizing your use of the relation catalog.

:administration.txt:
    Managing indexes and listeners.

:interfaces.py:
    The contract, for nuts and bolts.

Finally, the truly die-hard might also be interested in the timeit
directory, which holds scripts I ran to test assumptions and learn.

.. ......... ..
.. FOOTNOTES ..
.. ......... ..

.. [#verifyObjectICatalog] The catalog provides ICatalog.

    >>> from zope.interface.verify import verifyObject
    >>> import zc.relation.interfaces
    >>> verifyObject(zc.relation.interfaces.ICatalog, catalog)
    True

.. [#legacy] Old instances of zc.relationship indexes, which in the newest
    version subclass a zc.relationship Catalog, used to have a dict in an
    internal data structure.  We specify that here so that the code that
    converts the dict to an OOBTree can have a chance to run.

    >>> catalog._attrs = dict(catalog._attrs)

.. [#addValueIndexExceptions] Adding a value index can generate several
    exceptions.
    
    You must supply both of dump and load or neither.

    >>> catalog.addValueIndex(supervisor, dumpEmployees, None,
    ...                       btree=BTrees.family32.OI, name='supervisor2')
    Traceback (most recent call last):
    ...
    ValueError: either both of 'dump' and 'load' must be None, or neither

    In this example, even if we fix it, we'll get an error, because we have
    already indexed the supervisor function.

    >>> catalog.addValueIndex(supervisor, dumpEmployees, loadEmployees,
    ...                       btree=BTrees.family32.OI, name='supervisor2')
    ... # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    ValueError: ('element already indexed', <function supervisor at ...>)

    You also can't add a different function under the same name.
    
    >>> def supervisor2(emp, catalog):
    ...     return emp.supervisor # None or another employee
    ...
    >>> catalog.addValueIndex(supervisor2, dumpEmployees, loadEmployees,
    ...                       btree=BTrees.family32.OI, name='supervisor')
    ... # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    ValueError: ('name already used', 'supervisor')

    Finally, if your function does not have a __name__ and you do not provide
    one, you may not add an index.
    
    >>> class Supervisor3(object):
    ...     __name__ = None
    ...     def __call__(klass, emp, catalog):
    ...         return emp.supervisor
    ...
    >>> supervisor3 = Supervisor3()
    >>> supervisor3.__name__
    >>> catalog.addValueIndex(supervisor3, dumpEmployees, loadEmployees,
    ...                       btree=BTrees.family32.OI)
    ... # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    ValueError: no name specified

.. [#any] Any can be compared.

    >>> zc.relation.catalog.any('foo', 'bar', 'baz')
    <zc.relation.catalog.Any instance ('bar', 'baz', 'foo')>
    >>> (zc.relation.catalog.any('foo', 'bar', 'baz') ==
    ...  zc.relation.catalog.any('bar', 'foo', 'baz'))
    True
    >>> (zc.relation.catalog.any('foo', 'bar', 'baz') !=
    ...  zc.relation.catalog.any('bar', 'foo', 'baz'))
    False
    >>> (zc.relation.catalog.any('foo', 'bar', 'baz') ==
    ...  zc.relation.catalog.any('foo', 'baz'))
    False
    >>> (zc.relation.catalog.any('foo', 'bar', 'baz') !=
    ...  zc.relation.catalog.any('foo', 'baz'))
    True

.. [#intrinsic_search] Here's the same with token results.

    >>> list(catalog.findValueTokens('supervisor', {None: 'Howie'}))
    ['Diane']
    
    While we're down here in the footnotes, I'll mention that you can
    search for relations that haven't been indexed.

    >>> list(catalog.findRelationTokens({None: 'Ygritte'}))
    []
    >>> list(catalog.findRelations({None: 'Ygritte'}))
    []

.. [#findValuesExceptions] If you use findValues or findValueTokens and try
    to specify a value name that is not indexed, you get a ValueError.
    
    >>> catalog.findValues('foo')
    Traceback (most recent call last):
    ...
    ValueError: ('name not indexed', 'foo')

.. [#I_care] OK, you care about how that query factory worked, so
    we will look into it a bit.  Let's talk through two steps of the
    transitive search in the second question.  The catalog initially
    performs the initial intransitive search requested: find relations
    for which Betty is the supervisor.  That's Diane and Edgar. 
    
    Now, for each of the results, the catalog asks the query factory for
    next steps.  Let's take Diane.  The catalog says to the factory,
    "Given this query for relations where Betty is supervisor, I got
    this result of Diane.  Do you have any other queries I should try to
    look further?".  The factory also gets the catalog instance so it
    can use it to answer the question if it needs to.

    OK, the next part is where your brain hurts.  Hang on.
    
    In our case, the factory sees that the query was for supervisor. Its
    other key, the one it transposes with, is None.  *The factory gets
    the transposing key's result for the current token.*  So, for us, a
    key of None is actually a no-op: the result *is* the current
    token, Diane.  Then, the factory has its answer: replace the old value
    of supervisor in the query, Betty, with the result, Diane.  The next
    transitive query should be {'supervisor', 'Diane'}.  Ta-da.

.. [#needs_a_transitive_queries_factory] A search with a maxDepth > 1 but
    no queryFactory raises an error.
    
    >>> catalog.removeDefaultQueryFactory(factory)
    >>> catalog.findRelationTokens({'supervisor': 'Diane'}, maxDepth=3)
    Traceback (most recent call last):
    ...
    ValueError: if maxDepth not in (None, 1), queryFactory must be available

    >>> catalog.addDefaultQueryFactory(factory)

.. [#maxDepthExceptions] maxDepth must be None or a positive integer, or
    else you'll get a value error.
    
    >>> catalog.findRelations({'supervisor': 'Betty'}, maxDepth=0)
    Traceback (most recent call last):
    ...
    ValueError: maxDepth must be None or a positive integer
    
    >>> catalog.findRelations({'supervisor': 'Betty'}, maxDepth=-1)
    Traceback (most recent call last):
    ...
    ValueError: maxDepth must be None or a positive integer

.. [#filter] For instance:

    >>> list(catalog.findRelationTokens({'supervisor': 'Alice'},
    ...                                 targetFilter=female_filter,
    ...                                 targetQuery={None: 'Galyn'}))
    ['Galyn']
    >>> list(catalog.findRelationTokens({'supervisor': 'Alice'},
    ...                                 targetFilter=female_filter,
    ...                                 targetQuery={None: 'Not known'}))
    []
    >>> arbitrary = ['Alice', 'Chuck', 'Betty', 'Galyn']
    >>> def arbitrary_filter(relchain, query, catalog, cache):
    ...     return relchain[-1] in arbitrary
    >>> list(catalog.findRelationTokens({'supervisor': 'Alice'},
    ...                                 filter=arbitrary_filter,
    ...                                 targetFilter=female_filter))
    ['Betty', 'Galyn']
    

.. [#updates] The scenario we are looking at in this document shows a case
    in which special logic in the search index needs to address updates.
    For example, if we move Howie from Diane

    ::

                Alice
             __/     \__
        Betty           Chuck
        /   \           /   \
    Diane   Edgar   Frank   Galyn
      |
    Howie

    to Galyn

    ::

                Alice
             __/     \__
        Betty           Chuck
        /   \           /   \
    Diane   Edgar   Frank   Galyn
                              |
                            Howie

    then the search index is correct both for the new location and the old.

    >>> h.supervisor = g
    >>> catalog.index(h)
    >>> list(catalog.findRelationTokens({'supervisor': 'Diane'}))
    []
    >>> list(catalog.findRelationTokens({'supervisor': 'Betty'}))
    ['Diane', 'Edgar']
    >>> list(catalog.findRelationTokens({'supervisor': 'Chuck'}))
    ['Frank', 'Galyn', 'Howie']
    >>> list(catalog.findRelationTokens({'supervisor': 'Galyn'}))
    ['Howie']
    >>> h.supervisor = d
    >>> catalog.index(h) # move him back
    >>> list(catalog.findRelationTokens({'supervisor': 'Galyn'}))
    []
    >>> list(catalog.findRelationTokens({'supervisor': 'Diane'}))
    ['Howie']

.. [#same_set] The result of the query for Betty, Alice, and Zane are all the
    same.

    >>> res1 = catalog.findRelationTokens({'supervisor': 'Betty'})
    >>> res2 = catalog.findRelationTokens({'supervisor': 'Alice'})
    >>> res3 = catalog.findRelationTokens({'supervisor': 'Zane'})
    >>> list(res1) == list(res2) == list(res3)
    True

    The cycle doesn't pollute the index outside of the cycle.
    
    >>> res = catalog.findRelationTokens({'supervisor': 'Diane'})
    >>> list(res)
    ['Howie']
    >>> list(res) # it isn't lazy, it is precalculated
    ['Howie']

.. [#reverse_lookup] If you want to, look what happens when you go the
    other way:

    >>> res = list(catalog.findRelationChains({'supervisor': 'Zane'}))
    >>> def sortEqualLenByName(one, two):
    ...     if len(one) == len(two):
    ...         return cmp(one, two)
    ...     return 0
    ...
    >>> res.sort(sortEqualLenByName) # normalizes for test stability
    >>> print res # doctest: +NORMALIZE_WHITESPACE
    [(<Employee instance "Alice">,),
     (<Employee instance "Alice">, <Employee instance "Betty">),
     (<Employee instance "Alice">, <Employee instance "Chuck">),
     (<Employee instance "Alice">, <Employee instance "Betty">,
      <Employee instance "Diane">),
     (<Employee instance "Alice">, <Employee instance "Betty">,
      <Employee instance "Edgar">),
     cycle(<Employee instance "Alice">, <Employee instance "Betty">,
           <Employee instance "Zane">),
     (<Employee instance "Alice">, <Employee instance "Chuck">,
      <Employee instance "Frank">),
     (<Employee instance "Alice">, <Employee instance "Chuck">,
      <Employee instance "Galyn">),
     (<Employee instance "Alice">, <Employee instance "Betty">,
      <Employee instance "Diane">, <Employee instance "Howie">)]

    >>> [zc.relation.interfaces.ICircularRelationPath.providedBy(r)
    ...  for r in res]
    [False, False, False, False, False, True, False, False, False]
    >>> len(res[5].cycled)
    1
    >>> list(catalog.findRelations(res[5].cycled[0], maxDepth=1))
    [<Employee instance "Alice">]
