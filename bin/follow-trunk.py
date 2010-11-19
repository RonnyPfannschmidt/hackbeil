#!/usr/bin/python

import argparse

parser = argparse.ArgumentParser()
parser.add_argument('replay', argparse.FileType('r'))

from hackbeil.branchreplay import BranchReplay
