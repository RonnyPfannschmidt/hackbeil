from os import path

def targetdirname(branch):
    return '{base}@{start}'.format(
        base=branch.path.split('/')[-1],
        start=branch.start,
    )

def do_convert(converter, branch, repo, basedir):
    targetdir = targetdirname(branch)

    call_args = {
        'source': repo + branch.path,
        'start': branch.start,
        'end': (' -r %s' % (branch.end-1)) if branch.end is not None else '',
        'dest': path.join(basedir, targetdir),
    }

    converter(**call_args)


def convert_all(ui, replay, convert_call, repo, basedir):
    for idx, branch in enumerate(replay.branch_history):
        name = targetdirname(branch)
        ui.progress('converting repos',
                    pos=idx,
                    total=len(replay.branch_history),
                    item=name,
                   )
        do_convert(convert_call, branch, repo, basedir)

