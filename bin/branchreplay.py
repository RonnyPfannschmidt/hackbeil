#!/usr/bin/python

import sys
import simplejson as json
from hackbeil.branchreplay import BranchReplay, Branch


branchreplay = BranchReplay(
    initial=Branch('pypy/trunk/src', 320)
)
import pdb
oldhook = sys.excepthook
def excepthook(*k):
    oldhook(*k)
    pdb.pm()
sys.excepthook = excepthook

fp = open(sys.argv[1])
for line in fp:
    data = json.loads(line)
    if 'revno' in data:
        branchreplay.revdone(nextrev=data['revno'])
    else:
        branchreplay.event(**data)



import pprint
#print 'all branches'
#pprint.pprint(branchreplay.branch_history)

no_changes = [b for b in branchreplay.branch_history if not b.changesets]
for b in no_changes:
    print b.path, '%s-%s'%(b.startrev, b.endrev)
#pprint.pprint(no_changes)
#print 'branches with no changes', len(no_changes)
#print 'active branches'
#pprint.pprint(branchreplay.branches.values())



