#!/usr/bin/python

import sys
import simplejson as json
from mercurial import ui
from hgext import progress
ui = ui.ui()
import posixpath


progress.uisetup(ui)



assert len(sys.argv)==3, 'script <int> <out>'
assert sys.argv[1] != sys.argv[2], 'in shouldnt be out'

input = open(sys.argv[1])
output = open(sys.argv[2], 'w')


buffer = []
has_pypy = False

for line in input:
    data = json.loads(line)
    if 'revno' in data:
        ui.progress('rev', pos=data['revno'], total=78000)
    if data.get('kind') == 'file':
        continue

    if 'svn:ignore' in data:
        continue
    if 'svn:externals' in data:
        continue

    if 'path' in data:
        path = data['path']
        if not path.startswith('pypy'):
            continue
        has_pypy = True
        if path.endswith('.txt'):
            continue
        if path.count('/') >= 4:
            continue
        base, name = posixpath.split(path)

        if base not in ['pypy', 'pypy/branch', 'pypy/release']:
            continue

        if base == 'pypy' and name in ['branch', 'tag', 'django', 'www']:
            continue

    if 'revno'in data:
        if len(buffer)>1 or (has_pypy and 'merge' in buffer[0].lower()):
            output.writelines(buffer)
        has_pypy = False
        buffer = []

    if data.get('svn:log'):
        data['svn:log'] = data['svn:log'].splitlines()[0]
    data.pop('props_size', None)
    data.pop('svn:date', None)
    buffer.append(json.dumps(data) + '\n')

output.close()
