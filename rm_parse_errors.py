"""
Should run after run_slc_process.py.

Removes all hunks that contain a parse error.
"""

from mapreduce import mapreduce

def remove_error(slc):
    if "ERROR" in slc["edit_script"]: return []

    return [slc]

if __name__ == '__main__':
    mapreduce(remove_error)