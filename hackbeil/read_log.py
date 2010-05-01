#!/usr/bin/python
import sys
import re
import itertools
import functools
from svn_dump_reader import iter_file
from model import Revision, BranchTool


ignore_paths = [
    'vendor',
    'codespeak',
    'xpython',
    'trunk/www',
    'pypy/trunk/www/',
    'vpath',
    'rlcompleter2',
    'epoz',
    'kupu',
    'z3',
    'user',
    'rr',
    'basil',
    'std',
    'py/',
    'lxml',
]



