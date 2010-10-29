#!/usr/bin/python

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('rev', type=int)
parser.add_argument('branch', default='default')
options = parser.parse_args()

from mercurial.localrepo import localrepository
from hackbeil.hgutils import progressui, find_svn_rev


ui = progressui()

repo = localrepository(ui, '.')

rev = find_svn_rev(
    repo = repo,
    wanted_branch = options.branch,
    wanted_rev = options.rev,
)

ctx = repo[rev]

ui.status('found %s:%s with %s\n' % (ctx.rev(),
                                     ctx.hex(),
                                     ctx.extra().get('convert_revision')))
