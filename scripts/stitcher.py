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


from hackbeil import hgutils # import progressui, find_svn_rev, copying_fctxfn

import hgext.progress
import sys
import errno

options = parser.parse_args()

from mercurial import commands, hg, localrepo, context

ui = hgutils.progressui()

ui.status('opening repos\n')
target_repo = localrepo.localrepository(ui, '.')
stitch_source = localrepo.localrepository(ui, options.source)

if options.svn_source_rev:
    source_rev = hgutils.find_svn_rev(
        repo=target_repo,
        wanted_branch=options.source_branch,
        wanted_rev=options.svn_source_rev,
    )
else:
    source_rev = options.source_rev

current = target_repo[source_rev]
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
    filectxfn = hgutils.copying_fctxfn(stitch_root),
)

with hgutils.abort_on_error(tr):
    nextnode = target_repo.commitctx(memctx)


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
        filectxfn = hgutils.copying_fctxfn(stitch_root),
    )

    with hgutils.abort_on_error(tr):
        nextnode = target_repo.commitctx(memctx)

if options.close:

    with hgutils.abort_on_error(tr):
        hgutils.close_commit(target_repo, nextnode)


tr.close()
ui.status('completed stitching of %s\n' % options.source)
