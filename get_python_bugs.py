from mapreduce import mapreduce

from pydriller import Repository

# Need to be implemented --------------------------------

def visit_buggy_commit(commit_slc, commit_obj, modfile):
    """
    This function need to be implemented to process buggy commits in the dataset.

    commit_slc : dict
        Original dataset entry containing all information regarding the current bug commit
    
    commit_obj : PyDriller commit
        An object representing the buggy commit created by PyDriller

    modfile : PyDriller modfile
        An object representing the changed file in the buggy commit

    Return: dict
        A dictonary of all information that should be stored for the current commit.
        Keys and values have to be JSON serializable!

    ---------------------
    Sample usages:
        - Commit messages can be retrieved with commit_obj.msg
        - Buggy code can be obtained by modfile.source_code_before
        - Fixed code can be obtained by modfile.source_code
    
    Further information available: 
        https://pydriller.readthedocs.io/en/latest/commit.html
        https://pydriller.readthedocs.io/en/latest/modifiedfile.html
    
    """

# Downloader --------------------------------------------


def download_code_for_slc(slcs):    
    project_url = slcs[0]["project_url"]

    assert all(slc["project_url"] == project_url for slc in slcs)

    request_url = project_url.replace("https://", "https://:@")

    hash_to_slc = {slc["commit_sha"]: slc for slc in slcs}

    repo = Repository(request_url, only_commits=list(hash_to_slc.keys()))

    output = []
    for commit in repo.traverse_commits():
        commit_slc = hash_to_slc[commit.hash]

        for modfile in commit.modified_files:
            if commit_slc["file_path"] == modfile.new_path: break
        
        output.append(
            visit_buggy_commit(commit_slc, commit, modfile)
        )

    return output


def try_download_slcs(slcs):
    try:
        return download_code_for_slc(slcs)
    except Exception as e:
        print(e)
        return []

    
if __name__ == '__main__':
    mapreduce(try_download_slcs, group_by = lambda slc: slc["project_url"])