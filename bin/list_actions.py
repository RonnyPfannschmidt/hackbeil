#!/usr/bin/python
from hackbeil.branchreplay import BranchReplay
from hackbeil.histevents import EventReplay

import sys
import json

with open(sys.argv[1]) as fp:
    data = json.load(fp)

br = BranchReplay.from_json(data)

er = EventReplay(br)
er._add_replay()

for chunk in er.generate_chunklist():
    print chunk

#for action, chunk in er.generate_actions():
#    print action, chunk
