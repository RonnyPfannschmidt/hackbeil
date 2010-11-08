from hackbeil.branchreplay import BranchReplay, Branch, replay


def pytest_funcarg__replay(request):
    return BranchReplay(initial=Branch('trunk', 1))


def test_simple_replay(replay):
    assert len(replay.branch_history) == 1

    replay.event(
        action='add',
        kind='dir',
        path='trunk',
    )

    replay.revdone(nextrev=10)
    previous = 9

    trunk = replay.findbranch(path='trunk', rev=previous)

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
    assert trunk.end == replay.rev

    replay.revdone(nextrev=200)
    assert not replay.findbranch('trunk', replay.rev)


    replay.event(
        action='delete',
        path='branch/test',
    )
    replay.event(
        action='add',
        kind='dir',
        path='trunk',
        copy_from='branch/test',
        copy_rev=150,
    )

    replay.revdone()
    assert replay.findbranch('trunk', replay.rev)

    assert len(replay.branch_history) == 3


def test_replay_pop_missing_branch(replay):

    replay.event(
        action='delete',
        path='foo')





def test_branch_to_json():

    b = Branch('trunk', 10)
    data = b.to_json()
    assert data == {
        'path': 'trunk',
        'start': 10,
        'end': None,
        'changesets': [],
        'source_branch': None,
        'source_rev': None,
    }

    b2 = Branch.from_json(data)
    assert b.path == b2.path
    assert b.start == b2.start
    assert b.changesets == b2.changesets



def test_branch_replay_json():

    rp = BranchReplay(initial=Branch('trunk', 1))
    data = rp.to_json()
    assert data == {
        'history': [rp.branch_history[0].to_json()],
        'required_path': None,
        'rev': -1,
        'tag_prefixes': [],
    }


    rp2 = BranchReplay.from_json(data)
    assert rp2.findbranch('trunk', 1)
    assert rp2.rev == rp.rev
    assert rp2.required_path == rp.required_path

