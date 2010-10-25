#!/usr/bin/python

import simplejson
import argparse
parser = argparse.ArgumentParser()

parser.add_argument('config')
parser.add_argument('dump')

from hackbeil.cli import read_dump

options = parser.parse_args()

dump = open(options.dump)

walk_iter = (simplejson.loads(x) for x in dump)

revisions = read_dump(options.config, walk_iter)
