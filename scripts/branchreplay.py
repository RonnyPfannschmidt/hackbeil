#!/usr/bin/python

import sys
import simplejson as json
from hackbeil.branchreplay import BranchReplay


branchreplay = BranchReplay()

fp = open(sys.argv[1])
for line in fp:
    data = json.loads(line)
    if 'revno' in data:
        branchreplay.revdone(nextrev=data['revno'])
    else:
        branchreplay.event(**data)


import pprint
pprint.pprint(branchreplay.branch_history)
pprint.pprint(branchreplay.branches)

print 'history', len(branchreplay.branch_history)
print 'branches', len(branchreplay.branches)
