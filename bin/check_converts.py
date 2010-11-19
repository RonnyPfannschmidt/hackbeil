#!/usr/bin/python
import argparse
parser = argparse.ArgumentParser()
parser.add_argument('replay', type=argparse.FileType('r'))
parser.add_argument('basedir')
parser.add_argument('target')

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

ui.status('beginning chunk scanning\n')
er = EventReplay()
er.add_replay(br)

if 0:
    ui.status('scanning separate chunks')
    for idx, chunk in enumerate(er.generate_chunklist()):

        branch = chunk.branch
        td = targetdirname(branch)
        ui.progress('scanning chunk ' + td, pos=idx, item=str(chunk))

        repo = mercurial.localrepo.localrepository(ui, os.path.join(options.basedir, td))
        changesets = chunk.changesets()
        for commit in repo:
            ctx = repo[commit]
            changesets.discard(int(ctx.extra()['convert_revision'].split('@')[-1]))

        if changesets:
            ui.status('%s %s %s\n'%(branch, chunk, changesets))

ui.status('scanning target\n')

repo = mercurial.localrepo.localrepository(ui, options.target)

for commit in repo:
    ui.progress('scanning target', pos=commit+1, total=len(repo))
    ctx = repo[commit]
    crev = ctx.extra().get('convert_revision')
    if crev is not None:
        branch, rev = crev.rsplit('@')
        branch = branch.split('/',1)[-1]
        rev = int(rev)
        branch = br.findbranch(branch, rev)

        assert branch is not None, crev

        if rev == branch.start:
            branch.changesets.discard(rev)
        else:
            if rev in branch.changesets:
                branch.changesets.remove(rev)
            else:
                ui.debug('%s missing %s\n' % (branch, rev))


ui.status('finding branches missing in target\n')

number = 0
missing = 0
for branch in br.branch_history:
    if branch.changesets:
        ui.status('%s has %s unconverted revisions\n'% (branch, len(branch.changesets)))
        number+=1
        missing +=len(branch.changesets)

ui.status('%s branches have %s unconverted changesets\n' %(number, missing))

