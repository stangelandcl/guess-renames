# guess-renames
# Copyright (c) 2009 Colin Barrett <colin@springsandstruts.com>
#
# This software may be used and distributed according to the terms
# of the GNU General Public License, incorporated herein by reference.

from hg import *
from mercurial import extensions, commands

def addremove(orig, ui, repo, *args, **opts):
    shouldguess = False
    if opts['guess']:
        shouldguess = True
        
    if opts['similarity'] is not '':
        # Clear to cancel the behavior of the wrapped command
        opts['similarity'] = ''
        shouldguess = True
        
    if shouldguess:
        gr = MercurialGuessRenames(ui, repo)
        gr.guess()
        gr.move()
    
    return orig(ui, repo, *args, **opts)


def uisetup(ui):
    # XXX open question: import also uses the -s option.
    # determine how to make import use guessrenames too.
    ar = list(commands.table['addremove'])
    opts = ar[1]
    # XXX need to modify 's' to indicate it's deprecated and invokes -g instead.
    opts.append(('g', 'guess', False, 'guess at file renames'))
    commands.table['addremove'] = tuple(ar)
            
    extensions.wrapcommand(commands.table, 'addremove', addremove)
    