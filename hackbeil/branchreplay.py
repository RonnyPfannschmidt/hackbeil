

class Branch(object):
    def __init__(self, path, startrev):
        self.path = path
        self.startrev = startrev
        self.endrev = None

    def __repr__(self):
        return '<Branch {path} {startrev}-{endrev!r}>'.format(**vars(self))

class BranchReplay(object):

    def __init__(self):
        self.rev = 0
        self.branch_history = []
        self.branches = {}


    def action(self, action, **kw):
        if action == 'add':
            self.add(**kw)
        elif action == 'delete':
            self.remove(**kw)


    def add(self, kind, path, **kw):
        if kind !='dir':
            return
        branch = Branch(path, self.rev)
        self.branch_history.append(branch)
        self.branches[path] = branch

    def remove(self, path, **kw):
        branch = self.branches.pop(path)
        branch.endrev = self.rev
