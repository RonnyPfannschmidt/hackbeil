#!/usr/bin/python
import sys
import re
from svn_dump_reader import iter_file
from model import Revision, BranchTool


ignore_paths = [
    'vendor',
    'codespeak',
    'xpython',
    'trunk/www',
    'pypy/trunk/www/moininstance',
    'vpath',
    'rlcompleter2',
    'epoz',
    'kupu',
    'z3',
    'user',
    'rr',
    'basil'
]


class PyPyBranchTool(BranchTool):

    branch_matches = [
        '^(pypy/)?trunk',
        '^pypy/branch/(?P<branch>[^/]+)',
        '^pypy/(?P<branch>dist)'
    ]

    def figure_branch(self, revision):
        for matcher in self.branch_matches:
            for node in revision.nodes:
                match = re.match(matcher, node.path)
                if match is None:
                    break
                branch = match.groupdict().get('branch', '')
            else:
                return branch, matcher

        return None, None

    def adapt_paths(self, revision, regex):
        if not regex:
            return
        for node in revision.nodes:
            match = re.match(regex, node.path)
            node.path = node.path[match.end():]
            if node.copy_from:
                match = re.match(regex, node.copy_from)
                if match:
                    node.copy_from = node.copy_from[match.end():]


branchtool = PyPyBranchTool()


def path_filter(node):
    return any(node.path.startswith(x) for x in ignore_paths)



class InterestingRevision(Revision):
    filters = [path_filter]


dump = open(sys.argv[1], 'r')

for revision in iter_file(dump, InterestingRevision):
    if not revision.nodes:
        continue
    revision.transform_renames()
    revision.transform_branch(branchtool)
    if not any(node.copy_from for node in revision.nodes):
        continue
    
    print 'rev %s:'% revision.id
    print '  branch:', revision.branch or 'default'
    print '  author:', revision.author
    print '  log:', revision.message.split('\n')[0]
    print '  files:'
    for node in revision.nodes:
        print '    -', node.action, node.path, node.kind or ''
        if node.copy_from:
            print '        from', node.copy_from, node.copy_rev

