#!/usr/bin/python

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('svnbase')
parser.add_argument('listing', type=argparse.FileType('r'))

options = parser.parse_args()

import subvertpy.ra

entries = [x.split() for x in options.listing]




for branch, range in entries:

    conn = subvertpy.ra.RemoteAccess(options.svnbase + branch)

    start, end = range.split('-')
    start = int(start)
    end = int(end)-1 if end != 'None' else -1
    try:
        items = len(list(conn.iter_log(start=start,
                             end=end,
                             paths=None,
                             discover_changed_paths=True,
                            )))
    except:
        items = 'error'
    
    if items == 'error' or items>1:
        print branch, range, items



print 'all:', len(entries)
