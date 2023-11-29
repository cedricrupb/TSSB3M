"""
Deduplicates all entries.

Note: It is necessary to run this script with --no_parrallel. Otherwise, the behavior is undefined.
"""

from collections import defaultdict

from mapreduce import mapreduce


# Deduplication ----------------------------------------------------------------

class DeduplicationIndex:

    def __init__(self):
        self._index = set()

    def __contains__(self, slc):
        commit_sha = slc["commit_sha"]
        content_hash = hash(slc["diff"])
        return (commit_sha, content_hash) in self._index

    def add(self, slc):
        commit_sha = slc["commit_sha"]
        content_hash = hash(slc["diff"])
        self._index.add((commit_sha, content_hash))

    def info(self):
        return f"""
Num commits: {len(self._index)}
        """

def group_by_project_commit(slc):
    return (slc["project"], slc["commit_sha"])


if __name__ == '__main__':
    deduplication_index = DeduplicationIndex()

    def filter_duplicates(slc):
        if slc not in deduplication_index:
            deduplication_index.add(slc)
            return [slc]
        return []

    mapreduce(filter_duplicates)
    print(deduplication_index.info())