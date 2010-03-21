#!/usr/bin/python
import sys
import StringIO
from svn_dump_reader import read_header, read_entry


dump = open(sys.argv[1], 'r')


print read_header(dump)
print read_header(dump)
print read_entry(dump)

nodes = []
real = 0


while True:
    try:
        entry = read_entry(dump)
    except ValueError:
        break
    if 'Revision-number' in entry:
        if not nodes:
            continue
        for node in nodes:
            print '    ', node['Node-action'], node['Node-path']
            if 'Node-copyfrom-path' in node:
                print '        from', node['Node-copyfrom-path'], node["Node-copyfrom-rev"]
        print 'rev', entry['Revision-number'], 'has %s nodes' % len(nodes)
        real+=1
        nodes = []
    else:
        if not entry: continue
        if entry == {'data': '', 'props': {}}: continue
        next = False
        for path in [
                'vendor',
                'codespeak',
                'xpython',
                'trunk/www',
                'pypy/trunk/www/moininstance',
                'vpath',
                'rlcompleter2',
                'rlcompleter2',
                ]:
            if entry['Node-path'].startswith(path):
                next = True
        if next:
            continue

        if entry['Node-action'] == 'change': continue
        nodes.append(entry)

print 'found', real, 'real nodes'
