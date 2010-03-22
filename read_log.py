#!/usr/bin/python
import sys
from svn_dump_reader import iter_file
from model import Revision


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
    'basil'
]



def path_filter(node):
    return any(node.path.startswith(x) for x in ignore_paths)

class InterestingRevision(Revision):
    filters = [path_filter]


dump = open(sys.argv[1], 'r')
for revision in iter_file(dump, InterestingRevision):
    if not any(node.copy_from for node in revision.nodes):
        continue
    
    print 'rev %s:'% revision.id
    print '  author:', revision.author
    print '  log:', revision.message.split('\n')[0]
    print '  files:'
    revision.transform_renames()
    for node in revision.nodes:
        print '    -', node.action, node.path, node.kind or ''
        if node.copy_from:
            print '        from', node.copy_from, node.copy_rev

