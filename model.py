'''
some convience classes for storing the data from a replay/dump
'''



class BranchTool(object):
    branch_matches = [
    ]

class Node(object):
    def __init__(self, node):
        self.kind = node.get('Node-kind')
        self.path = node['Node-path']
        self.action = node['Node-action']
        self.copy_from = node.get('Node-copyfrom-path')
        self.copy_rev = node.get('Node-copyfrom-rev')
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
        return int(self.entry['Revision-number'])

    @property
    def message(self):
        return self.entry['props'].get('svn:log') or '\n'

    @property
    def author(self):
        return self.entry['props'].get('svn:author') or '\n'


