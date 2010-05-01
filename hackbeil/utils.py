from itertools import islice
from collections import deque

def window(s, width):
    s = iter(s) # else a grue  eats us on normal sequences
    q = deque(islice(s, width), maxlen=width)
    yield tuple(q)
    for item in s:
        q.append(item)
        yield tuple(q)
