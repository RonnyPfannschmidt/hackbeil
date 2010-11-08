#!/usr/bin/python
import argparse
import simplejson

parser = argparse.ArgumentParser()
parser.add_argument('dump')
parser.add_argument('replay_store')

opts = parser.parse_args()

from hackbeil.branchreplay import BranchReplay, Branch, replay, json_listing
from hackbeil.hgutils import progressui

ui = progressui()

br = BranchReplay(initial=Branch('pypy/trunk/src', 320))
replay(br, json_listing(opts.dump, ui))

ui.status('writing replay dump\n')
with open(opts.replay_store, 'w') as fp:
    simplejson.dump(br.to_json(), fp, indent=2)


