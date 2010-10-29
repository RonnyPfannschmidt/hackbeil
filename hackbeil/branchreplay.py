

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


    def revdone(self, nextrev=None):
        previous = self.rev
        if nextrev is not None:
            assert nextrev > self.rev, 'uh i don\'t go backward bastard'
            self.rev = nextrev
        else:
            self.rev+=1
        return previous

    def event(self, action, **kw):
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
