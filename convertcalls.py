#!/usr/bin/python
import re
import subprocess

listing = open('pypy-branches.txt')
listing.next() #skip the comment

calls = []

endrev = None
for item in listing:
    parts = item.split()
    path = parts[0]
    startrev = parts[-1][1:]
    # print path, startrev, '!', endrev
    calls.append((path, startrev, endrev))
    endrev = startrev

template = (
    'hg convert -s svn{ends} '
    'file:///home/ronny/.local/var/pypy-clone{path} '
    '--config convert.svn.startrev={start} '
    '/home/ronny/pypy-stitches/{stitch:02d}'
)


for stitch, (path, start, end) in enumerate(calls):
    if end:
        end = int(end)-1
    command = template.format(
        stitch=stitch,
        path=path,
        start=start,
        ends=' -r %s' % end if end else '')
    print command


