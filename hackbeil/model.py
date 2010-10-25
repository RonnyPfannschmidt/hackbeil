'''
some convience classes for storing the data from a replay/dump
'''
import re


class BranchTool(object):
    branch_matches = [
        #XXX: defaults?
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

    def is_branchop(self, revision):
        """ use after adapt_paths"""
        if not revision.nodes:
            return

        indicator = revision.nodes[0]
        return not indicator.path and bool(indicator.copy_from)

    def changes_only(self, revision):
        return all(node.kind == 'change' for node in revision.nodes)


class Node(object):
    def __init__(self, node):
        self.kind = node.get('kind')
        self.path = node['path']
        self.action = node['action']
        self.copy_from = node.get('copy_from')
        self.copy_rev = node.get('copy_rev')
        self.data = node


class Revision(object):
    filters = []
    def __init__(self, entry, nodes=()):
        self.entry = entry
        self.branch = ''
        self.nodes = [
            n for n in map(Node, nodes)
            if not any(
                f(n)
                for f in self.filters
            )
        ]

    def transform_branch(self, branchtool):
        self.branch, branch_regex = branchtool.figure_branch(self)
        if branch_regex:
            branchtool.adapt_paths(self, branch_regex)

    def transform_renames(self):
        #XXX: tricky hack
        deletes = [node for node in self.nodes if node.action=='delete']
        for delete in deletes:
            for node in self.nodes[:]:
                if node.copy_from == delete.path:
                    node.action = 'rename'
                    node.deletes = [delete]
                    try:
                        self.nodes.remove(delete)
                    except:
                        pass # renamed to 2 different names


    def __repr__(self):
        return '<Rev %s, nodes=%s>' % (self.id, len(self.nodes))

    @property
    def id(self):
        return int(self.entry['revno'])

    @property
    def message(self):
        return self.entry.get('svn:log') or '\n'

    @property
    def author(self):
        return self.entry.get('svn:author') or '\n'




