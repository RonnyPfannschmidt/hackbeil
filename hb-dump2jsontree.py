#!/usr/bin/python

import argparse
import json
from os.path import join, exists

parser = argparse.ArgumentParser()

parser.add_argument(
    'dump', type=argparse.FileType('r'),
)
parser.add_argument(
    'output', type=argparse.FileType('w'),
)
parser.add_argument('file_tree', default=None, nargs='?')

from hackbeil.svn_dump_reader import read_header, walk_entries
from hackbeil.hgutils import progressui
options = parser.parse_args()

ui = progressui()


total = None

for entry in walk_entries(options.dump):
    if 'revno' in entry:
        if entry['revno'] == 0:
            total = int(entry['svn:sync-last-merged-rev']) #HACK
        ui.progress('rev', pos=entry['revno'], total=total)
    data = entry.pop('data', None)
    if data is not None and options.file_tree is not None:
        path = join(options.file_tree, entry['content_sha1'])
        if not exists(path):
            with open(path ,'w') as fp:
                fp.write(data)
    options.output.write(json.dumps(entry) + '\n')
    options.output.flush()





