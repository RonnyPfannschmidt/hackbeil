import simplejson

class Branch(object):
    def __init__(self, path, startrev, source_branch=None, source_rev=None):
        self.path = path
        self.startrev = startrev
        self.endrev = None
        self.source_branch = source_branch
        self.source_rev = source_rev
        self.changesets = set()

    def active_in(self, rev):
        if rev >=self.startrev:
            return self.endrev is None or rev < self.endrev


    def matches(self, path, rev, subdir=False):
        if self.active_in(rev):
            if subdir:
                return path.startswith(self.path)
            else:
                return self.path == path

    def __str__(self):
        return self.path

    def __repr__(self):
        return '<Branch {path} {startrev}-{endrev!r} from {source_branch!s}@{source_rev}>'.format(**vars(self))

class BranchReplay(object):

    def __init__(self, initial, tag_prefixes=[], required_path=None):
        self.rev = -1
        self.branch_history = [initial]
        self.branches = {initial.path: initial}
        self.tag_prefixes = []
        self.required_path = required_path

    def findbranch(self, path, rev, subdir=False):
        branchlist = reversed(self.branch_history)

        for branch in branchlist:
            if branch.matches(path, rev, subdir):
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
        if (self.required_path and
            not kw['path'].startswith(self.required_path)):
            return
        method = getattr(self, 'on_' + action)
        method(**kw)


    def on_add(self, kind, path, **kw):
        source_branch = self.findbranch(
            path=kw.get('copy_from'),
            rev=kw.get('copy_rev'))
        if source_branch is None:
            branch = self.findbranch(path, self.rev, subdir=1)
            if branch:
                branch.changesets.add(self.rev)
            return
        branch = Branch(path, self.rev, source_branch,  kw.get('copy_rev'))
        self.branch_history.append(branch)
        #ignore tag locations for active branches
        for tag_prefix in self.tag_prefixes:
            if path.startswith(tag_prefix):
                return
        self.branches[path] = branch


    def on_change(self, path, **kw):
        branch = self.findbranch(path, self.rev, subdir=True)
        if branch is not None:
            #print repr(branch), path, kw.get('kind')
            branch.changesets.add(self.rev)

    def on_delete(self, path, **kw):
        branch = self.branches.pop(path, None)
        if branch is not None:
            branch.endrev = self.rev
        else:
            branch = self.findbranch(path, self.rev, subdir=True)
            if branch is not None:
                branch.changesets.add(self.rev)

    def on_replace(self, **kw):
        pass



def json_listing(filename, ui=None):

    with open(filename) as fp:
        for line in fp:
            data = simplejson.loads(line)
            revno = data.get('revno')
            if revno is not None and ui is not None:
                ui.progress('json reading', pos=revno)
            yield data


def replay(branchreplay, items):
    for data in items:
        if 'revno' in data:
            branchreplay.revdone(nextrev=data['revno'])
        else:
            branchreplay.event(**data)

