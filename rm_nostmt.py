"""
Should run after run_slc_process.py -> rm_parse_errors.py.

Removes all non single statement commits.

Produces: SSC-28M

"""

from mapreduce import mapreduce

def filter_nostmt(slc):
    if slc["sstub_pattern"] in ["NO_STMT", "MULTI_STMT"]: return []
    return [slc]

if __name__ == '__main__':
    mapreduce(filter_nostmt)