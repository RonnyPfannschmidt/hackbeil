#!/usr/bin/python
import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--branch', default=None)
parser.add_argument('--target_rev', default='tip')
parser.add_argument('source')
import hgext.progress

import errno

options = parser.parse_args()

from mercurial.ui import ui as Ui
from mercurial import commands, hg, localrepo, context

ui = Ui()
hgext.progress.uisetup(ui)

target_repo = localrepo.localrepository(ui, '.')
stitch_source = localrepo.localrepository(ui, options.source)

ui.status('comparing first change and target parent')
current = target_repo[options.target_rev]

stitch_root = stitch_source[0]
new_files = set(stitch_root)
old_files = set(current)

common = sorted(old_files&new_files)

added = new_files-old_files
removed = old_files-new_files
changed = set(
    name for name in common
    if current[name].data() != stitch_root[name].data()
)

ui.status('added %s removed %s changed %s common %s\n' % (
    len(added),
    len(removed),
    len(changed),
    len(common),
))



def filectx(repo, ctx, path):
    if path not in stitch_root:
        error = IOError()
        #error.errno=errno.ENOENT
        #error.filename=path
        raise error

    other = stitch_root[path]
    return context.memfilectx(
        path=path,
        data=other.data(),
        islink='l' in other.flags(),
        isexec='x' in other.flags(),
    )





base_extra = stitch_root.extra()
if options.branch:
    base_extra['branch'] = options.branch

memctx = context.memctx(
    repo=target_repo,
    parents=[current.node(), None],
    text=stitch_root.description(),
    user=stitch_root.user(),
    date=stitch_root.date(),
    files=sorted(added|removed|changed),
    extra=base_extra,
    filectxfn = filectx,
)


target_repo.commitctx(memctx)



raise SystemExit
#ui.progress('stich rev', pos=0, total=len(stitch_source))
for i in range(20):
    import time
    time.sleep(0.1)
    ui.progress('stich rev', pos=i, total=10)
