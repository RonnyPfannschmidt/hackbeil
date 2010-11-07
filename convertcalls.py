#!/usr/bin/python
import re
import subprocess

listing = open('converts.txt')

calls = []

for item in listing:
    parts = item.split()

    name = parts[0]
    path = parts[0]
    startrev = parts[-1][1:]
    # print path, startrev, '!', endrev
    calls.append((path, startrev, endrev))
    endrev = startrev



def make_call(name, path, startrev, endrev=None, source_branch=None):
    if endrev:
        ending = ['-r',

    name = 
    'hg convert -s svn{ends} '
    'file:///home/ronny/.local/var/pypy-clone{path} '
    '--config convert.svn.startrev={start} '
    '/home/ronny/pypy-stitches/'
)


for stitch, (path, start, end) in enumerate(reversed(calls)):
    if end:
        end = int(end)-1
    command = template.format(
        stitch=stitch,
        path=path,
        start=start,
        ends=' -r %s' % end if end else '')
    print command, '&&'

print 'echo weeeeeeeeee'

