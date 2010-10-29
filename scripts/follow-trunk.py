#!/usr/bin/python
import sys
import simplejson as json

input = open(sys.argv[1])

entries = [ json.loads(s) for s in input ]
entries = [ x for x in entries if not x.get('kind') == 'file' ]
indexes = [ idx for idx, ent in enumerate(entries) if 'revno' in ent ]
indexes.append(None)

commits = []

for start, end in zip(indexes, indexes[1:]):
    op = entries[start:end]
    commit = op[0]
    actions = op[1:]
    commit['actions'] = actions
    commits.append(commit)

commits = commits[::-1]



trunk = 'pypy/trunk'
moves = []


def guess_newtrunk(commit):

    for action in commit['actions']:
        if action['action'] == 'add' and \
           (action['path'] == trunk or \
            action['path'] == trunk.rsplit('/',1)[0]):
                if 'copy_from' not in action:
                    if commit['revno']>320:
                        import pdb;pdb.set_trace()
                    continue
                copy_from = action['copy_from']
                if action['path'] != trunk:
                    copy_from += trunk[trunk.rindex('/'):]
                copy = '%s@%s' %(copy_from, action['copy_rev'])
                print commit['revno'], 'add', trunk, 'from', copy
                moves.append(commit)
                return copy_from
        import posixpath
    return trunk

for commit in commits:
    trunk = guess_newtrunk(commit)


import pprint
pprint.pprint(moves)
