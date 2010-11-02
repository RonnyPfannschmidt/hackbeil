#!/usr/bin/python
import sys
import simplejson as json


seen = set()

with open(sys.argv[1]) as fp:
    for line in fp:
        data = json.loads(line)
        author = data.get('svn:author')
        if author and author not in seen:
            print author
            seen.add(author)
