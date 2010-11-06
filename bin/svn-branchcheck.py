#!/usr/bin/python

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('svnbase')
parser.add_argument('branch')
parser.add_argument('range')

options = parser.parse_args()

import subvertpy.ra

conn = subvertpy.ra.RemoteAccess(options.svnbase + options.branch)

start, end = options.range.split('-')
start = int(start)
end = int(end)-1 if end != 'None' else -1

log_iter = conn.iter_log(start=start,
                         end=end,
                         paths=None,
                         discover_changed_paths=True,
                        )


for changed_files, revno, props, has_children in log_iter:
    props = dict((k.replace('svn:',''), v) for k,v in props.items())
    props['log'] = props.get('log', 'not given').splitlines()[0]

    print '{revno} {author} {log}'.format(revno=revno, **props)
    for name in sorted(changed_files):
        print ' ', name, changed_files[name][0]
