from hackbeil.branchreplay import BranchReplay


def pytest_funcarg__replay(request):
    return BranchReplay()


def test_simple_replay(replay):
    assert not replay.branch_history
    assert not replay.branches

    replay.rev = 0

    replay.action(
        action='add',
        kind='dir',
        path='trunk',
    )
    assert 'trunk' in replay.branches

    replay.rev = 1
    replay.action(
        action='delete',
        path='trunk',
    )

    assert 'trunk' not in replay.branches
    assert replay.branch_history[0].endrev == 1
