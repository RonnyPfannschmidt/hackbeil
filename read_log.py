#!/usr/bin/python
import sys
from svn_dump_reader import read_header, read_entry, Revision


ignore_paths = [
    'vendor',
    'codespeak',
    'xpython',
    'trunk/www',
    'pypy/trunk/www/moininstance',
    'vpath',
    'rlcompleter2',
    'epoz',
    'kupu',
    'z3',
    'user',
    'rr',
]



def path_filter(node):
    path = node['Node-path']
    return any(path.startswith(x) for x in ignore_paths)

def change_filter(node):
    return node['Node-action'] == 'change'

class InterestingRevision(Revision):
    filters = Revision.filters + [path_filter]


dump = open(sys.argv[1], 'r')
for revision in InterestingRevision.iter_file(dump):
    print 'rev %s:'% revision.id
    print '  author:', revision.author
    print '  log:', revision.message.split('\n')[0]
    print '  files:'

    for node in revision.nodes:
        print '    -', node['Node-action'], node['Node-path']
        if 'Node-copyfrom-path' in node:
            print '        from', node['Node-copyfrom-path'], node["Node-copyfrom-rev"]

