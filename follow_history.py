import sys
from collections import defaultdict
import simplejson

class SvnDir(object):
    def __init__(self, path, startrev, fromdir=None):
        self.path = path
        self.startrev = startrev
        self.endrev = None
        self.fromdir = fromdir
        self.children = []
        if fromdir:
            assert fromdir.endrev is not None
            assert self.startrev >= fromdir.endrev
            fromdir.children.append(self)

    def __repr__(self):
        s = '%s@%s:%s' % (self.path, self.startrev, self.endrev or '')
        if self.fromdir:
            s += ' (from %s@%s)' % (self.fromdir.path, self.fromdir.endrev-1)
        return s

    def is_alive_at(self, rev):
        return self.startrev <= rev and (self.endrev is None or
                                         rev < self.endrev)

    def info(self):
        return self.path, self.startrev, self.endrev

    def split(self, rev, newpath, newstartrev):
        assert self.is_alive_at(rev)
        current_endrev = self.endrev
        self.endrev = rev
        left = SvnDir(self.path, rev, fromdir=self)
        right = SvnDir(newpath, newstartrev, fromdir=self)
        left.endrev = current_endrev
        return left, right

    def dot_node(self):
        name = self.path.replace('/', '_')
        name = name.replace('-', '_')
        name = name.replace('.', '_')
        name = name.replace('+', '_')
        return '%s__%s' % (name, self.startrev)

    def gendot(self, out):
        label = '%s[%s:%s]' % (self.path, self.startrev, self.endrev or '')
        color = ''
        if getattr(self, 'color', None):
            color = 'fillcolor="%s"' % self.color
        out.write('%s[label="%s",%s];\n' % (self.dot_node(), label, color))
        for child in self.children:
            out.write('%s -> %s;\n' % (self.dot_node(), child.dot_node()))
        for child in self.children:
            child.gendot(out)

class Repository(object):

    def __init__(self):
        self.fs = {}
        self.rev = 0

    def find(self, path, rev):
        for svndir in self.fs.get(path, []):
            if svndir.is_alive_at(rev):
                return svndir
        return None

    def add(self, path, copy_from=None, copy_rev=None):
        assert self.find(path, self.rev) is None, 'cannot add %s, it already exists' % path
        if copy_from:
            print 'r%s    A  %s (from %s@%s)' % (self.rev, path, copy_from, copy_rev)
            fromdir = self.find(copy_from, copy_rev)
            left, right = fromdir.split(copy_rev, path, self.rev)
            self._append_dir(left.path, left)
            self._append_dir(right.path, right)
        else:
            print 'r%s    A  %s' % (self.rev, path)
            self._append_dir(path, SvnDir(path, self.rev))

    def _append_dir(self, path, svndir):
        self.fs.setdefault(path, []).append(svndir)

    def delete(self, path):
        if path not in self.fs:
            return
        svndir = self.find(path, self.rev)
        #assert svndir is not None, 'cannot delete %s, it does not exist' % path
        if svndir:
            svndir.endrev = self.rev

    def gendot(self, out, rootpath, rootrev):
        root = self.find(rootpath, rootrev)
        out.write('digraph repo {\n')
        root.gendot(out)
        out.write('}\n')
        

    # ------------------------------------------------------------------------------
    # PyPy specific optimization

    FIRST_TRUNK = ('pypy/trunk/src', 320)
    def is_proper_branch(self, frompath, fromrev):
        fromdir = self.find(frompath, fromrev)
        if not fromdir:
            return False
        if (fromdir.path, fromdir.startrev) == self.FIRST_TRUNK:
            return True
        return self.is_proper_branch(fromdir.fromdir.path, fromdir.fromdir.startrev)
        

def follow_history(history, repo=None):
    if repo:
        skip_until = repo.rev
    else:
        repo = Repository()
        skip_until = -1
    #
    for data in history:
        if data.get('revno') is not None:
            repo.rev = data['revno']
        if repo.rev <= skip_until or repo.rev == 56480: # workaround for a bug
            continue
        #
        action = data.get('action')
        kind = data.get('kind')
        path = data.get('path')
        copy_from = data.get('copy_from')
        copy_rev = data.get('copy_rev')
        #
        if action == 'add' and copy_from is None:
            if (path, repo.rev) == repo.FIRST_TRUNK:
                repo.add(path)
        elif action == 'add' and copy_from is not None:
            if repo.is_proper_branch(copy_from, copy_rev):
                repo.add(path, copy_from, copy_rev)
        elif action == 'delete':
            repo.delete(path)
    #
    return repo

def main():
    def gen_history():
        f = open('dumps/pypy-json-filtered')
        for line in f:
            yield simplejson.loads(line)
    repo = Repository()
    trunkpath, trunkrev = repo.FIRST_TRUNK
    repo.rev = trunkrev
    repo.add(trunkpath)
    repo = follow_history(gen_history(), repo)
    #
    print 'applying color to trunk'
    trunk = repo.find('pypy/trunk', repo.rev)
    while trunk is not None:
        trunk.color = '#CCFFFF'
        trunk = trunk.fromdir
    #
    print 'creating dot file...'
    dot = open('repo.dot', 'w')
    repo.gendot(dot, *repo.FIRST_TRUNK)
    dot.close()


if __name__ == '__main__':
    main()

