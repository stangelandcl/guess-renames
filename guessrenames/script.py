# guess-renames
# Copyright (c) 2009 Colin Barrett <colin@springsandstruts.com>
#
# This software may be used and distributed according to the terms
# of the GNU General Public License, incorporated herein by reference.

import guessrenames
import subprocess
import os
from mercurial import hg, ui as ui_

def _findrepo(p):
    while not os.path.isdir(os.path.join(p, ".hg")):
        oldp, p = p, os.path.dirname(p)
        if p == oldp:
            return None

    return p

def main():
    repopath = _findrepo(os.getcwd())
    if not repopath:
        print "error: no Mercurial repository found"
        sys.exit(1)

    ui = ui_.ui()
    repo = hg.repository(ui, repopath)
    gr = guessrenames.MercurialGuessRenames(ui, repo)
    gr.guess()
    gr.move()
    
if __name__ == '__main__':
    main()