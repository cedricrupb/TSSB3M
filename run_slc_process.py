"""
This script preprocesses all entries.

1. We remove all hunks that do not modify code (comments or formatting)
2. We compute the SStuB pattern (if possible)
3. We compute an AST edit script between the code before and after

"""

from mapreduce import mapreduce

import code_diff as cd
from code_diff.diff_utils import parse_hunks, clean_hunk
from code_diff.gumtree    import json_serialize

import logging as logger
logger.basicConfig(filename='run_slc.log', filemode='w', encoding='utf-8', level=logger.DEBUG)


def create_output(slc, hunk, **kwargs):  

    diff_message = str(hunk)

    assert len(diff_message) > 0 and len(diff_message.splitlines()) > 0

    output = {
        "project": slc["project"],
        "commit_sha": slc["commit_sha"],
        "parent_sha": slc["parent_sha"],
        "file_path": slc["file_path"],
        "project_url": slc["project_url"],

        "likely_bug": slc["likely_bug"],
        "comodified": slc["comodified"],
        "in_function": slc["in_function"],
        
        "diff": diff_message,
    }

    output.update(kwargs)
    return output


def _increase_ast_size(diff, current_level):

    if current_level == 0:
        try:
            return diff.statement_diff()
        except Exception:
            return diff
        
    if current_level == 1:
        return diff.root_diff()

    if current_level > 1: return diff


def _is_ghost_script(script):
    if script is None: return True
    if len(script) == 0: return False

    return hasattr(script[0].target_node, "node_id")


def compute_edit_script_it(diff):
    # For efficiency, we donnot compute the edit script for the full AST
    # While this works in most cases, there exists some corner cases where it fails.
    # However, we can detect when computation fails: 
    # ghost nodes (i.e. nodes that do not appear in AST)
    # appear in the edit script.
    # If this is the case, we increase the AST context and recompute the edit script

    edit_script = None
    diff_level  = 0

    while diff_level < 3:
        edit_script = diff.edit_script()

        if not _is_ghost_script(edit_script): return edit_script
        
        diff = _increase_ast_size(diff, diff_level)
        diff_level += 1

    return edit_script # Return most precise edit script (even if it has ghost nodes)



def process_hunk(slc, hunk):

    if len(str(hunk)) > 10_000: # Typically hunks are much smaller than this.
        logger.debug("Skip hunk in %s [%s] because it is too large" % (slc["project"], slc["commit_sha"]))
        return None
    
    # Generate diff
    logger.debug("Compute diff for hunk in %s [%s]" % (slc["project"], slc["commit_sha"]))
    try:
        diff = cd.difference(hunk.before, hunk.after, lang = "python")
    except Exception:
        logger.debug("Skip hunk in %s [%s]" % (slc["project"], slc["commit_sha"]))
        return None
    
    # Process diff
    logger.debug("SStub pattern for hunk in %s [%s]" % (slc["project"], slc["commit_sha"]))
    sstub_pattern = diff.sstub_pattern()

    logger.debug("Edit script for hunk in %s [%s]" % (slc["project"], slc["commit_sha"]))
    edit_script = compute_edit_script_it(diff)

    try:
        stmt_diff = diff.statement_diff()
        before_diff = stmt_diff.source_text
        after_diff  = stmt_diff.target_text
    except ValueError:
        before_diff = diff.source_text
        after_diff  = diff.target_text

    edit_script_json = json_serialize(edit_script)

    logger.debug("Return output for hunk in %s [%s]" % (slc["project"], slc["commit_sha"]))
    return create_output(slc, hunk,
                            before = before_diff,
                            after  = after_diff,
                            sstub_pattern = sstub_pattern.name,
                            edit_script   = edit_script_json)


def process_slc(slc):
    logger.debug("Parse hunks for %s [%s]" % (slc["project_url"], slc["commit_sha"]))
    
    diff_message = slc["diff"]
    diff_hunks   = parse_hunks(diff_message)

    outputs = []
    for hunk in diff_hunks:
        hunk = clean_hunk(hunk)
        output = process_hunk(slc, hunk)
        if output is not None: outputs.append(output)
        
    return outputs
    

def try_process_slc(slc):
    try:
        return process_slc(slc)
    except Exception:
        return []


if __name__ == '__main__':
    mapreduce(try_process_slc)