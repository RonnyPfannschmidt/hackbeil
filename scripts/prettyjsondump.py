#!/usr/bin/python
import sys
import simplejson as json

input = open(sys.argv[1])


for line in input:
    data = json.loads(line)
    if data.get('revno'):
        data['svn:author'] = data.get('svn:author') # turn missing to None
        print 'r%(revno)s %(svn:author)s %(svn:log)s' % data
    elif 'action' in data:
        if data.get('kind') == 'dir':
            data['path']+='/'

        if 'copy_from' in data:
            data['source'] = 'from %(copy_from)s@%(copy_rev)s' % data
        else:
            data['source'] = ''
        print '    %(action)s %(path)s %(source)s' % data
