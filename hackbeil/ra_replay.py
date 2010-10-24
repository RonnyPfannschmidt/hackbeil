#!/usr/bin/python
# Demonstrates how to use the replay function to fetch the 
# changes made in a revision.
import sys
from subvertpy.ra import RemoteAccess, Auth, get_username_provider



class MyFileEditor:

    def change_prop(self, key, value):
        return
        if 'bzr' in key:
            return
        print "Change prop: %s -> %r" % (key, value)

    def apply_textdelta(self, base_checksum):
        # This should return a function that can receive delta windows
        def apply_window(x):
            pass
        return apply_window

    def close(self):
        pass

class MyDirEditor:

    def open_directory(self, path, base):
        return MyDirEditor()

    def add_directory(self, path, copyfrom_path=None, copyfrom_rev=-1):
        return MyDirEditor()

    def open_file(self, *args):
        return MyFileEditor()

    def add_file(self, path, copyfrom_path=None, copyfrom_rev=-1):
        return MyFileEditor()
        if copyfrom_path:
            print "Add file: %s (from %r:%r)" % (path, copyfrom_path, copyfrom_rev)

    def change_prop(self, key, value):
        return
        if 'bzr' in key:
            return
        print "Change prop %s -> %r" % (key, value)

    def delete_entry(self, path, revision):
        return
        print "Delete: %s" % path

    def close(self):
        pass


class MyEditor(object):

    def __init__(self, rev, props):
        self.rev = rev
        self.props = props

    def change_prop(self, key, value):
        return
    def set_target_revision(self, revnum):
        print "Target revision: %d" % revnum

    def abort(self):
        print "Aborted"

    def close(self):
        print "Closed"

    def open_root(self, base_revnum):
        #print "/", base_revnum
        return MyDirEditor()


conn = RemoteAccess("file:///home/ronny/.local/var/pypy-clone",
        auth=Auth([get_username_provider()]))
def op(rev, props):
    return MyEditor(rev, props)

def close(rev, props, editor):
    return editor


print conn

conn.replay_range(
    1, 71999, #start, end
    0, # watermark
    (op, close), #editor callbacks
    False) #send deltas
