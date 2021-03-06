import heapq
from hackbeil.scripting.convert import targetdirname

def events_from_replay(replay):
    for branch in replay.branch_history:
        yield branch.start, 'branch', branch
        if branch.end is not None:
            yield branch.end, 'close', branch




class Chunk(object):

    def changesets(self):
        def cset_filter(id):
            return id >= self.start and (self.end is None or id < self.end)
        return set(filter(cset_filter, self.branch.changesets))

    def __init__(self, start, branch, parent=None):
        self.given_name = None
        self.branch = branch
        self.start = start
        self.end = None
        self.children = []
        self.parent = parent
        if parent:
            parent.children.append(self)

    def guessed_name(self):
        if self.given_name is not None:
            return self.given_name
        else:
            if self.end is None:
                return self.branch.path.split('/')[-1]
            else:
                return targetdirname(self.branch)

    def __repr__(self):
        return '<{branch.path}@{start}-{end}>'.format(**vars(self))

class EventReplay(object):
    def __init__(self):
        self.chunks = []
        self.executed = False
        self._events = []


    def findchunk(self, path ,rev):
        for chunk in self.chunks:
            if (path == chunk.branch.path
                and chunk.start <= rev
                and (chunk.end is None or rev < chunk.end)):
                    return chunk

    def add_replay(self, replay):
        for item in events_from_replay(replay):
            heapq.heappush(self._events, item)

    def add_mergelist(self):
        pass

    def generate_chunklist(self):
        while self._events:
            curr = heapq.heappop(self._events)
            rev, action = curr[:2]
            call = getattr(self, 'on_' + action)
            call(rev, *curr[2:])
        return self.chunks

    def on_branch(self, rev, newbranch):
        if newbranch.source_branch:
            oldchunk = self.findchunk(newbranch.source_branch,
                                      newbranch.source_rev)

            old_end = oldchunk.end
            oldchunk.end = rev
            newchunk = Chunk(start=rev,
                             branch=oldchunk.branch,
                             parent=oldchunk)
            newchunk.end = old_end
            self.chunks.append(newchunk)

                #self.chunks.insert(
                #   self.chunks.index(oldchunk)+1,
                #   newchunk)
        else:
            oldchunk = None
        chunk = Chunk(start=rev,
                      branch=newbranch,
                      parent=oldchunk)
        self.chunks.append(chunk)

    def on_close(self, rev, branch):
        chunk = self.findchunk(branch.path, rev)
        chunk.end = rev

