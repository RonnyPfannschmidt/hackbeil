from hackbeil.branchreplay import BranchReplay, Branch, replay


def pytest_funcarg__replay(request):
    return BranchReplay(initial=Branch('trunk', 1))


def test_simple_replay(replay):
    assert len(replay.branch_history) == 1
    assert 'trunk' in replay.branches
    

    replay.event(
        action='add',
        kind='dir',
        path='trunk',
    )
    assert 'trunk' in replay.branches

    replay.revdone(nextrev=10)
    previous = 9
    print replay.branches
    assert replay.findbranch(path='trunk', rev=previous)
    replay.event(
        action='add',
        kind='dir',
        path='branch/test',
        copy_from='trunk',
        copy_rev=previous,
    )

    print replay.branches

    replay.revdone(nextrev=100)
    replay.event(
        action='delete',
        path='trunk',
    )

    assert 'trunk' not in replay.branches
    assert replay.branch_history[0].endrev == 100

    replay.revdone(nextrev=200)

    replay.event(
        action='delete',
        path='branch/test',
    )
    print replay.branches
    replay.event(
        action='add',
        kind='dir',
        path='trunk',
        copy_from='branch/test',
        copy_rev=150,
    )
    replay.revdone()
    assert len(replay.branches) == 1

    assert len(replay.branch_history) == 3


def test_replay_pop_missing_branch(replay):

    replay.event(
        action='delete',
        path='foo')

