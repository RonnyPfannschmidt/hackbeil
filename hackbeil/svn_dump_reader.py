"""
utility functions to read svn dumps into structured data
"""

from io import BytesIO
import itertools
import hashlib

key_names = {
    'Revision-number': 'revno',
    'Node-path': 'path',
    'Node-kind': 'kind',
    'Node-action': 'action',
    'Node-copyfrom-path': 'copy_from',
    'Node-copyfrom-rev': 'copy_rev',
    'Prop-content-length': 'props_size',
    'Content-length': delattr,
    'Text-content-length': 'content_size',
    'Text-content-md5': delattr,
    'Text-content-sha1': 'content_sha1',
}

def headerkv(text):
    key, value = text.split(':', 1)
    value = value.strip()
    if value.isdigit():
        value = int(value)
    return key, value


def read_header(fd):
    result = {}
    for key, value in map(headerkv, iter(fd.readline, '\n')):
        key = key_names.get(key, key)
        if key is delattr:
            continue
        result[key] = value
    return result


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
        return []
    raw = fd.read(pl)
    return read_props_inner(BytesIO(raw))


def read_entry(fd):
    headers = read_header(fd)
    props = dict(read_props(fd, headers.get('props_size', 0)))
    data = fd.read(headers.get('content_size', 0))
    if 'content_sha1' in headers:
        content_hash = hashlib.sha1(data).hexdigest()
        assert content_hash == headers['content_sha1']
    headers.update(props)
    if data:
        headers['data'] = data
    return headers


def walk_entries(fd):
    while True:
        try:
            entry = read_entry(fd)
            #XXX: why are those empty ones there
            if entry:
                yield entry

        except ValueError:
            break

def iter_file(fd, cls, discard_header=True):
    if discard_header:
        read_header(fd) # dump version
        read_header(fd) # dump uuid

    revgrouped = itertools.groupby(
            walk_entries(fd),
            lambda entry: entry.get('revno'))
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



