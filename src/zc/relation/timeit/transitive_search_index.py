"""

The result has three big sections, one for `findRelationTokens`, one for
`findValueTokens`, and one for `canFind`.  Within each section, we have six
searches, each broader than the last.  A 'brute' result is a result without
a search index.  A 'relation' result uses a search index without a configured
value index.  A 'value' result uses a search index with a configured value
index.  'relation' and 'value' results should really only differ materially
for `findValueTokens`.  A 'brute_generate' result shows how fast it takes to
get the generator back from a brute search, without actually iterating over
it, and is not pertinent for `canFind`.

Example result:

[('control_result', 0.0094759464263916016),
 "**** res = list(catalog.findRelationTokens({'token': 9})) ****",
 '**** [109] ****',
 ('brute_generate', 0.2457740306854248),
 ('brute', 0.81798601150512695),
 ('relation', 0.52101397514343262),
 ('value', 0.51753401756286621),
 "**** res = list(catalog.findRelationTokens({'token': 7})) ****",
 '**** [107] ****',
 ('brute_generate', 0.24491000175476074),
 ('brute', 0.83113908767700195),
 ('relation', 0.53361701965332031),
 ('value', 0.52347803115844727),
 "**** res = list(catalog.findRelationTokens({'token': 5})) ****",
 '**** [105, 107, 108, 109] ****',
 ('brute_generate', 0.24980616569519043),
 ('brute', 1.9965240955352783),
 ('relation', 0.5299079418182373),
 ('value', 0.53121399879455566),
 "**** res = list(catalog.findRelationTokens({'token': 3})) ****",
 '**** [103, 105, 106, 107, 108, 109] ****',
 ('brute_generate', 0.24709606170654297),
 ('brute', 2.8365921974182129),
 ('relation', 0.54007720947265625),
 ('value', 0.53515410423278809),
 "**** res = list(catalog.findRelationTokens({'token': 1})) ****",
 '**** [101, 103, 104, 105, 106, 107, 108, 109] ****',
 ('brute_generate', 0.24880099296569824),
 ('brute', 3.6703901290893555),
 ('relation', 0.53357386589050293),
 ('value', 0.53384017944335938),
 "**** res = list(catalog.findRelationTokens({'token': 0})) ****",
 '**** [100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111] ****',
 ('brute_generate', 0.25098800659179688),
 ('brute', 5.3719911575317383),
 ('relation', 0.53967404365539551),
 ('value', 0.53260326385498047),
 '------------------',
 '------------------',
 "**** res = list(catalog.findValueTokens('children', {'token': 9})) ****",
 '**** [23, 24] ****',
 ('brute_generate', 0.25597715377807617),
 ('brute', 0.87791824340820312),
 ('relation', 0.71430587768554688),
 ('value', 0.53523707389831543),
 "**** res = list(catalog.findValueTokens('children', {'token': 7})) ****",
 '**** [17, 18, 19] ****',
 ('brute_generate', 0.25435924530029297),
 ('brute', 0.9038851261138916),
 ('relation', 0.73513698577880859),
 ('value', 0.53882598876953125),
 "**** res = list(catalog.findValueTokens('children', {'token': 5})) ****",
 '**** [7, 8, 9, 17, 18, 19, 20, 21, 22, 23, 24] ****',
 ('brute_generate', 0.2563321590423584),
 ('brute', 2.2175660133361816),
 ('relation', 0.8459780216217041),
 ('value', 0.54215097427368164),
 "**** res = list(catalog.findValueTokens('children', {'token': 3})) ****",
 '**** [5, 6, 7, 8, 9, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24] ****',
 ('brute_generate', 0.25664114952087402),
 ('brute', 3.1539299488067627),
 ('relation', 0.91316413879394531),
 ('value', 0.55379605293273926),
 "**** res = list(catalog.findValueTokens('children', {'token': 1})) ****",
 '**** [3, 4, 5, 6, 7, 8, 9, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24] ****',
 ('brute_generate', 0.25446605682373047),
 ('brute', 4.058326244354248),
 ('relation', 0.98118209838867188),
 ('value', 0.54912614822387695),
 "**** res = list(catalog.findValueTokens('children', {'token': 0})) ****",
 '**** [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32] ****',
 ('brute_generate', 0.25460124015808105),
 ('brute', 6.0014550685882568),
 ('relation', 1.1424670219421387),
 ('value', 0.55950188636779785),
 '------------------',
 '------------------',
 "**** res = catalog.canFind({'token': 9}, targetQuery={'children': 23}) ****",
 '**** True ****',
 ('brute', 0.81314396858215332),
 ('relation', 0.68167209625244141),
 ('value', 0.68214011192321777),
 "**** res = catalog.canFind({'token': 7}, targetQuery={'children': 23}) ****",
 '**** False ****',
 ('brute', 0.98219418525695801),
 ('relation', 0.67153406143188477),
 ('value', 0.6687159538269043),
 "**** res = catalog.canFind({'token': 5}, targetQuery={'children': 23}) ****",
 '**** True ****',
 ('brute', 2.0033540725708008),
 ('relation', 0.70535111427307129),
 ('value', 0.70386195182800293),
 "**** res = catalog.canFind({'token': 3}, targetQuery={'children': 23}) ****",
 '**** True ****',
 ('brute', 2.8076090812683105),
 ('relation', 0.72887015342712402),
 ('value', 0.71839404106140137),
 "**** res = catalog.canFind({'token': 1}, targetQuery={'children': 23}) ****",
 '**** True ****',
 ('brute', 3.6096680164337158),
 ('relation', 0.73476409912109375),
 ('value', 0.73782920837402344),
 "**** res = catalog.canFind({'token': 0}, targetQuery={'children': 23}) ****",
 '**** True ****',
 ('brute', 5.2542290687561035),
 ('relation', 0.75870609283447266),
 ('value', 0.75950288772583008),
 '------------------',
 '------------------']

Notes:

- While simply creating a generator is unsurprisingly the least work, if you
  want all the results then the index is always a win (on read!), even in the
  smallest search.  Even in this small graph it can give us factor-of-10
  results at the broadest search.

- The relation index, without the additional value index, still does a pretty
  good job on value searches, as hoped.

It might be nice to be able to demand a generator even when you have a search
index, in case you only want a result or two for a given call.  Probably
should be YAGNI for now.

It would be nice to add some further tests later to see how much worse
the write performance is when you have these indexes.

(I want to write look at the intransitive search too: is it really only
useful when you have a query factory that mutates the initial search, as
in tokens.txt?)

"""

import timeit
import pprint

# see zc/relation/searchindex.txt

brute_setup = '''
import BTrees
relations = BTrees.family64.IO.BTree()
relations[99] = None # just to give us a start

class Relation(object):
    def __init__(self, token, children=()):
        self.token = token
        self.children = BTrees.family64.IF.TreeSet(children)
        self.id = relations.maxKey() + 1
        relations[self.id] = self


def token(rel, self):
    return rel.token

def children(rel, self):
    return rel.children

def dumpRelation(obj, index, cache):
    return obj.id

def loadRelation(token, index, cache):
    return relations[token]

import zc.relation.queryfactory
factory = zc.relation.queryfactory.TransposingTransitive(
    'token', 'children')
import zc.relation.catalog
catalog = zc.relation.catalog.Catalog(
    dumpRelation, loadRelation, BTrees.family64.IO, BTrees.family64)
catalog.addValueIndex(token)
catalog.addValueIndex(children, multiple=True)
catalog.addDefaultQueryFactory(factory)

for token, children in (
    (0, (1, 2)), (1, (3, 4)), (2, (10, 11, 12)), (3, (5, 6)),
    (4, (13, 14)), (5, (7, 8, 9)), (6, (15, 16)), (7, (17, 18, 19)),
    (8, (20, 21, 22)), (9, (23, 24)), (10, (25, 26)),
    (11, (27, 28, 29, 30, 31, 32))):
    catalog.index(Relation(token, children))

'''

#                                  _____________0_____________
#                                 /                           \
#                        ________1_______                ______2____________
#                       /                \              /          |        \
#                ______3_____            _4_          10       ____11_____   12
#               /            \          /   \         / \     / /  |  \ \ \
#       _______5_______       6       13     14     25  26  27 28 29 30 31 32
#      /       |       \     / \
#    _7_      _8_       9   15 16
#   / | \    / | \     / \
# 17 18 19  20 21 22  23 24

relation_index_setup = brute_setup + '''
import zc.relation.searchindex
catalog.addSearchIndex(
    zc.relation.searchindex.TransposingTransitive('token', 'children'))
'''

value_index_setup = brute_setup + '''
import zc.relation.searchindex
catalog.addSearchIndex(
    zc.relation.searchindex.TransposingTransitive(
        'token', 'children', names=('children',)))
'''

relations_run_template = '''
res = list(catalog.findRelationTokens({'token': %d}))
'''

value_run_template = '''
res = list(catalog.findValueTokens('children', {'token': %d}))
'''

canfind_run_template = '''
res = catalog.canFind({'token': %d}, targetQuery={'children': 23})
'''

options = (9,7,5,3,1,0)

runs = 10000

control = timeit.Timer('res = catalog.__len__()\nlist()', brute_setup)
control_result = min(control.repeat(3, runs))
d = [('control_result', control_result)]

for template in (relations_run_template, value_run_template,
                 canfind_run_template):
    for o in options:
        run = template % (o,)
        # verify we get the same results
        brute_globs = {}
        relation_globs = {}
        value_globs = {}
        exec brute_setup + run in brute_globs
        exec relation_index_setup + run in relation_globs
        exec value_index_setup + run in value_globs
        brute = brute_globs['res']
        relation = relation_globs['res']
        value = value_globs['res']
        canfind = template == canfind_run_template
        if not canfind:
            brute.sort()
        assert brute == relation == value, '%s: %r, %r, %r' % (
            run, brute, relation, value)
        # end verify
        d.append('**** %s ****' % (run.strip(),))
        d.append('**** %s ****' % (brute,))
        if not canfind:
            # show how long it takes to make the generator
            altered = run.replace('list(', '', 1)
            altered = altered.replace(')', '', 1)
            d.append((
                'brute_generate',
                min(timeit.Timer(
                    altered, brute_setup).repeat(3, runs)) - control_result))
        d.append((
            'brute',
            min(timeit.Timer(
                run, brute_setup).repeat(3, runs)) - control_result))
        d.append((
            'relation',
            min(timeit.Timer(
                run, relation_index_setup).repeat(3, runs)) - control_result))
        d.append((
            'value',
            min(timeit.Timer(
                run, value_index_setup).repeat(3, runs)) - control_result))
        
    d.append('------------------')
    d.append('------------------')

pprint.pprint(d)
