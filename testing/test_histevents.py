from hackbeil.branchreplay import BranchReplay
from hackbeil.histevents import EventReplay, events_from_replay

def simple_replay():
    return BranchReplay.from_json({
        'rev': 20,
        'required_path': None,
        'history': [
            {
                'path': 'trunk',
                'start': 1,
                'end': None,
                'changesets': [],
                'source_branch': None,
                'source_rev': None
            }
        ]
    })



def test_event_from_replay():
    replay = simple_replay()

    events = list(events_from_replay(replay))
    assert len(events) ==1

def test_simple_event_replay():
    branch_replay = simple_replay()
    event_replay = EventReplay(branch_replay)
    event_replay._add_replay()
    print event_replay._events
    chunks = event_replay.generate_chunklist()


    assert event_replay.findchunk('trunk', 10)
    


def test_branch_splits_chunk():
    branch_replay = BranchReplay.from_json({
        'rev': 20,
        'required_path': None,
        'history': [
            {
                'path': 'trunk',
                'start': 1,
                'end': 20,
                'changesets': [],
                'source_branch': None,
                'source_rev': None
            },
            {
                'path': 'branch/test',
                'start': 10,
                'end':  21,
                'changesets': [],
                'source_branch': 'trunk',
                'source_rev': 9,
            },
            {
                'path': 'trunk',
                'start': 20,
                'end': None,
                'changesets': [],
                'source_branch': 'branch/test',
                'source_rev': 20,
            },
        ]
    })


    event_replay = EventReplay(branch_replay)
    event_replay._add_replay()
    print event_replay._events
    chunks = event_replay.generate_chunklist()
    print chunks
    assert len(chunks) == 5

