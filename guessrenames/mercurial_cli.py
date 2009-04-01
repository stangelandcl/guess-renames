# guess-renames
# Copyright (c) 2009 Colin Barrett <colin@springsandstruts.com>
#
# This software may be used and distributed according to the terms
# of the GNU General Public License, incorporated herein by reference.

from __future__ import with_statement
import subprocess
import os.path

import abstract

__all__ = ["MercurialCLIGuessRenames"]

class MercurialCLIGuessRenames(abstract.AbstractGuessRenames):

    def __init__(self):
        super(MercurialCLIGuessRenames, self).__init__()
        self._root = subprocess.Popen(['hg', 'root'], stdout=subprocess.PIPE).communicate()[0].rstrip('\n')
        self._hg_st_lines = subprocess.Popen(['hg', 'st'], stdout=subprocess.PIPE).communicate()[0].splitlines()
            
    def iter_missing_files(self):
        for line in self._hg_st_lines:
            if line[0] == '!':
                yield os.path.join(self._root, line[2:])
    
    def missing_file_lines(self, missing_file):
        return subprocess.Popen(['hg', 'cat', missing_file], stdout=subprocess.PIPE).communicate()[0].splitlines(True)
        
    def iter_unknown_files(self):
        for line in self._hg_st_lines:
            if line[0] == '?':
                yield os.path.join(self._root, line[2:])
                
    def unknown_file_lines(self, unknown_file):
        with open(unknown_file) as f:
            return f.readlines()

    def record_old_is_new(self, old_file, new_file):
        subprocess.call(['hg', 'mv', '-A', old_file, new_file])
        #print 'hg mv -A %s %s' % (old_file, new_file)
    
    def strip_root(self, path):
        return path[len(self._root)+1:]
