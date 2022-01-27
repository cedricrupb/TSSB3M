"""
Can be run anytime after run_slc_process.py

Computes central statistics of the dataset such as SStuB or AST Edit distribution.
"""

from mapreduce import mapreduce

import json
from collections import defaultdict

from tssb_miner.edit_abstraction import abstract_edit_script


def label_instance(slc):
    labels = ["ALL"]

    if slc["likely_bug"]:
        labels.append("BUGGY")
    
    if not slc["comodified"]:
        labels.append("NOCOMODIFIED")

    if slc["sstub_pattern"] not in ["SINGLE_TOKEN", "SINGLE_STMT", "NO_STMT", "MULTI_STMT", "CHANGE_STRING_LITERAL"]:
        labels.append("SSTUB")

    edit_script = json.loads(slc["edit_script"])
    if len(edit_script) == 1:
        labels.append("SINGLE_EDIT")

    return [(slc, labels)]

# Counter --------------------------------------------------------------------------------------------------------------------------------

class GeneralCounter:

    def __init__(self):
        self.projects = defaultdict(set)
        self.project_urls = set()
        self.total = 0
    
    def __call__(self, slc):
        project_url, project, commit = slc["project_url"], slc["project"], slc["commit_sha"]

        self.projects[project].add(commit)
        self.project_urls.add(project_url)
        self.total += 1

    def report(self):
        print("Num project urls:\t%d" % len(self.project_urls))
        print("Num projects:    \t%d" % len(self.projects))
        print("Num commits:     \t%d" % sum(len(v) for v in self.projects.values()))
        print("Num changes:     \t%d" % self.total)


class SStubCounter:

    def __init__(self):
        self.total = 0
        self.sstub_types = defaultdict(int)

    def __call__(self, slc):
        sstub_type = slc["sstub_pattern"]
        self.sstub_types[sstub_type] += 1
        self.total += 1

    def report(self):
        sstub_types = sorted(self.sstub_types.keys(), key=lambda k: self.sstub_types[k], reverse = True)

        for sstub_type in sstub_types:
            count      = self.sstub_types[sstub_type]
            sstub_type = sstub_type + " "*(30 - len(sstub_type))
            print("%s\t| %d\t| %.4f" % (sstub_type, count, count / self.total))
        
        print("-----------------------------------------------------")
        total = "TOTAL" + " "*(30-len("TOTAL"))
        print("%s\t| %d\t| %.4f" % (total, self.total, 1.0))


class EditCounter:

    def __init__(self):
        self.edit_types = defaultdict(lambda: defaultdict(int))
        self.edit_categories = defaultdict(int)

    def __call__(self, slc):
        edit_script = json.loads(slc["edit_script"])

        abstract_ops = set(abstract_edit_script(edit_script))
        abstract_categories = set(k for k, _ in abstract_ops)

        for op_type, op_ctx in abstract_ops:
            self.edit_types[op_type][op_ctx] += 1

        for op_type in abstract_categories:
            self.edit_categories[op_type] += 1


    def report(self):
        total = sum(x for per_op_type in self.edit_types.values() for x in per_op_type.values())

        for op_type, sub_count in self.edit_types.items():
            sub_total = sum(x for x in sub_count.values())
            op_type_str = op_type + " "*(50 - len(op_type))
            print()
            print("%s\t| %d\t|%d\t| %f" % (op_type_str, self.edit_categories[op_type], sub_total, sub_total / total))
            print("-----------------------------------------------------")

            sub_keys = sorted(sub_count.keys(), key=lambda x: sub_count[x], reverse = True)

            for key in sub_keys:
                sub_key_count = sub_count[key]
                key_str = key + " "*(46 - len(key))
                print("    %s\t| %d\t| %f" % (key_str, sub_key_count, sub_key_count / sub_total)) 
        




class CountReducer:

    def __init__(self):
        self.general_stats = GeneralCounter()
        self.sstub_stats   = SStubCounter()
        self.edit_stats    = EditCounter()

    def __call__(self, slc):
        for counter in [self.general_stats, self.sstub_stats, self.edit_stats]:
            counter(slc)

    def report(self):
        print("General stats:")
        self.general_stats.report()
        print()

        print("SStub patterns:")
        self.sstub_stats.report()
        print()

        print("Edit operations:")
        self.edit_stats.report()
        print()


# Sorting ---------------------------------------------------------------

class SortingReducer:

    def __init__(self):
        sort_clazzes = [
            ("ALL",), ("BUGGY",), ("BUGGY", "SSTUB"), ("BUGGY", "SINGLE_EDIT"),
            ("BUGGY", "NOCOMODIFIED"), ("BUGGY", "NOCOMODIFIED", "SSTUB"),
            ("BUGGY", "NOCOMODIFIED", "SINGLE_EDIT")
        ]

        self.sort_clazzes = [(c, CountReducer()) for c in sort_clazzes]

    def __call__(self, slc_labels):
        slc, labels = slc_labels
        for sort_clazz, counter in self.sort_clazzes:
            if all(c in labels for c in sort_clazz):
                counter(slc)

    def report(self):
        for sort_clazz, counter in self.sort_clazzes:
            print("###################### Type: %s ###############################" % ",".join(sort_clazz))
            counter.report()


if __name__ == '__main__':
    sort_reducer = SortingReducer()
    mapreduce(label_instance, sort_reducer)
    sort_reducer.report()

