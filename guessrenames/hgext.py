# guess-renames
# Copyright (c) 2009 Colin Barrett <colin@springsandstruts.com>
#
# This software may be used and distributed according to the terms
# of the GNU General Public License, incorporated herein by reference.

from hg import *
from mercurial import extensions, commands, cmdutil

def addremove(orig, repo, pats=[], opts={}, dry_run=None, similarity=None):
    shouldguess = False
    if opts['guess']:
        shouldguess = True
        
    if similarity:
        # Clear to cancel the behavior of the wrapped function
        similarity = 0
        shouldguess = True
        
    if shouldguess:
        gr = MercurialGuessRenames(repo.ui, repo)
        gr.guess()
        gr.move()
    
    return orig(repo, pats, opts, dry_run, similarity)


def uisetup(ui):
    ar = list(commands.table['addremove'])
    opts = ar[1]
    # XXX need to modify 's' to indicate it's deprecated and invokes -g instead.
    opts.append(('g', 'guess', False, 'guess renamed files'))
    commands.table['addremove'] = tuple(ar)
    
    import_ = list(commands.table['import|patch'])
    opts = import_[1]
    # XXX need to modify 's' to indicate it's deprecated and invokes -g instead.
    opts.append(('g', 'guess', False, 'guess renamed files'))
    commands.table['import'] = tuple(import_)
            
    extensions.wrapfunction(cmdutil, 'addremove', addremove)
