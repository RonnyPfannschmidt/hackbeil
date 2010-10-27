import iniconfig
import functools
import itertools

try:
    import cPickle as pickle
except ImportError:
    import pickle

from .model import Revision, BranchTool

filter_nonodes = functools.partial(itertools.ifilter, lambda x: x.nodes)

def filter_range(revisions, start=0, end=999999999999999):
    assert start < end
    revisions = itertools.dropwhile(lambda x: x.id < start, revisions)
    return itertools.takewhile(lambda x: x.id <= end, revisions)

def iter_entries(walk_iter, cls):

    revgrouped = itertools.groupby(
            walk_iter,
            lambda entry: entry.get('revno'))
    rev = None
    for key, group in revgrouped:
        group = list(group)
        if key is not None:
            if rev is not None:
                yield cls(rev, [])
            rev = group[0]
        else:
            yield cls(rev, group)
            rev = None
    if rev is not None:
        yield cls(rev, [])

def read_dump(configfile, walk_iter):
    config = iniconfig.IniConfig(configfile)

    start = config.get('range', 'start', convert=int)
    end = config.get('range', 'end', convert=int)

    branchtool = BranchTool()
    BranchTool.branch_matches = config.get('branches', 'match',
                                        convert=str.splitlines)

    include = config.get('paths', 'include', convert=str.splitlines)
    exclude = config.get('paths', 'exclude',
                         convert=str.split,
                         default=[],
                        )

    class InterestingRevision(Revision):
        filters = [
            lambda node: not any(node.path.startswith(x)
                                 for x in include),
            lambda node: any(node.path.startswith(x)
                             for x in exclude),
            ]


    revisions = iter_entries(walk_iter, InterestingRevision)
    revisions = filter_nonodes(revisions)
    revisions = filter_range(revisions, start, end)
    return revisions, branchtool

def print_rev(revision, branchtool):
    revision.transform_renames()
    revision.transform_branch(branchtool)
    if not any(node.copy_from for node in revision.nodes):
        return
    if not branchtool.is_branchop(revision):
        return
    print '- rev: %s'% revision.id
    print '  branch:', revision.base
    print '  branchop:', branchtool.is_branchop(revision)
    print '  author:', revision.author
    print '  log:', revision.message.split('\n')[0]
    print '  files:'
    for node in revision.nodes:
        print '    -', node.action, node.path, node.kind or ''
        if node.copy_from:
            print '        from', node.copy_from, node.copy_rev
    print


def check_entry(config, entry):
    if 'path' not in entry:
        return True

    path = entry['path']
    #XXX: copy_from !
    if any(path.startswith(x) for x in config.get('exclude')):
        return False
    if not any(path.startswith(x) for x in config.get('include')):
        return True


def convert_dump_to_pickle(configfile, dump, picklefile):

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

