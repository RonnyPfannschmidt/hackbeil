#!/usr/bin/python
from hackbeil.branchreplay import BranchReplay
from hackbeil.histevents import EventReplay

import sys
import json

with open(sys.argv[1]) as fp:
    data = json.load(fp)

br = BranchReplay.from_json(data)

er = EventReplay()
er.add_replay(br)

for chunk in er.generate_chunklist():
    print chunk

