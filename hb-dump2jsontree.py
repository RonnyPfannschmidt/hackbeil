#!/usr/bin/python

import argparse
import json

from os.path import join

parser = argparse.ArgumentParser()

parser.add_argument('dump')
parser.add_argument('output')
parser.add_argument('file_tree')

from hackbeil.svn_dump_reader import read_header, walk_entries

options = parser.parse_args()

dump = open(options.dump)
output = open(options.output, 'w')

read_header(dump) # skip uuid
read_header(dump) # skip extra metadatoa

for entry in walk_entries(dump):
    data = entry.pop('data', None)
    if data is not None:
        with open(join(options.file_tree, entry['content_sha1']), 'w') as fp:
            fp.write(data)
    print >> output, json.dumps(entry)





