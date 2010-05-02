#!/usr/bin/python

import sys
if len(sys.argv) != 4:
    print 'usage:', sys.argv[0], '$config $dump $outfile'
    exit(1)


from hackbeil.cli import convert_dump_to_pickle
convert_dump_to_pickle(*sys.argv[1:])
