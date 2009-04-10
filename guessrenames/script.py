# guess-renames
# Copyright (c) 2009 Colin Barrett <colin@springsandstruts.com>
#
# This software may be used and distributed according to the terms
# of the GNU General Public License, incorporated herein by reference.

from hg import *
from svn import *

import subprocess
import os
import sys
from mercurial import hg, ui as ui_

def _findsvnrepo(p):
    if os.path.isdir(os.path.join(p, '.svn')):
        return p
    else:
        return None

def _findhgrepo(p):
    while not os.path.isdir(os.path.join(p, ".hg")):
        oldp, p = p, os.path.dirname(p)
        if p == oldp:
            return None
    else:
        return p

def main():
    gr = None
    cwd = os.getcwd()
    
    if not gr:
        repopath = _findsvnrepo(cwd)
        if repopath:
            gr = SubversionGuessRenames()
    
    if not gr:
        repopath = _findhgrepo(cwd)
        if repopath:
            ui = ui_.ui()
            repo = hg.repository(ui, repopath)
            gr = MercurialGuessRenames(ui, repo)
 
    if not gr:
        print "error: no Subversion or Mercurial repository found"
        sys.exit(1)

    gr.guess()
    gr.move()
    
if __name__ == '__main__':
    main()
