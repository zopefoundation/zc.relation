import persistent
import BTrees
import zope.interface

import zc.relation.interfaces
import zc.relation.catalog

##############################################################################
# a common case transitive queries factory

_marker = object()

class TransposingTransitive(persistent.Persistent):
    zope.interface.implements(zc.relation.interfaces.IQueryFactory)

    def __init__(self, name1, name2):
        self.names = [name1, name2] # a list so we can use index

    def __call__(self, query, catalog):
        static = []
        name = other = _marker
        for nm, val in query.items():
            try:
                ix = self.names.index(nm)
            except ValueError:
                static.append((nm, val))
            else:
                if name is not _marker:
                    # both were specified: no transitive search known.
                    return None
                else:
                    name = nm
                    other = self.names[not ix]
        if name is not _marker:
            def getQueries(relchain):
                if not relchain:
                    yield query
                    return
                if other is None:
                    rels = relchain[-1]
                else:
                    tokens = catalog.getValueTokens(other, relchain[-1])
                    if not tokens:
                        return
                    rels = zc.relation.catalog.Any(tokens)
                res = BTrees.family32.OO.Bucket(static)
                res[name] = rels
                yield res
            return getQueries

    def __eq__(self, other):
        return (isinstance(other, self.__class__) and
                set(self.names) == set(other.names))

    def __ne__(self, other):
        return not self.__eq__(other)
