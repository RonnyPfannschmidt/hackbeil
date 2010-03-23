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


include_paths = [
    'pypy',
    'trunk',
]


class PyPyBranchTool(BranchTool):

    branch_matches = [
        '^(pypy/)?trunk',
        '^pypy/branch/(?P<branch>[^/]+)',
        '^pypy/(?P<branch>dist)'
    ]



branchtool = PyPyBranchTool()


def path_filter(node):
    return any(node.path.startswith(x) for x in ignore_paths)

def path_filter2(node):
    return not any(node.path.startswith(x) for x in include_paths)


class InterestingRevision(Revision):
    filters = [path_filter, path_filter2]


def print_rev(revision):
    revision.transform_renames()
    revision.transform_branch(branchtool)

    print 'rev %s:'% revision.id
    print '  branch:', revision.branch or 'default'
    print '  author:', revision.author
    print '  log:', revision.message.split('\n')[0]
    print '  files:'
    for node in revision.nodes:
        print '    -', node.action, node.path, node.kind or ''
        if node.copy_from:
            print '        from', node.copy_from, node.copy_rev

filter_nonodes = functools.partial(itertools.ifilter, lambda x: x.nodes)

def filter_range(revisions, start=0, end=999999999999999):
    assert start < end
    revisions = itertools.dropwhile(lambda x: x.id < start, revisions)
    return itertools.takewhile(lambda x: x.id <= end, revisions)

def main(start, end):
    dump = open(sys.argv[1], 'r')
    revisions = iter_file(dump, InterestingRevision)
    revisions = filter_nonodes(revisions)
    revisions = filter_range(revisions, start, end)
    for revision in revisions:
        print_rev(revision)

if __name__ == '__main__':
    main(0, 400)
