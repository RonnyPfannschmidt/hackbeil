#!/usr/bin/python

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('replay')
parser.add_argument('svnroot')
parser.add_argument('basedir')
parser.add_argument('authormap')

options = parser.parse_args()

import subprocess
from hackbeil.scripting.convert import convert_all
from hackbeil.branchreplay import BranchReplay
from hackbeil.hgutils import progressui
import json


with open(options.replay) as fp:
    data = json.load(fp)


replay = BranchReplay.from_json(data)


def call_convert(**args):

    
    command = (
        'hg convert -q -s svn {source} {dest} '
        '--config convert.svn.startrev={start}{end} '
        '--authormap {authormap}'
    )
    subprocess.check_call(command.format(**args), shell=True)


def call_hgsubversion(**args):
    dest = args['dest']
    if path.exists(dest):
        command = 'hg pull -q -R {dest} {end}'
    else:
        command = 'hg clone -q -U {source} {dest} --startrev {start} {end}'

    subprocess.check_call(command.format(**args), shell=True)

ui = progressui()

convert_all(ui, replay, call_convert, options.svnroot, options.basedir, options.authormap)

ui.status('weeeeeeeeee\n')

