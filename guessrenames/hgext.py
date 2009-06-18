# guess-renames
# Copyright (c) 2009 Colin Barrett <colin@springsandstruts.com>
#
# This software may be used and distributed according to the terms
# of the GNU General Public License, incorporated herein by reference.

from hg import *
from mercurial import extensions, commands, cmdutil
import re

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
        if not dry_run:
            gr.move()
    
    return orig(repo, pats, opts, dry_run, similarity)


def uisetup(ui):
    def replace_similarity(opts):
        newopts = []
        for idx, opt in enumerate(opts):
            if opt[0] == 's':
                newopt = list(opt)
                newopt[3] = 'backwards compatability; implies -g/--guess'
                opt = tuple(newopt)
            newopts.append(opt)
        return newopts
    
    ar = list(commands.table['addremove'])
    docre = re.compile('Use the -s option.+way can be expensive\.', re.M | re.S)
    ar[0].__doc__ = re.sub(docre,
    """
    Use the -g option to detect renamed files. This option uses a smarter, more
    accurate algorithm than the built-in -s option.
    """.strip(), ar[0].__doc__)
    ar[1] = replace_similarity(ar[1])
    ar[1].append(('g', 'guess', False, 'guess renamed files'))
    commands.table['addremove'] = tuple(ar)
    
    import_ = list(commands.table['import|patch'])
    import_[0].__doc__ = re.sub(r'(--similarity),',
                                r'\1 or -g/--guess,',
                                import_[0].__doc__)
    import_[1] = opts = replace_similarity(import_[1])
    import_[1].append(('g', 'guess', False, 'guess renamed files'))
    commands.table['import'] = tuple(import_)
            
    extensions.wrapfunction(cmdutil, 'addremove', addremove)
