import heapq

def events_from_replay(replay):
    for branch in replay.branch_history:
        yield branch.start, 'branch', branch
        if branch.end is not None:
            yield branch.end, 'close', branch




class Chunk(object):

    def __init__(self, start, branch, parent=None):
        self.given_name = None
        self.branch = branch
        self.start = start
        self.end = None
        self.children = []
        self.parent = parent
        if parent:
            parent.children.append(self)

    def __repr__(self):
        return '<{branch.path}@{start}-{end}>'.format(**vars(self))

class EventReplay(object):
    def __init__(self, branchreplay = None, merges=None):
        self.branchreplay = branchreplay
        self.chunks = []
        self.executed = False
        self._events = []


    def findchunk(self, path ,rev):
        for chunk in self.chunks:
            if path == chunk.branch.path:
                if chunk.end is None or rev < chunk.end:
                    return chunk

    def _add_replay(self):
        for item in events_from_replay(self.branchreplay):
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

            if oldchunk.end is not None:
                oldchunk.end = rev
                newchunk = Chunk(start=rev,
                                 branch=oldchunk.branch,
                                 parent=oldchunk)
                self.chunks.append(newchunk)
            else:
                oldchunk = None
        else:
            oldchunk = None
        chunk = Chunk(start=rev,
                      branch=newbranch,
                      parent=oldchunk)
        self.chunks.append(chunk)

    def on_close(self, rev, branch):
        chunk = self.findchunk(branch.path, rev)
        chunk.end = rev



    def generate_actions(self):
        chunks = self.generate_chunklist()
        for chunk in chunks:
            branch = chunk.branch
            # dont yield actions for replays without change
            yield 'replay', chunk
            if branch.end is not None and chunk.end == branch.end:
                yield 'close', chunk
