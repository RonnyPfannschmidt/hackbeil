#!/usr/bin/python

import sys
import simplejson as json
from hackbeil.branchreplay import BranchReplay, Branch, replay, json_listing

from hackbeil.hgutils import progressui

import pdb
oldhook = sys.excepthook
def excepthook(*k):
    oldhook(*k)
    pdb.pm()
sys.excepthook = excepthook


ui = progressui()

branchreplay = BranchReplay(
    initial=Branch('pypy/trunk/src', 320),
    tag_prefixes=['pypy/tag', 'pypy/release'],
    required_path='pypy/',
)

replay(
    branchreplay=branchreplay,
    items=json_listing(sys.argv[1], ui),
)

import pprint
#print 'all branches'
#pprint.pprint(branchreplay.branch_history)

no_changes = [b for b in branchreplay.branch_history if not b.changesets]
for b in no_changes:
    ui.status('%(path)s %(startrev)s-%(endrev)s\n'%vars(b))
#pprint.pprint(no_changes)
#print 'branches with no changes', len(no_changes)
#print 'active branches'
#pprint.pprint(branchreplay.branches.values())



