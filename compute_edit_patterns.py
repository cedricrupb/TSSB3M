from mapreduce import mapreduce
import json

from collections import defaultdict
from tssb_miner.edit_abstraction import abstract_edit_script


def slc_to_pattern(slc):
    if not slc["likely_bug"]: return []
    if slc["comodified"]: return []

    edit_script = json.loads(slc['edit_script'])
    edit_pattern = tuple("%s_%s" % x for x in abstract_edit_script(edit_script))
    return [(edit_pattern, slc["sstub_pattern"])]

# Collect --------------------------------

class PatternCollector:

    def __init__(self):
        self._patterns = defaultdict(int)

    def __call__(self, pattern_sstub):
        pattern, sstub = pattern_sstub
        self._patterns[(pattern, sstub)] += 1



if __name__ == '__main__':
    collector = PatternCollector()
    mapreduce(slc_to_pattern, collector)
    
    with open("edit_patterns.jsonl", "w") as o:
        for (pattern, sstub), count in collector._patterns.items():
            o.write(json.dumps(
                {
                    "pattern": pattern,
                    "count"  : count,
                    "sstub" : sstub
                }
            ) + "\n")