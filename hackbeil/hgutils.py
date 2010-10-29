from mercurial.util import Abort
from mercurial import context
import contextlib

def progressui():
    from mercurial.ui import ui
    ui = ui()
    from hgext.progress import uisetup
    uisetup(ui)
    return ui

@contextlib.contextmanager
def abort_on_error(transaction):
    transaction.nest()
    try:
        yield
    except:
        transaction.abort()
        raise
    else:
        transaction.close()


def find_svn_rev(repo, wanted_branch, wanted_rev):
    ui = repo.ui

    lastctx = None
    for idx, rev in enumerate(repo):
        ui.progress('finding svn target', pos=idx)
        ctx = repo[rev]
        branch = ctx.branch()
        if branch != wanted_branch:
            continue
        extra = ctx.extra()
        convert_rev = extra.get('convert_revision')
        if convert_rev:
            if '@' in convert_rev:
                convert_rev = convert_rev.split('@')[-1] #from hg
            else:
                convert_rev = crev.split(':')[-1] # from bzr
            convert_rev = int(convert_rev)
            if convert_rev > wanted_rev:
                if lastctx is None:
                    # this happens when the first svn revision of the branch
                    # is higher than the source svn revision. The sanest thing
                    # to do is to just abort.
                    raise Abort('The first SVN revision of the branch is %d, which is higher than %d\n' % (convert_rev, rev))

                return lastctx.rev()
        lastctx = ctx
    else:
        ui.status('no fitting svn commit found\nusing latest instead\n')
        return ctx.rev()



def copying_fctxfn(stitch_root):

    def filectx(repo, ctx, path):
        if path not in stitch_root:
            error = IOError()
            #error.errno=errno.ENOENT
            #error.filename=path
            raise error

        other = stitch_root[path]
        copy = other.renamed() and other.renamed()[0]
        return context.memfilectx(
            path=path,
            data=other.data(),
            islink='l' in other.flags(),
            isexec='x' in other.flags(),
            copied = copy,
        )
    return filectx


def close_commit(repo, lookup, date=None):
    ui = repo.ui
    ctx = repo[lookup]

    if date is None:
        date = ctx.date()
    branch = ctx.branch()

    ui.status('closing branch %s\n' % branch)
    closectx = context.memctx(
        repo=repo,
        parents=[ctx.rev(), None],
        text='closed branch %s' % branch,
        user='sticher branch closer',
        date=date,
        files=[],
        extra={
            'branch': branch,
            'close': 1,
        },
        filectxfn = None,
    )

    repo.commitctx(closectx)
