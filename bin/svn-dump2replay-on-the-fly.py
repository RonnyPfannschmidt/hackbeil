#!/usr/bin/python
import subprocess
import argparse
import os
parser = argparse.ArgumentParser()
parser.add_argument('replay')
parser.add_argument('svnrepo')
options = parser.parse_args()

svnrepo = options.svnrepo

if svnrepo[:7] == 'file://':
    svnrepo = svnrepo[7:]

from hackbeil.branchreplay import BranchReplay, Branch, replay, json_listing
from hackbeil.svn_dump_reader import walk_entries
from hackbeil.hgutils import progressui
ui = progressui()

branchreplay = BranchReplay(
    initial=Branch('pypy/trunk/src', 320),
    tag_prefixes=['pypy/tag', 'pypy/release'],
    required_path='pypy/',
)


proc = subprocess.Popen(['svnadmin', 'dump', '-q', svnrepo],
                        stdout=subprocess.PIPE)

def walk():
    total = None
    for entry in walk_entries(proc.stdout):
        if 'revno' in entry:
            total = int(entry.get('svn:sync-last-merged-rev', total))
            ui.progress('revision', pos=entry['revno'], total=total)
        yield entry


replay(branchreplay, walk() )

import json

with open(options.replay, 'w') as fp:
    json.dump(branchreplay.to_json(), fp, indent=2)
