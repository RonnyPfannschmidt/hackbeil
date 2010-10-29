#!/usr/lib/python
import re
import os
import argparse
parser = argparse.ArgumentParser()
parser.add_argument('listing', type=argparse.FileType('r'))
parser.add_argument('svn')
parser.add_argument('base')
parser.add_argument('--idx', default=None, type=int)

options = parser.parse_args()


from subprocess import call

chunks = []

with options.listing as fp:
    lastrev = None
    for line in fp:
        if line[0] == '#':
            continue
        parts = line.split()
        subdir = parts[0]
        rev = int(parts[-1].strip('r'))
        chunks.append((subdir, rev, lastrev))
        lastrev =rev


def convert_one(subdir, rev, lastrev):
    target = os.path.join(options.base, 'trunk-%05d' % rev)
    print target, subdir, rev, lastrev
    params = [
        'hg', 'convert',
        '-s', 'svn',
        options.svn + subdir, # + ('' if lastrev is None else '@%s' % (lastrev-1,)),
        target,
        '--config', ' convert.svn.startrev=%s' % (rev,),
    ]
    if lastrev is not None:
        params.extend(['-r', str(lastrev-1)])
    ret = call(params)
    if ret:
        print params
        raise SystemExit

if options.idx is not None:
    convert_one(*chunks[options.idx])
else:
    for chunk in chunks:
        convert_one(*chunk)
