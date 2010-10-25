#!/usr/bin/python

import argparse
parser = argparse.ArgumentParser()

parser.add_argument('config')
parser.add_argument('dump')

from hackbeil.cli import read_dump
from hackbeil.svn_dump_reader import walk_entries

options = parser.parse_args()

walk_iter = walk_entries(
    open(options.dump),
    discard_header=True)

read_dump(options.config, walk_iter)



