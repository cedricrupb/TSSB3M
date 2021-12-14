"""
Can be run anytime after run_slc_process.py

Computes the precentage of bugs that reflect a typo (Damerau Levenshtein distance <= 2)
"""

from mapreduce import mapreduce
from fastDamerauLevenshtein import damerauLevenshtein
import json

from code_diff.diff_utils import parse_hunks

def get_match_line(hunk):
    assert len(hunk.added_lines) == 1
    assert len(hunk.rm_lines) == 1

    add_line = next(iter(hunk.added_lines))
    rm_line  = next(iter(hunk.rm_lines))

    add_line = hunk.lines[add_line]
    rm_line  = hunk.lines[rm_line]

    add_line = " " + add_line[1:]
    rm_line = " " + rm_line[1:]

    return rm_line, add_line


def text_dist(slc):

    diff = slc["diff"]
    hunks = parse_hunks(diff)

    cum_dist = 0
    for hunk in hunks:
        try:
            before_line, after_line = get_match_line(hunk)
            cum_dist += damerauLevenshtein(before_line, after_line, similarity = False)
        except AssertionError:
            return [1e9]

    return [cum_dist]


def update_dist(slc):
    edit_script = json.loads(slc["edit_script"])
    if len(edit_script) != 1: return []
    if edit_script[0][0] != "Update": return []
    if "string" not in edit_script[0][1][0]: return []

    before = edit_script[0][1][0].replace("string:", "")
    after  = edit_script[0][2]

    if len(before) < 3: return [1e9]

    return [damerauLevenshtein(before, after, similarity = False)]


class TypoCount():

    def __init__(self):
        self.count = 0
        self.total = 0

    def __call__(self, edit_distance):
        if edit_distance <= 2:
            self.count += 1
        self.total += 1
    
    def count_info(self):
        return "%d / %d (%f)" % (self.count, self.total, self.count / self.total)

if __name__ == '__main__':
    typo_count = TypoCount()
    mapreduce(text_dist, typo_count) # Replace text_dist by update_dist to compute typo distribution for specific updates
    print("Total number of typos: %s" % typo_count.count_info())