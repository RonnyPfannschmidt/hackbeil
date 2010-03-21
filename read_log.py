#!/usr/bin/python
import sys
import StringIO
dump = open(sys.argv[1], 'r')

def headerkv(text):
    key, value = text.split(':', 1)
    value = value.strip()
    if value.isdigit():
        value = int(value)
    return key, value

def read_header(fd):
    return dict(map(headerkv, iter(fd.readline, '\n')))

def read_props_inner(fd):
    while True:
        line = fd.readline().strip()
        if line == 'PROPS-END':
            return
        kind, len = line.split(' ')
        assert kind == 'K'
        key = fd.read(int(len))
        fd.read(1) # padding newline

        kind, len = fd.readline().strip().split()
        assert kind == 'V'
        value = fd.read(int(len))
        fd.read(1) # padding newline
        yield key, value



def read_props(fd, pl):
    if not pl:
        return
    raw = fd.read(pl)
    return read_props_inner(StringIO.StringIO(raw))

def read_entry(fd):
    headers = read_header(fd)
    cl = headers.get('Content-length', 0)
    pl = headers.get('Prop-content-length', 0)
    props = dict(read_props(fd, pl) or [])
    data = fd.read(cl-pl)
    headers.update({
        'props': props,
        'data': data,
        })
    return headers



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
