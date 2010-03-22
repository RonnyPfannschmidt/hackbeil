"""
utility functions to read svn dumps into structured data
"""

from io import BytesIO
import itertools

def headerkv(text):
    key, value = text.split(':', 1)
    value = value.strip()
    if value.isdigit():
        value = int(value)
    return key, value


def read_header(fd):
    return dict(map(headerkv, iter(fd.readline, '\n')))


def read_props_inner(fd):
    while True:
        line = fd.readline().strip()
        if line == 'PROPS-END':
            return
        kind, len = line.split(' ')
        assert kind == 'K'
        key = fd.read(int(len))
        fd.read(1) # padding newline

        kind, len = fd.readline().strip().split()
        assert kind == 'V'
        value = fd.read(int(len))
        fd.read(1) # padding newline
        yield key, value


def read_props(fd, pl):
    if not pl:
        return
    raw = fd.read(pl)
    return read_props_inner(BytesIO(raw))


def read_entry(fd):
    headers = read_header(fd)
    cl = headers.get('Content-length', 0)
    pl = headers.get('Prop-content-length', 0)
    props = dict(read_props(fd, pl) or [])
    data = fd.read(cl-pl)
    headers.update({
        'props': props,
        'data': data,
        })
    return headers


def walk_entries(fd):
    while True:
        try:
            yield read_entry(fd)
        except ValueError:
            return

class Revision(object):
    filters = [
            lambda x: x=={'data': '', 'props': {}},
            ]
    def __init__(self, entry, nodes=()):
        self.entry = entry
        self.nodes = [
            n for n in nodes
            if not any(
                f(n)
                for f in self.filters
            )
        ]

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

    @classmethod
    def from_fd(cls, fd):

        nodes = []

        for entry in iter(lambda: read_entry(fd), None):
            if 'Revision-number' in entry:
                break
            else:
                nodes.append(entry)


        return cls(entry, nodes)

    @classmethod
    def iter_file(cls, fd, discard_header=True):
        if discard_header:
            read_header(fd) # dump version
            read_header(fd) # dump uuid

        revgrouped = itertools.groupby(
                walk_entries(fd),
                lambda entry: entry.get('Revision-number'))
        rev = None
        for key, group in revgrouped:
            group = list(group)
            if key is not None:
                if rev is not None:
                    yield cls(rev, [])
                rev = group[0]
            else:
                yield cls(rev, group)
                rev = None
        if rev is not None:
            yield cls(rev, [])


