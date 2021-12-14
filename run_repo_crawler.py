import argparse
import json

from tqdm import tqdm
from collections import namedtuple
from collections import OrderedDict
from pydriller import Repository, ModificationType

from code_diff.diff_utils import parse_hunks

from tssb_miner.diff_utils import iter_stmts
from tssb_miner.diff_utils import has_diff, diff_tokens
from tssb_miner.tokenizers import tokenize

LANG_EXTENSIONS = {
    "python": [".py"],
    "java": [".java"],
    "javascript": [".js"]
}

SingleLineCommit = namedtuple("SingleLineCommit", ["project_url", "commit", "modfile", "lang"])

# Identify single line commits --------------------------------


def all_statements_common(lines, common_set, lang):
    
    for i, line in lines.items():
        if i in common_set: continue
        
        if is_statement(line, lang): return False
            
    return True


def is_single_line(parsed_diff, lang):

    added, rms = OrderedDict(parsed_diff["added"]), OrderedDict(parsed_diff["deleted"])
    
    common_lines = set.intersection(set(added.keys()), set(rms.keys()))
    
    if len(common_lines) == 0: return False
    
    # All non-common lines have to be comments!
    
    if not all_statements_common(added, common_lines, lang): return False
    if not all_statements_common(rms,   common_lines, lang): return False
    
    diff_lines = 0
    
    for line_ix in common_lines:
        add_line, rm_line = added[line_ix], rms[line_ix]

        is_add_stmt = is_statement(add_line, lang)
        is_rm_stmt  = is_statement(rm_line, lang)    

        if not is_add_stmt and not is_rm_stmt: continue
        if is_add_stmt != is_rm_stmt: return False # Here we uncomment things or remove a code (no code change)

        if has_diff(add_line, rm_line, lang): diff_lines += 1
        if diff_lines > 1: break
    
    return diff_lines == 1


# Test if single token modification ---------------------------

def is_single_token_mod(diff, lang):
    hunks = parse_hunks(diff)
    
    if len(hunks) != 1: return False
    
    hunk = hunks[0]
    new_lines, old_lines = list(iter_stmts(hunk.after)), list(iter_stmts(hunk.before))
    
    if len(new_lines) != len(old_lines): return False
    if len(new_lines) == 0: return False
    
    single_diffs = 0
    
    for i in range(len(new_lines)):
        diff = diff_tokens(new_lines[i], old_lines[i], lang)
        
        if len(diff) > 1: return False
        
        if len(diff) == 1: single_diffs += 1
    
    return single_diffs == 1


def single_token_mod(diff, lang):
    hunks = parse_hunks(diff)
    single_diff = None

    for hunk in hunks:
        new_lines, old_lines = list(iter_stmts(hunk.after)), list(iter_stmts(hunk.before))
        
        if len(new_lines) != len(old_lines): return "None"
        if len(new_lines) == 0: return "None"
        
        for i in range(len(new_lines)):
            diff = diff_tokens(new_lines[i], old_lines[i], lang)

            if len(diff) == 0: continue
            if len(diff) > 1: return "None"

            if single_diff is None:
                single_diff = diff[0][0][1]
            else:
                return "None"
    
    return single_diff if single_diff is not None else "None"
    

def is_likely_bug(commit_msg):
    return any(t in commit_msg.lower() for t in ["error", "bug", "fix", "issue", "mistake", 
                                                    "incorrect", "fault", "defect", "flaw", "type"])

def is_infunction(modfile):
    return len(modfile.changed_methods) > 0

def create_result_entry(commit, modfile, lang = "python"):

    return {
        "project": commit.project_name, 
        "commit_sha": commit.hash,
        "parent_sha": commit.parents[0],
        "file_path" : modfile.old_path,

        # Metrics useful for filtering the index
        "likely_bug" : is_likely_bug(commit.msg),
        "comodified" : len(commit.modified_files) > 1,
        "in_function": is_infunction(modfile),
        "single_token_mod": single_token_mod(modfile.diff, lang),

        # Diff used to update the code
        "diff": modfile.diff,
        
    }



def parse_commit(commit, lang = "python"):
    
    for modfile in commit.modified_files:
        
        # Heuristics to exclude mod files
        if modfile.change_type != ModificationType.MODIFY: continue
        if not any(modfile.filename.endswith(ext) for ext in LANG_EXTENSIONS[lang]): continue
        if not is_single_line(modfile.diff_parsed, lang): continue

        yield modfile
        

def crawl_single_line_commits(repo_url, lang = "python"):
    repo = Repository(repo_url, only_modifications_with_file_types=LANG_EXTENSIONS[lang])

    T = tqdm(repo.traverse_commits())

    for commit in T:

        # Filter to exclude commits
        if commit.merge: continue
        if len(commit.parents) != 1: continue

        for single_line_mod in parse_commit(commit, lang):
            yield SingleLineCommit(repo_url, commit, single_line_mod, lang)
            


def main(): 
    parser = argparse.ArgumentParser()

    parser.add_argument("repo_url")
    parser.add_argument("output_file")

    parser.add_argument("--lang", default="python")

    args = parser.parse_args()

    with open(args.output_file, "w") as o:
        for slc in crawl_single_line_commits(args.repo_url, args.lang):
            slc_info = create_result_entry(slc.commit, slc.modfile, slc.lang)
            if slc_info is None: continue # We reject a single code change because an AST analysis found an incompatible type
            slc_info["project_url"] = slc.project_url
            o.write(json.dumps(slc_info) + "\n")


# Helpers ----------------------------------------------------------------

def is_statement(line, lang):
    if len(line) == 0: return False
    
    return any(tok_type != "comment" for _, tok_type in tokenize(line, lang))

# ------------------------------------------------------------------------


if __name__ == '__main__':
    main()