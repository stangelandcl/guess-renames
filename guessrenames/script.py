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

def _svnrepofound(p):
    return SubversionGuessRenames(p)

def _findhgrepo(p):
    while not os.path.isdir(os.path.join(p, ".hg")):
        oldp, p = p, os.path.dirname(p)
        if p == oldp:
            return None
    else:
        return p
        
def _hgrepofound(p):
    ui = ui_.ui()
    repo = hg.repository(ui, p)
    return MercurialGuessRenames(ui, repo)

# ---

def main():
    gr = None
    cwd = os.getcwd()
    
    order = [(_findsvnrepo, _svnrepofound),
             (_findhgrepo, _hgrepofound)]
 
    for search, found in order:
        repopath = search(cwd)
        if repopath:
            gr = found(repopath)
            break
    else:
        print "error: no Subversion or Mercurial repository found"
        sys.exit(1)

    gr.guess()
    gr.move()
    
if __name__ == '__main__':
    main()
