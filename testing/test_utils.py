import py

from hackbeil.utils import window

def test_window():

    w = window(range(10), 6)
    for item in w:
        print item
    w = window(range(10), 8)
    assert w.next() == tuple(range(8))
    assert w.next() == tuple(range(1,9))
    assert w.next() == tuple(range(2, 10))
    py.test.raises(StopIteration, w.next)
