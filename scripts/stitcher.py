#!/usr/bin/python
import argparse
parser = argparse.ArgumentParser()
parser.add_argument('source')
parser.add_argument('--close', default=False, action='store_true')
parser.add_argument('--import-as-branch', default=None)
parser.add_argument('--source-branch', default='default')

group = parser.add_mutually_exclusive_group()
group.add_argument('--source-rev', default='tip')
group.add_argument('--svn-source-rev', type=int)


import hgext.progress
import sys
import errno

options = parser.parse_args()

from mercurial.ui import ui as Ui
from mercurial import commands, hg, localrepo, context

ui = Ui()
hgext.progress.uisetup(ui)

ui.status('opening repos\n')
target_repo = localrepo.localrepository(ui, '.')
stitch_source = localrepo.localrepository(ui, options.source)

if options.svn_source_rev:
    lastctx = None
    for idx, rev in enumerate(target_repo):
        ui.progress('finding svn target', pos=idx)
        ctx = target_repo[rev]
        branch = ctx.branch()
        if branch != options.source_branch:
            continue
        extra = ctx.extra()
        crev = extra.get('convert_revision')
        if crev:
            if '@' in crev:
                crev = crev.split('@')[-1] #from hg
            else:
                crev = crev.split(':')[-1] # from bzr
            crev = int(crev)
            if crev > options.svn_source_rev:
                if lastctx is None:
                    # this happens when the first svn revision of the branch
                    # is higher than the source svn revision. The sanest thing
                    # to do is to just abort.
                    ui.status('The first SVN revision of the branch is %d, which is higher than %d\n' % (crev, options.svn_source_rev))
                    sys.exit()
                
                options.source_rev=lastctx.rev()
                break
        lastctx = ctx
    else:
        ui.status('no fitting svn commit found\nusing latest instead\n')
        options.source_rev=ctx.rev()

current = target_repo[options.source_rev]
ui.status('found %s:%s (%s)\n' % (current.rev(), current.hex(), current.extra().get('convert_revision')))

ui.status('comparing first change and source parent\n')

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

ui.status('added %s removed %s changed %s common %s\n\n' % (
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
    copy = other.renamed() and other.renamed()[0]
    return context.memfilectx(
        path=path,
        data=other.data(),
        islink='l' in other.flags(),
        isexec='x' in other.flags(),
        copied = copy,
    )



ui.status('stitching initial revision\n')

tr = target_repo.transaction('commit')

base_extra = stitch_root.extra()
if options.import_as_branch:
    base_extra['branch'] = options.import_as_branch

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

try:
    nextnode = target_repo.commitctx(memctx)
except:
    tr.abort()
    raise


for index, commit in enumerate(stitch_source):
    # we already took the first commit
    if not index:
        continue
    ui.progress('stich rev', pos=index+1, total=len(stitch_source))

    stitch_root = stitch_source[index]

    base_extra = stitch_root.extra()
    if options.import_as_branch:
        base_extra['branch'] = options.import_as_branch

    memctx = context.memctx(
        repo=target_repo,
        parents=[nextnode, None],
        text=stitch_root.description(),
        user=stitch_root.user(),
        date=stitch_root.date(),
        files=sorted(stitch_root.files()),
        extra=base_extra,
        filectxfn = filectx,
    )

    try:
        nextnode = target_repo.commitctx(memctx)
    except:
        tr.abort()
        raise

if options.close:
    ui.status('closing branch %s\n' % memctx.branch())
    closectx = context.memctx(
        repo=target_repo,
        parents=[nextnode, None],
        text='closed branch %s' % memctx.branch(),
        user='sticher branch close',
        date=stitch_root.date(),
        files=[],
        extra={
            'branch': memctx.branch(),
            'close': 1,
        },
        filectxfn = None,
    )

    try:
        target_repo.commitctx(closectx)
    except:
        tr.abort()
        raise


tr.close()
tr.release()
ui.status('completed stitching of %s\n' % options.source)