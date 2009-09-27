# guess-renames
# Copyright (c) 2009 Colin Barrett <colin@springsandstruts.com>
#
# This software may be used and distributed according to the terms
# of the GNU General Public License, incorporated herein by reference.

from __future__ import with_statement
import subprocess
import os.path
from mercurial import cmdutil
import hashlib

import abstract

__all__ = ["MercurialGuessRenames"]

class MercurialGuessRenames(abstract.AbstractGuessRenames):

    def __init__(self, ui, repo):
        super(MercurialGuessRenames, self).__init__()
        self._ui = ui
        self._repo = repo
        status = self._repo.status(unknown=True)[3:5]
        status = [[self._repo.wjoin(path) for path in group] for group in status]
        self._missing, self._unknown = status

    def iter_missing_files(self):
        for i in xrange(len(self._missing)):
            yield self._missing[i]
    
    def missing_file_lines(self, missing_file):
        missing_file = self.strip_root(missing_file)
        ctx = self._repo['.']
        data = ctx[missing_file].data()
        if '\0' in data[:1024]:
            return [str(len(data)), hashlib.md5(data).hexdigest()]
        else:
            return data.splitlines(True)
        
    def iter_unknown_files(self):
        for i in xrange(len(self._unknown)):
            yield self._unknown[i]
    
    def unknown_file_lines(self, unknown_file):
        # diff(1) heuristic for binary files
        def isbinary(filename):        
            with open(filename, 'rb') as f:
                bytes = f.read(1024)
                return '\0' in bytes
        
        # returns (size, hash) as a list
        def binaryfilelines(filename):
            md5 = hashlib.md5()
            with open(filename, 'rb') as f:
                size = 1048576
                chunk = f.read(1048576)
                while chunk:
                    size += len(chunk)
                    md5.update(chunk)
                    chunk = f.read(1048576)
                return [str(size), md5.hexdigest()]

        # XXX do something more intelligent
        if os.path.isdir(unknown_file) or os.path.islink(unknown_file):
            #print "ignoring dir or link: %s" % unknown_file
            return []
            
        if isbinary(unknown_file):
            #print "NUL in %s" % unknown_file
            return binaryfilelines(unknown_file)
        else:
            with open(unknown_file) as f:
                return f.readlines()

    def record_old_is_new(self, old_file, new_file):
        #print 'hg mv -A %s %s' % (old_file, new_file)
        wlock = self._repo.wlock(False)
        try:
            return cmdutil.copy(self._ui, self._repo, (old_file, new_file), {'after': True}, rename=True)
        finally:
            wlock.release()
    
    def strip_root(self, path):
        return path[len(self._repo.root)+1:]
