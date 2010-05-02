import yaml
import functools
import itertools

try:
    import cPickle as pickle
except ImportError:
    import pickle

from .model import Revision, BranchTool
from .svn_dump_reader import iter_file, walk_entries

filter_nonodes = functools.partial(itertools.ifilter, lambda x: x.nodes)

def filter_range(revisions, start=0, end=999999999999999):
    assert start < end
    revisions = itertools.dropwhile(lambda x: x.id < start, revisions)
    return itertools.takewhile(lambda x: x.id <= end, revisions)

def read_dump(configfile, dump):
    with open(configfile) as fp:
        config = yaml.load(fp)
    

    start = config['revrange']['start']
    end = config['revrange']['end']

    dump = open(dump, 'r')
    
    branchtool = BranchTool()
    BranchTool.branch_matches = config['branchmatch']



    class InterestingRevision(Revision):
        filters = [
            lambda node: not any(node.path.startswith(x)
                                 for x in config['include']),
            lambda node: any(node.path.startswith(x)
                             for x in config.get('exclude', [])),
            ]


    revisions = iter_file(dump, InterestingRevision)
    revisions = filter_nonodes(revisions)
    revisions = filter_range(revisions, start, end)
    for revision in revisions:
        print_rev(revision, branchtool)

def print_rev(revision, branchtool):
    revision.transform_renames()
    revision.transform_branch(branchtool)
    if not any(node.copy_from for node in revision.nodes):
        return
    print 'rev %s'% revision.id
    print '  branch', revision.branch or 'default'
    print '  branchop', branchtool.is_branchop(revision)
    print '  author', revision.author
    print '  log', revision.message.split('\n')[0]
    print '  files'
    for node in revision.nodes:
        print '    -', node.action, node.path, node.kind or ''
        if node.copy_from:
            print '        from', node.copy_from, node.copy_rev


def check_entry(config, entry):
    if 'path' not in entry:
        return True

    path = entry['path']

    if any(path.startswith(x) for x in config.get('exclude')):
        return False
    if not any(path.startswith(x) for x in config.get('include')):
        return True





def convert_dump_to_pickle(configfile, dump, picklefile):
    with open(configfile) as fp:
        config = yaml.load(fp)
    
    dump = open(dump, 'r')
    picklefile = open(picklefile, 'w')
    try:
        for entry in walk_entries(dump):
            if check_entry(config, entry):
                pickle.dump(entry, picklefile, protocol=2)
            if 'revno' in entry:
                print 'at revision', entry['revno']
    finally:
        picklefile.close()
        dump.close()

