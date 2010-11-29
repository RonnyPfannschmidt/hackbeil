from os import path
import posixpath
from mercurial.localrepo import localrepository
from hackbeil.hgutils import svnrev
def targetdirname(branch):
    return '{base}@{start}'.format(
        base=branch.path.split('/')[-1],
        start=branch.start,
    )

def do_convert(converter, branch, repo, basedir, authormap):
    targetdir = targetdirname(branch)

    call_args = {
        'source': posixpath.join(repo, branch.path),
        'start': branch.start,
        'end': (' -r %s' % (branch.end-1)) if branch.end is not None else '',
        'dest': path.join(basedir, targetdir),
        'authormap': authormap,
    }

    converter(**call_args)


def convert_all(ui, replay, convert_call, repo, basedir, authormap):
    for idx, branch in enumerate(replay.branch_history):
        name = targetdirname(branch)

        ui.status('%s %s/%s\n'%(name, idx, len(replay.branch_history))),
        ui.progress('converting repos',
                    pos=idx,
                    total=len(replay.branch_history),
                    item=name,
                   )
        if branch.end and path.exists(path.join(basedir, name)):
            #XXX: fragility?
            dest = localrepository(ui, path.join(basedir, name))
            tip = dest['tip']
            if branch.changesets:
                if svnrev(tip) == max(branch.changesets):
                    continue
            else:
                continue

        do_convert(convert_call, branch, repo, basedir, authormap)

