#!/usr/bin/python
import argparse
parser = argparse.ArgumentParser()
parser.add_argument('replay', type=argparse.FileType('r'))
parser.add_argument('basedir')


options = parser.parse_args()

from hackbeil.branchreplay import BranchReplay
from hackbeil.histevents import EventReplay
from hackbeil.hgutils import progressui

ui = progressui()

import json
import os

br = BranchReplay.from_json(json.load(options.replay))

from hackbeil.scripting.convert import targetdirname
import mercurial.localrepo

commit_counts = {}

for idx, branch in enumerate(br.branch_history):
    td = targetdirname(branch)
    ui.progress('scanning repo', pos=idx, total=len(br.branch_history),
                item=td)


    repo = mercurial.localrepo.localrepository(ui, os.path.join(options.basedir, td))
    commit_counts[td] = len(repo)
    if branch.start in branch.changesets:
        ui.debug('%s start is cset\n'%td)

commits = sum(commit_counts.values())
changesets = sum(len(x.changesets) for x in br.branch_history)

unique_changesets = set()
for x in  br.branch_history:
    unique_changesets.update(x.changesets)

ui.status('number of repos %s\n'%len(br.branch_history))
ui.status('amount of commits: %s unique %s\n'%(commits, len(unique_changesets)))
ui.status('amount of changesets: %s\n'%changesets)
ui.status('difference: %s\n'%(commits - changesets))




from hackbeil.histevents import EventReplay

er = EventReplay()
er.add_replay(br)
for idx, chunk in enumerate(er.generate_chunklist()):

    branch = chunk.branch
    td = targetdirname(branch)
    ui.progress('scanning chunk', pos=idx, item=str(chunk))

    repo = mercurial.localrepo.localrepository(ui, os.path.join(options.basedir, td))
    changesets = chunk.changesets()
    for commit in repo:
        ctx = repo[commit]
        changesets.discard(int(ctx.extra()['convert_revision'].split('@')[-1]))

    if changesets:
        ui.status('%s %s %s\n'%(branch, chunk, changesets))

