import argparse
import json

from collections import defaultdict
from tqdm import tqdm

def is_sstub(sstub_patterns):
    return any(c not in {"SINGLE_TOKEN", "SINGLE_STMT", "NO_STMT", "MULTI_STMT", "CHANGE_STRING_LITERAL"} for c in sstub_patterns)


def iterate_ngrams(pattern, n):
    for i in range(len(pattern)):
        start_offset = max(0, i - n + 1)
        ngram = ("SKIP",) * max(n - start_offset - 1, 0) +pattern[start_offset:start_offset + n]
        yield tuple(ngram)


class JaccardPatternIndex:

    def __init__(self, q = 1):
        self.q = q
        self._jaccard_index = defaultdict(set)
        self._qgram_cache   = {}

    def get_profile(self, pattern):
        if pattern not in self._qgram_cache:
            self._qgram_cache[pattern] = set(iterate_ngrams(pattern, self.q))
        return self._qgram_cache[pattern]

    def add(self, pattern):
        for qgram in self.get_profile(pattern):
            self._jaccard_index[qgram].add(pattern)

    def _compute_jaccard_if_necessary(self, pattern, other, min_jaccard = 0.0):

        # Trivial checks --------------------------------

        if min_jaccard == 1.0:
            return 0.0

        if pattern == other:
            return 1.0

        # Compute profiles ------------------------------
        pattern_profile = self.get_profile(pattern)
        other_profile   = self.get_profile(other)

        # If min_jaccard == 0.0, we cannot get any benefit by the heuristic
        if min_jaccard == 0.0:
            return len(set.intersection(pattern_profile, other_profile)) / len(set.union(pattern_profile, other_profile))

        # If min_jaccard > 0.0, we can stop if the computed value cannot be above threshold

        pattern_length = len(pattern_profile)
        other_length   = len(other_profile)

        # Step 1: Complete set length (strong approximation)

        if pattern_length <= min_jaccard * other_length or other_length <= min_jaccard * pattern_length:
            return 0.0

        # Step 2: Intersection to complete

        inter_length  = len(set.intersection(pattern_profile, other_profile))

        if inter_length <= min_jaccard * pattern_length or inter_length <= min_jaccard * other_length:
            return 0.0

        # Step 3: Compute full jaccard

        union_length = len(set.union(pattern_profile, other_profile))

        return  inter_length / union_length


    def compute_max_jaccard(self, pattern):
        max_sim = 0.0

        for qgram in self.get_profile(pattern):
            try:
                candidates = self._jaccard_index[qgram]

                for candidate in candidates:
                    max_sim = max(max_sim, self._compute_jaccard_if_necessary(pattern, candidate, max_sim))
                    if max_sim == 1.0: return max_sim
            
            except KeyError:
                continue

        return max_sim
        

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file")
    parser.add_argument("output_file")

    parser.add_argument("--ngram_length", type=int, default=1)

    args = parser.parse_args()

    index = JaccardPatternIndex(args.ngram_length)
    sstub_count = 0

    total = sum(1 for _ in open(args.input_file, "r"))

    with open(args.input_file, "r") as lines:
        for line in tqdm(lines, total=total, desc = "Index SStubs"):
            pattern_info = json.loads(line)

            if is_sstub([pattern_info["sstub"]]):
                index.add(tuple(pattern_info["pattern"]))
                sstub_count += pattern_info["count"]

    with open(args.output_file, "w") as o:
        with open(args.input_file, "r") as lines:
            for line in tqdm(lines, total = total, desc = "Compute distance"):
                pattern_info = json.loads(line)

                if not is_sstub([pattern_info["sstub"]]):
                    max_jaccard_sim = index.compute_max_jaccard(tuple(pattern_info["pattern"]))
                    distance = 1 - max_jaccard_sim
                else:
                    distance = 0.0

                pattern_info["distance_to_sstub"] = distance
                o.write(json.dumps(pattern_info) + "\n")


if __name__ == '__main__':
    main()