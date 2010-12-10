#!/usr/bin/python

import subprocess
import py

config_file = py.path.local(__file__).dirpath().join('example.ini')
config = py.iniconfig.IniConfig(config_file)
config_dir = config_file.dirpath()

bin = config_dir.dirpath().join('bin')

svnrepo = config['workload']['repo']
replay = str(config_dir.join(config['workload']['replay']))
converts = str(config_dir.join(config['workload']['converts']))
target = str(config_dir.join(config['workload']['target']))
authormap = str(config_dir.join(config['workload']['authormap']))


def call(cmd, *args):
    cmd = str(bin/cmd)
    subprocess.check_call(['python', cmd] + list(args))



import sys
args = sys.argv[1:]

if 'sync' in args:
    subprocess.check_call(['svnsync', 'sync', svnrepo])
if 'replay' in args:
    call('svn-dump2replay-on-the-fly.py', replay, svnrepo)

if 'convert' in args:
    call('convert-via-replay.py', replay, svnrepo ,converts, authormap)
if 'combine' in args:
    if not py.path.local(target).check(dir=1):
        subprocess.check_call(['hg', 'init', target])
    call('replay-hg-history.py', replay, converts, target)
if 'push' in args:
    subprocess.check_call(['hg', '-R', target, 'push', '-f', 'bb:pypy-test'])
