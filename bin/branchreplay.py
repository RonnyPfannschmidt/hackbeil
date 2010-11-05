#!/usr/bin/python

import sys
import simplejson as json
from hackbeil.branchreplay import BranchReplay, Branch


branchreplay = BranchReplay(
    initial=Branch('pypy/trunk/src', 320)
)
import pdb
def excepthook(*k):
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
print 'active branches'
pprint.pprint(branchreplay.branches.values())

print 'number of all    branches', len(branchreplay.branch_history)
print 'number of active branches', len(branchreplay.branches)
