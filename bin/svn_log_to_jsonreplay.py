#!/usr/bin/python
import argparse
import simplejson

from hackbeil.hgutils import progressui
ui = progressui()
parser = argparse.ArgumentParser()
parser.add_argument('svndir')
parser.add_argument('dump', type=argparse.FileType('w'))

options = parser.parse_args()
items = []
import subvertpy.ra


from hackbeil.branchreplay import BranchReplay, Branch

br = BranchReplay(
    initial=Branch('pypy/trunk', 320),
    required_path='pypy',
)

conn = subvertpy.ra.RemoteAccess(options.svndir)
last_rev = conn.get_latest_revnum()
ui.status('running log \n')
log_iter = conn.iter_log(paths=None,
                         start=0,
                         end=last_rev,
                         discover_changed_paths=True,
                        )

action_mapping = {
    'M': 'change',
    'A': 'add',
    'D': 'delete',
    'R': 'replace',
}

kind_mapping = {
    subvertpy.NODE_DIR: 'dir',
    subvertpy.NODE_FILE: 'file',

}

for (changed_paths, rev, props, has_children) in log_iter:
    if changed_paths is None:
        continue
    br.revdone(nextrev=rev)

    for path, (log_action, copy_from, copy_rev, kind_id) in changed_paths.items():
        act = action_mapping[log_action]
        kind =  kind_mapping[kind_id]
        # stripping the initial /
        action = { 'action': act, 'path': path[1:], 'kind': kind, }
        if copy_from is not None:
            action.update({
                'copy_from': copy_from[1:], # strip leading / as well
                'copy_rev': copy_rev,
            })
        br.event(**action)

    ui.progress('parse rev', pos=rev, total=last_rev)



with options.dump as out:
    simplejson.dump(br.to_json(), out, indent=2)

ui.status('done\n')
