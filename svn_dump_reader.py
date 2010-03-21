"""
utility functions to read svn dumps into structured data
"""

from io import BytesIO

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


