#!/usr/bin/python
import re
import subprocess

listing = open('pypy-branches.txt')
latest = list(listing)[-1]

regex = r'\(from (?P<path>[\w\/\-\.]+):(?P<rev>\d+)\)'

match = re.search(regex, latest)
path, revno = match.groups()

template = "svn log file:///home/ronny/.local/var/pypy-clone/%s@%s -v --stop-on-copy"
command = template % (path, revno)
print command

subprocess.call(command, shell=True,
)

