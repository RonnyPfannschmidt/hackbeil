#!/usr/bin/python
from argparse import ArgumentParser
from hackbeil.hgutils import progressui, replay_commit, close_commit, abort_on_error
from hackbeil.branchreplay import BranchReplay
from hackbeil.histevents import EventReplay

from hackbeil.scripting.convert import targetdirname

from mercurial import localrepo


import pdb
import sys
import traceback
def hk(*k):
    pdb.pm()
    traceback.print_exc()

sys.excepthook = hk

parser = ArgumentParser()
parser.add_argument('replay')
parser.add_argument('convert_roots')
parser.add_argument('target_repo')

options = parser.parse_args()
import os



ui = progressui()
ui.status('reading replay\n')
import json
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




def maybe_replay_commit(repo, base, source_ctx, target_branch=None):
    target = repo[base]
    se = source_ctx.extra()
    for child in target.children():
        ce = child.extra()
        if ce['convert_revision'] == se['convert_revision']:
            return child.rev()
    return replay_commit(repo, base, source_ctx, target_branch)



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

            ui.progress('replay ' + source_repo_name,
                        pos=rev+1,
                        item=source_ctx.hex(),
                        total=len(source_repo))
            if rev == len(source_repo) or (chunk.end and svnrev(source_ctx) >= chunk.end):
                chunk.nextrev = rev
                chunk.nextbase = base
                break
            else:
                base = maybe_replay_commit(target_repo, base=base, source_ctx=source_ctx, target_branch=chunk.guessed_name())
                rev += 1
        ui.progress('replay ' + source_repo_name, pos=None)
        tr.close()



