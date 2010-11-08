#!/usr/bin/python

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('replay')
parser.add_argument('svnroot')
parser.add_argument('basedir')

options = parser.parse_args()

import subprocess

from hackbeil.branchreplay import BranchReplay
import json
from os import path


with open(options.replay) as fp:
    data = json.load(fp)


replay = BranchReplay.from_json(data)


def targetdirname(branch):
    return '{base}@{start}'.format(
        base=branch.path.split('/')[-1],
        start=branch.start,
    )


def call_convert(**args):

    
    command = (
        'hg convert -s svn {source} {dest} '
        '--config convert.svn.startrev={start}{end}'
    )
    subprocess.call(command.format(**args), shell=True)


def call_hgsubversion(**args):
    dest = args['dest']
    if path.exists(dest):
        command = 'hg pull -q -R {dest} {end}'
    else:
        command = 'hg clone -q -U {source} {dest} --startrev {start} {end}'

    subprocess.call(command.format(**args), shell=True)


def convert(branch, repo, basedir):
    targetdir = targetdirname(branch)
    
    
    call_args = {
        'source': repo + branch.path,
        'start': branch.start,
        'end': (' -r %s' % (branch.end-1)) if branch.end is not None else '',
        'dest': path.join(basedir, targetdir),
    }

    call_convert(**call_args)


for branch in replay.branch_history:
    print 'converting', repr(branch)
    convert(branch, options.svnroot, options.basedir)

print 'echo weeeeeeeeee'

