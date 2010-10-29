from hackbeil.branchreplay import BranchReplay


def pytest_funcarg__replay(request):
    return BranchReplay()


def test_simple_replay(replay):
    assert not replay.branch_history
    assert not replay.branches

    replay.event(
        action='add',
        kind='dir',
        path='trunk',
    )
    assert 'trunk' in replay.branches

    previous = replay.revdone()


    replay.event(
        action='add',
        kind='dir',
        path='branch/test',
        copy_from='trunk',
        copy_rev=previous,
    )



    replay.revdone(nextrev=100)
    replay.event(
        action='delete',
        path='trunk',
    )

    assert 'trunk' not in replay.branches
    assert replay.branch_history[0].endrev == 100

    previous = replay.revdone()

    replay.event(
        action='delete',
        path='branch/test',
    )
    replay.event(
        action='add',
        kind='dir',
        path='trunk',
        copy_from='branch/test',
        copy_rev=previous,
    )
    replay.revdone()
