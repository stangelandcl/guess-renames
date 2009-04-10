# guess-renames
# Copyright (c) 2009 Colin Barrett <colin@springsandstruts.com>
#
# This software may be used and distributed according to the terms
# of the GNU General Public License, incorporated herein by reference.

from __future__ import with_statement
import abstract
import subprocess
import os

__all__ = ["SubversionGuessRenames"]

# Currently this just drives the svn client. Investigate using pysvn or the new
# Subversion ctypes Python bindings.
class SubversionGuessRenames(abstract.AbstractGuessRenames):

    def __init__(self):
        super(SubversionGuessRenames, self).__init__()
        self._svn_st_lines = subprocess.Popen(['svn', 'st'], stderr=subprocess.STDOUT, stdout=subprocess.PIPE).communicate()[0].splitlines()
        self._root = os.getcwd()
        self._missing_files = self._gen_for_type('!')
        self._unknown_files = self._gen_for_type('?')
        
    def _gen_for_type(self, typechar):
        for line in self._svn_st_lines:
            if len(line) > 0 and line[0] is typechar:
                yield os.path.join(self._root, line[1:].lstrip())
        
    def iter_missing_files(self):
        return self._missing_files
    
    def missing_file_lines(self, missing_file):
        return subprocess.Popen(['svn', 'cat', missing_file], stdout=subprocess.PIPE).communicate()[0].splitlines(True)
        
    def iter_unknown_files(self):
        return self._unknown_files
    
    def unknown_file_lines(self, unknown_file):
        with open(unknown_file) as f:
            return f.readlines()
    
    def record_old_is_new(self, old_file, new_file):
        # Because svn is a control freak, we need to move the new file back to
        # where the old file was, so svn can do the full move operation. Dumb.
        os.rename(new_file, old_file)
        subprocess.check_call(['svn', 'mv', '--force', old_file, new_file], stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
        
    def strip_root(self, path):
        return path[len(self._root)+1:]
