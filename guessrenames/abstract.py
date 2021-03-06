# guess-renames
# Copyright (c) 2009 Colin Barrett <colin@springsandstruts.com>
#
# This software may be used and distributed according to the terms
# of the GNU General Public License, incorporated herein by reference.

# Algorithm description is here:
# http://osdir.com/ml/bazaar/2009-03/msg01300.html

__all__ = ["AbstractGuessRenames"]

class AbstractGuessRenames(object):

    # Public ---

    def __init__(self):
        super(AbstractGuessRenames, self).__init__()
        self._edge_hashes = {}
        self._old_to_new = {}

    @property
    def guesses(self):
        return self._old_to_new
    
    def guess(self):
        # All edge hashes (each two consecutive lines) in the missing files
        for path in self.iter_missing_files():
            for edge_hash in self._iter_edge_hashes(self.missing_file_lines(path)):
                self._edge_hashes.setdefault(edge_hash, set()).add(path)
                
        # For each edge hash in this unknown file, find all missing files with
        # that edge. Bump the score for each missing file with this edge based
        # on the rarity of the edge.
        score_tuples = []
        for path in self.iter_unknown_files():
            scores = {}
            for edge_hash in self._iter_edge_hashes(self.unknown_file_lines(path)):
                if self._edge_hashes.has_key(edge_hash):
                    matched_files = self._edge_hashes[edge_hash]
                    weight = 1.0 / len(matched_files)
                    for matched_file in matched_files:
                        scores.setdefault(matched_file, 0)
                        scores[matched_file] += weight
                    
            for matched_file, weight in scores.items():
                score_tuples.append((weight, matched_file, path))
            
        for weight, old_file, new_file in sorted(score_tuples, reverse=True):
            if old_file in self._old_to_new.keys() or new_file in self._old_to_new.values():
                continue
            self._old_to_new[old_file] = new_file
            print "%s is now %s (score: %f)" % (self.strip_root(old_file), self.strip_root(new_file), weight)

    def move(self):
        for old_file, new_file in self.guesses.items():
            self.record_old_is_new(old_file, new_file)

    # Private ---

    @staticmethod # XXX is there any point to this?
    def _iter_edge_hashes(lines):
        # Limit the size of edge_hashes to 10M items.
        maximum = 1024 * 1024 * 10
        for n in xrange(len(lines)):
            yield hash(tuple(lines[n:n+2])) % maximum
    
    # Abstract ---
        
    def iter_missing_files(self):
        while False:
            yield None
    
    def missing_file_lines(self, missing_file):
        raise NotImplementedError
        
    def iter_unknown_files(self):
        while False:
            yield None
    
    def unknown_file_lines(self, unknown_file):
        raise NotImplementedError
    
    def record_old_is_new(self, old_file, new_file):
        raise NotImplementedError
        
    def strip_root(self, path):
        raise NotImplementedError
