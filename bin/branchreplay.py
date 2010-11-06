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

print 'branches with no changes'
pprint.pprint([b for b in branchreplay.branch_history if not b.changesets])

#print 'active branches'
#pprint.pprint(branchreplay.branches.values())



print 'number of all    branches', len(branchreplay.branch_history)
print 'number of active branches', len(branchreplay.branches)
