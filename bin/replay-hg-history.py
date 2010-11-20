#!/usr/bin/python
import json
import os
from argparse import ArgumentParser
from hackbeil.hgutils import progressui, replay_commit, close_commit, abort_on_error
from hackbeil.branchreplay import BranchReplay
from hackbeil.histevents import EventReplay

from hackbeil.scripting.convert import targetdirname

from mercurial import localrepo


parser = ArgumentParser()
parser.add_argument('replay')
parser.add_argument('convert_roots')
parser.add_argument('target_repo')

options = parser.parse_args()

import pdb
import sys
sys.excepthook = lambda*k: pdb.pm()

ui = progressui()
ui.status('reading replay\n')
with open(options.replay) as fp:
    data = json.load(fp)
    br = BranchReplay.from_json(data)


ui.status('generating history event list\n')
er = EventReplay()
er.add_replay(br)


chunks = er.generate_chunklist()
ui.status('marking default\n')
default_chunk = er.findchunk('pypy/trunk', br.rev)
while default_chunk is not None:
    default_chunk.given_name = 'default'
    default_chunk = default_chunk.parent

total_changesets = 0
ui.status('creating statistics\n')
for idx, branch in enumerate(br.branch_history):
    ui.progress('scanning converts', pos=idx+1, total=len(br.branch_history))
    target = targetdirname(branch)
    repo = localrepo.localrepository(ui, os.path.join(options.convert_roots, target))
    total_changesets += len(repo)

ui.status('creating target %s\n' % options.target_repo)
target_repo = localrepo.localrepository(ui, options.target_repo)

def svnrev(ctx):
    try:

        convert_revision = ctx.extra()['convert_revision']
    except KeyError:
        ctx._repo.ui.status('%s@%s has extra %s'%(ctx._repo.root, ctx.rev(), ctx.extra()))
        raise
    base, _, rev = convert_revision.rpartition('@')

    return int(rev)


ui.status('building lookup table for completed commits\n')
completed_lookup = {}
closed_commits = set()

for commit in target_repo:
    ui.progress('scanning', pos=commit+1, total=len(target_repo))
    ctx = target_repo[commit]
    convert_rev = ctx.extra().get('convert_revision')
    completed_lookup[convert_rev] = commit
    if ctx.extra().get('close'):
        closed_commits.add(ctx.parents()[0].rev())


def maybe_replay_commit(repo, base, source_ctx, target_branch=None):
    target = repo[base]
    se = source_ctx.extra()
    convert_rev = se['convert_revision']
    if convert_rev in completed_lookup:
            return completed_lookup[convert_rev]
    return replay_commit(repo, base, source_ctx, target_branch)



total_converted = 0
for idx, chunk in enumerate(chunks):
    source_repo_name = targetdirname(chunk.branch)
    ui.status('replaying chunk %s %s/%s\n'%(chunk, idx+1, len(chunks)))
    source_repo = localrepo.localrepository(
        ui, os.path.join(options.convert_roots, source_repo_name))

    if chunk.parent and chunk.parent.branch is chunk.branch:
        rev = chunk.parent.nextrev
    else:
        rev = 0

    if chunk.parent:
        base = chunk.parent.nextbase
    else:
        base = -1

    tr = target_repo.transaction('commit')
    with abort_on_error(tr):
        while True:
            if rev not in source_repo:
                break
            source_ctx = source_repo[rev]

            ui.progress('replay',
                        pos=total_converted,
                        item=source_ctx.hex(),
                        total=total_changesets)
            if rev == len(source_repo) or (chunk.end and svnrev(source_ctx) >= chunk.end):
                chunk.nextrev = rev
                chunk.nextbase = base
                if chunk.end is not None and chunk.end == chunk.branch.end:
                    if base not in closed_commits:
                        close_commit(target_repo, base)
                break
            else:
                base = maybe_replay_commit(target_repo,
                                           base=base,
                                           source_ctx=source_ctx,
                                           target_branch=str(chunk.guessed_name()).split('@')[0]
                                          )
                rev += 1
                total_converted += 1
        tr.close()



