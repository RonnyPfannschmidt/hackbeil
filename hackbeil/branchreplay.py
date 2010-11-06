
class Branch(object):
    def __init__(self, path, startrev, source_branch=None, source_rev=None):
        self.path = path
        self.startrev = startrev
        self.endrev = None
        self.source_branch = source_branch
        self.source_rev = source_rev

    def matches(self, path, rev):
        return (path == self.path
                and rev >=self.startrev
                and (self.endrev is None or rev < self.endrev))

    def __str__(self):
        return self.path

    def __repr__(self):
        return '<Branch {path} {startrev}-{endrev!r} from {source_branch!s}@{source_rev}>'.format(**vars(self))

class BranchReplay(object):

    def __init__(self, initial):
        self.rev = -1
        self.branch_history = [initial]
        self.branches = {initial.path: initial}

    def findbranch(self, path, rev):
        for branch in self.branch_history:
            if branch.matches(path, rev):
                return branch

    def revdone(self, nextrev=None):
        previous = self.rev
        if nextrev is not None:
            assert nextrev > self.rev, 'uh i don\'t go backward bastard'
            self.rev = nextrev
        else:
            self.rev+=1
        return previous

    def event(self, action, **kw):
        method = getattr(self, 'on_' + action)
        method(**kw)


    def on_add(self, kind, path, **kw):
        if kind !='dir' or 'copy_from' not in kw:
            return
        if not path.startswith('pypy/'):
            return
        source_branch = self.findbranch(
            path=kw.get('copy_from'),
            rev=kw.get('copy_rev'))
        if source_branch is None:
            copy_from = kw.get('copy_from')
            if not copy_from.startswith('pypy/'):
                return
            if copy_from:
                if copy_from.endswith('/pypy'):
                    print self.rev, path, 'invavalid /pypy branch from', copy_from
                else:
                    print self.rev, path, 'wtf', kw
            else:
                print self.rev, path, kw
            return
        branch = Branch(path, self.rev, source_branch,  kw.get('copy_rev'))
        self.branch_history.append(branch)
        #XXX pypy magic
        if path.startswith('pypy/release/'):# and not path[-1] =='x':
            return
        if path.startswith('pypy/tag'):
            return
        self.branches[path] = branch
    def on_change(self, **kw):
        pass #XXX mark actual changes

    def on_delete(self, path, **kw):
        branch = self.branches.pop(path, None)
        if branch is not None:
            branch.endrev = self.rev
            if branch.endrev==self.rev-1:
                print 'shorty', branch


    def on_replace(self, **kw):
        pass
