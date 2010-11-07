#!/usr/bin/python
import sys

from hackbeil.hgutils import progressui
from hackbeil.branchreplay import BranchReplay, Branch, replay, json_listing

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


output = open(sys.argv[2], 'w')


replay(
    branchreplay=branchreplay,
    items=json_listing(sys.argv[1], ui),
)

ui.status('writing conversions')

for branch in branchreplay.branch_history:
    if branch.source_branch:
        fromname = ' {path}@{copy_rev}'.format(
            path=branch.source_branch.path,
            copy_rev = branch.source_rev,
        )
    else:
        fromname = ''
    output.write('{branch.name} {branch.path} {branch.startrev} {branch.endrev}'
                 '{fromname}\n'.format(
                        fromname=fromname,
                        branch=branch,
                 ))
output.close()

ui.status(' done\n')
