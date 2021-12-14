"""
Should run after run_slc_process.py -> rm_nostmt.py -> rm_nobug.py.

Removes all commits that modifiy more than one file.

Produces: TSSB-3M

"""


from mapreduce import mapreduce

def filter_comod(slc):
    if slc["comodified"]: return []
    return [slc]

if __name__ == '__main__':
    mapreduce(filter_comod)