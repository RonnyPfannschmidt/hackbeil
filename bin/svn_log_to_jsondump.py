#!/usr/bin/python
import argparse

from hackbeil.hgutils import progressui
import simplejson
ui = progressui()
parser = argparse.ArgumentParser()
parser.add_argument('svndir')
parser.add_argument('dump', type=argparse.FileType('w'))

options = parser.parse_args()
items = []
import subvertpy.ra

conn = subvertpy.ra.RemoteAccess(options.svndir)
last_rev = conn.get_latest_revnum()
ui.status('running log \n')
log_iter = conn.iter_log(paths=None,
                         start=last_rev,
                         end=0,
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
    for path, (log_action, copy_from, copy_rev, kind_id) in changed_paths.items():
        act = action_mapping[log_action]
        kind =  kind_mapping[kind_id]
        if act == 'change' or kind == 'file':
            continue
        # stripping the initial /
        action = { 'action': act, 'path': path[1:], 'kind': kind, }
        if copy_from is not None:
            action.update({
                'copy_from': copy_from[1:], # strip leading / as well
                'copy_rev': copy_rev,
            })
        items.append(action)

    props['revno'] = rev
    items.append(props)

    ui.progress('parse rev', pos=abs(rev - last_rev-1), total=last_rev)


with options.dump as out:
    for index, item in enumerate(reversed(items)):
        ui.progress('write data', pos=index+1, total=len(items))
        simplejson.dump(item, out)
        out.write('\n')

ui.status('done\n')
