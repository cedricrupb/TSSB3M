# TSSB-3M: Mining single statement bugs at massive scale
> Mining tool and large-scale datasets of single statement bug fixes in Python

[[**PAPER**](https://arxiv.org/abs/2201.12046) | [**DATASETS**](#datasets) | [**CODE ARTIFACT**](https://doi.org/10.5281/zenodo.5898547)]

Access to single statement bug fixes at massive scale is not only important for exploring how developers introduce bugs in code and fix them but it is also
a valuable resource for research in data-driven
bug detection and automatic repair. Therefore, we are releasing multiple large-scale collections of single statement bug fixes mined from public Python repositories.

## :warning: Deduplicated Datasets
We came to notice that our datasets contain a significant number of duplicate patches that were missed by our deduplication procedure. To mitigate this, we are releasing cleaned versions of **TSSB-3M** and **SSB-9M**:

* [**CTSSB-1M**](https://tssb3m.s3.eu-west-1.amazonaws.com/ctssb_data_1M.zip) A cleaned version of TSSB-3M containing nearly a million isolated single statement bug fixes. 

* [**CSSB-2.6M**](https://tssb3m.s3.eu-west-1.amazonaws.com/cssb_data_2_6M.zip) A cleaned version of SSB-9M containing over 2.6 million single statement bug fixes.

To obtain the cleaned versions of the two datasets we implemented a more aggressive deduplication scheme (see `run_udiff_deduplication.py`). The cleaned datasets are also available on [Zenodo](https://doi.org/10.5281/zenodo.10217373). Statistics of the new datasets can be found [below](#statistics).

## Datasets
To facilitate future research, we are releasing three
datasets:
* [**TSSB-3M:**](https://tssb3m.s3.eu-west-1.amazonaws.com/tssb_data_3M.zip) A dataset of over 3 million isolated single statement bug fixes. Each bug fix is related to a commit in a public Python that does not change more 
than a single statement.

* [**SSB-9M:**](https://tssb3m.s3.eu-west-1.amazonaws.com/ssb_data_9M.zip) A dataset of over 9 million single statement bug fixes. Each fix modifies at least a single statement to fix a bug. However, the related code changes might incorporate changes to other files.

* [**SSC-28M:**](https://tssb3m.s3.eu-west-1.amazonaws.com/ssc_data_28M.zip) A dataset of over 28 million general single statement changes. We are releasing this dataset with the intention to faciliate research in software evolution. Therefore, a code change might not necessarily relate to a bug fix.

All datasets are available at [Zenodo](https://doi.org/10.5281/zenodo.10217373).

The datasets were collected for our research project related to:
```bibtex
@inproceedings{richter2022tssb,
  title={TSSB-3M: Mining single statement bugs at massive scale},
  author={Cedric Richter, Heike Wehrheim},
  booktitle={MSR},
  year={2022}
}
```

## Mining tool
This project has lead to muliple open source libraries released in indepedent repositories:

* [code.diff:](https://github.com/cedricrupb/code_diff) A library for fast AST based code differencing. The library is employed to compute
AST edit script between code changes and the detection
of SStuB patterns.

* [code.tokenize:](https://github.com/cedricrupb/code_tokenize) A library for fast tokenization and AST analysis of program code. This library was mainly developed for parsing source code during code differencing and is therefore the base for code.diff.

This repository additionaly includes all scripts used for mining single line edits and for filtering the datasets for single statement bug fixes. A description of the mining process can be found [below](#Mining-Process).

## Quick start (for using the datasets)
We provide our datasets as sets of commits referenced by URLs and git SHAs
and annotated with additional analytical information. All entries are stored in jsonlines format where each entry contains the following information:
```json
{
  "project_url": "URL of project containing the commit",
  "commit_sha" : "commit SHA of the code change",
  "file_path"  : "File path of the changed source file",
  "diff"       : "Universal diff of the code change",
  ...
}
```
A more detailed overview can be found [here](#json-fields). While this data contained in our datasets can be sufficient for most use cases, we sometimes which to extract the exact code from the original project. Therefore, we provide a `get_python_bugs.py` script that provides a frame implementation for extracting the code before and after the bug fix included in our datasets. The script automatically reads the datasets and clones the original repositories (thanks to [PyDriller](https://github.com/ishepard/pydriller)). The `visit_buggy_commit` need to be implemented:

* `visit_buggy_commit` is called on the referenced commit. Information like the code before and after the commit can be obtained
by processing the available PyDriller objects. Results of the mining process can be automatically stored by just returning JSON dict which
is then stored in a jsonlines format.

Note however that cloning all datasets might require multiple days (or month) on a single machine. Therefore, filtering the dataset beforehand might be necessary.

## Dataset Info
In the following, we provide an overview over central
statistics of the released datasets and description of the stored
dataset entries.

### Statistics

SStuB statistic:

Pattern Name	| CTSSB-1M |	TSSB-3M|	SSB-9M     
----------------|----------------|----------------|-----------------------
| Change Idenfier Used  | 69K	|   237K	|      659K      	
| Change Binary Operand | 48K	|   174K	|      349K      
| Same Function More Args | 41K	|   150K	|      457K   
| Wrong Function Name   | 39K	|   134K	|      397K
| Add Function Around Expression | 32K	|   117K	|      244K 
| Change Attribute Used  | 30K	|   104K	|      285K      
| Change Numeric Literal | 33K	|   97K	|      275K 
| More Specific If  | 16K	|   68K	|      121K
| Add Method Call  | 17K 	|   60K	|      118K          	
| Add Elements To Iterable | 15K 	|   57K	|      175K
| Same Function Less Args | 14K	|   50K	|      169K     
| Change Boolean Literal | 13K 	|   37K	|      82K
| Add Attribute Access | 10K 	|   32K	|      74K
| Change Binary Operator | 9K	|   29K	|      71K
| Same Function Wrong Caller | 8K	|   25K	|      46K
| Less Specific If  | 5K 	|   22K	|      45K
| Change Keyword Argument Used | 6K 	|   20K	|      59K
| Change Unary Operator  | 4K	|   15K	|      23K
| Same Function Swap Args | 2K	|   8K	|      77K
| Change Constant Type | 2K	|   6K	|      12K                   
  

NonSStuB Statistic:
Pattern Name	| CTSSB-1M |	TSSB-3M|	SSB-9M     
----------------|----------------|----------------|-----------------------
Single Statement| 333K |   1.15M      | 3.37M
Single Token    | 220K |   740K       | 2.2M

### JSON fields
The released dataset indexes up to 28 million single statement change commits from more than 460K git projects. All dataset entries are stored in a compressed [jsonlines](https://jsonlines.org) format. Because of size of the dataset, we sharded the dataset in files containing 100.000 commits each. Each entry does not only contain information to access the original source code but also information supporting basic analyses. A description of the stored json objects is given in the following:

**Commit details:**
- **project:** Name of the git project where the commit occurred.
- **project_url:** URL of project containing the commit
- **commit_sha:** commit SHA of the code change
- **parent_sha:** commit SHA of the parent commit
- **file_path:** File path of the changed source file
- **diff:** Universal diff describing the change made during the commit
- **before:** Python statement before commit
- **after:** Python statement after commit (addresses the same line)

**Commit analysis:**
- **likely_bug:** `true` if the commit message indicates that the commit is a bug fix. This is heuristically determined.
- **comodified:** `true` if the commit modifies more than one statement in a single file (formatting and comments are ignored).
- **in_function:** `true` if the changed statement appears inside a Python function
- **sstub_pattern:** the name of the single statement change pattern the commit can be classified for (if any). Default: `SINGLE_STMT`
- **edit_script:** A sequence of AST operation to transform the code before the commit to the code after the commit (includes `Insert`, `Update`, `Move` and `Delete` operations).


## Mining Process
To mine software repositories for millionth of single
statement bugs, we developed multiple scripts for mining and filtering the datasets. We describe them in the following in the order which they should be executed:

`run_batch_crawler.py`: A script to mine a batch of Git repositories. The crawler will sequentially checkout each repository and then search the Git history for single line edits
```bash
$ python run_batch_crawler.py [--compress] [index_file] [output_dir]
```
The index file should be file with a list of Git repository urls. Output dir is the directory where mining results are saved to. Optionally, the script can save results into compressed files to save disk space.

`convert_to_jsonl_gz.py`: Can be skipped if only one batch crawler was used. This script can be employed to collect all files produced by the batch crawler and save them in a single directory containing compressed jsonl files.

`run_deduplication.py`: Filters the dataset for duplicate entries (based on project name, commit hash and file difference).

`run_slc_process.py`: Filter a given collection
of single line edits for single line changes (without any other code modifications). In addition, this also identifies potential SStuB paterns
and computes the edit script.

`rm_parse_errors.py`: Remove all entries where the diff could not be parsed.

`rm_nostmt.py`: Remove all entries that are not single
statement changes.

After running, `rm_nostmt.py` were are now performed the necessary steps to create **SSC-28M**.

`rm_nobug.py`: Remove all entries which are not likely
related to a bug. Bug fixes are identifed heuristically by checking the commit message for certain keywords. The strategy has been proven to be highly precise.

After running, `rm_nobug.py` were are now performed the necessary steps to create **SSB-9M**.

`rm_comodified.py`: Remove all entries that belong
to commits that modify more than one statement. Bug fixes are often tangled with non-fixing code changes. To avoid mining the tangled changes, we remove all bug-fixes that modifiy more than one statement.

After running, `rm_comodified.py` were are now performed the necessary steps to create **TSSB-3M**.

The initial mining process (`run_batch_crawler.py`) used repository urls extracted from Libraries.io 1.6 and were performed on a cluster for two weeks. After mining, the remaining steps were performed on a single machine.

In addition to the scripts necessary for mining our datasets, we additionally provide scripts for analyzing the generated datasets:

`stats.py`: Collects statistics over the dataset. Statistics include number of commits, number of projects, SStuB pattern distribution, distribution of central AST edit operations.

`compute_edit_patterns.py`: For each bug fix transform
the AST edit script into an edit pattern. The translation converts for example inserting a binary operator into an assignment as `Insert(binary_op, assign)`.

`compute_pattern_distance.py`: For each pattern, compute smallest jaccard distance to a bug fix classified as a SStuB.

`typo_identification.py`: Computes the percentage
of bug fixing commits that can be likely attributed to typos. Code changes are considered as typo fixes whenever the Damerau-Levenshtein distance between bug and fix is lower equal 2.





