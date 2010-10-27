#!/usr/bin/python

import posixpath

import simplejson
import argparse
parser = argparse.ArgumentParser()

parser.add_argument('config')
parser.add_argument('dump')

from hackbeil.cli import iter_entries, Revision, BranchTool


def removes_branch(node):
    base, name = posixpath.split(node.path)
    if base == 'pypy/branch' and node.action == 'delete':
        print node.path
        return True

class InterestingRevision(Revision):
    filters = [ lambda node: not removes_branch(node)]


options = parser.parse_args()

dump = open(options.dump)

walk_iter = (simplejson.loads(x) for x in dump)

def print_rev(revision, branchtool):
    if not revision.nodes: 
        return
    revision.transform_branch(branchtool)
    from hackbeil.cli import print_rev
    #revision.transform_renames()
    if hasattr(revision, 'source'):
        print revision.id, \
                revision.base, \
                'from %s@%s' % ( revision.source.encode('utf-8'), revision.source_rev), \
                revision.branchop
    print_rev(rev, branchtool)


branchtool = BranchTool()

revisions = iter_entries(walk_iter, InterestingRevision)
for rev in revisions:
    print_rev(rev, branchtool)

