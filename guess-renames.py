# guess-renames.py
# Copyright (c) 2009 Colin Barrett <colin@springsandstruts.com>
#
# This software may be used and distributed according to the terms
# of the GNU General Public License, incorporated herein by reference.

from __future__ import with_statement
import sys
import subprocess
import os.path

# Algorithm description is here:
# http://bundlebuggy.aaronbentley.com/project/bzr/request/%253C49C7A51C.4050000%2540aaronbentley.com%253E

# All edge hashes (each two consecutive lines) in the missing files
edge_hashes = {}

# Globals, necessary for now.
root = subprocess.Popen(['hg', 'root'], stdout=subprocess.PIPE).communicate()[0].rstrip('\n')
hg_st_lines = subprocess.Popen(['hg', 'st'], stdout=subprocess.PIPE).communicate()[0].splitlines()

# Edge hashses ---

def iter_edge_hashes(lines):
    # Limit the size of edge_hashes to 10M items.
    maximum = 1024 * 1024 * 10
    for n in range(len(lines)):
        yield hash(tuple(lines[n:n+2])) % maximum

# Missing files ---

def iter_missing_files():
    for line in hg_st_lines:
        if line[0] == '!':
            yield os.path.join(root, line[2:])

def missing_file_lines(missing_file):
    return subprocess.Popen(['hg', 'cat', missing_file], stdout=subprocess.PIPE).communicate()[0].splitlines(True)

# Unknown files ---

def iter_unknown_files():
    for line in hg_st_lines:
        if line[0] == '?':
            yield os.path.join(root, line[2:])
            
def unknown_file_lines(unknown_file):
    with open(unknown_file) as f:
        return f.readlines()
        
# Moving files ---

def record_old_is_new(old_file, new_file):
    subprocess.call(['hg', 'mv', '-A', old_file, new_file])

# Main implementation ---

for path in iter_missing_files():
    for edge_hash in iter_edge_hashes(missing_file_lines(path)):
        edge_hashes.setdefault(edge_hash, set()).add(path)

score_tuples = []
for path in iter_unknown_files():
    scores = {}
    # For each edge hash in this unknown file, find all missing files with
    # that edge. Bump the score for each missing file with this edge based
    # on rarity of the edge.
    for edge_hash in iter_edge_hashes(unknown_file_lines(path)):
        if edge_hashes.has_key(edge_hash):
            matched_files = edge_hashes[edge_hash]
            weight = 1.0 / len(matched_files)
            for matched_file in matched_files:
                scores.setdefault(matched_file, 0)
                scores[matched_file] += weight
            
    for matched_file, weight in scores.items():
        score_tuples.append((weight, matched_file, path))

old_to_new = {}
root_len = len(root) + 1
for weight, old_file, new_file in sorted(score_tuples, reverse=True):
    if old_file in old_to_new.keys() or new_file in old_to_new.values():
        continue
    old_to_new[old_file] = new_file
    record_old_is_new(old_file, new_file)
    print "%s is now %s (score: %f)" % (old_file[root_len:], new_file[root_len:], weight)
