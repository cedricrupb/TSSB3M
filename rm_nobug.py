
"""
Should run after run_slc_process.py -> rm_parse_errors.py -> rm_nostmt.py.

Removes all (likely) non buggy commits.

Produces: SSB-9M

"""

from mapreduce import mapreduce

def filter_nobug(slc):
    if not slc["likely_bug"]: return []
    return [slc]

if __name__ == '__main__':
    mapreduce(filter_nobug)