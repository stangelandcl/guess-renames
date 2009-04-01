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

def iter_edge_hashes(lines):
    # Limit the size of edge_hashes to 10M items.
    maximum = 1024 * 1024 * 10
    for n in range(len(lines)):
        yield hash(tuple(lines[n:n+2])) % 10

root = subprocess.Popen(['hg', 'root'], stdout=subprocess.PIPE).communicate()[0].rstrip('\n')

hg_st_lines = subprocess.Popen(['hg', 'st'], stdout=subprocess.PIPE).communicate()[0].splitlines()

unknown_files = set()
for line in hg_st_lines:
    if line[0] == '!':
        item = os.path.join(root, line[2:])
        lines = subprocess.Popen(['hg', 'cat', item], stdout=subprocess.PIPE).communicate()[0].splitlines(True)
        for edge_hash in iter_edge_hashes(lines):
            edge_hashes.setdefault(edge_hash, set()).add(item)
    elif line[0] == '?':
        item = os.path.join(root, line[2:])
        unknown_files.add(item)

score_tuples = []
for item in unknown_files:
    lines = []
    scores = {}
    with open(item) as f:
        lines = f.readlines()
    
    # For each edge hash in this unknown file, find all missing files with
    # that edge. Bump the score for each missing file with this edge based
    # on rarity of the edge.
    for edge_hash in iter_edge_hashes(lines):
        if edge_hashes.has_key(edge_hash):
            matched_files = edge_hashes[edge_hash]
            weight = 1.0 / len(matched_files)
            for matched_file in matched_files:
                scores.setdefault(matched_file, 0)
                scores[matched_file] += weight
            
    for matched_file, weight in scores.items():
        score_tuples.append((weight, matched_file, item))

old_to_new = {}
root_len = len(root) + 1
for weight, old_file, new_file in sorted(score_tuples, reverse=True):
    if old_file in old_to_new.keys() or new_file in old_to_new.values():
        continue
    old_to_new[old_file] = new_file
    print "%s is now %s (score: %f)" % (old_file[root_len:], new_file[root_len:], weight)
    subprocess.call(['hg', 'mv', '-A', old_file, new_file])

