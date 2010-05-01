#!/usr/bin/python

import sys

if len(sys.argv)!=3:
    print 'Usage:', sys.argv[0], '$config $dump'
    exit(1)


from hackbeil.cli import read_dump
read_dump(sys.argv[1], sys.argv[2])

