# TSSB-3M: Mining single statement bugs at massive scale
> Mining tool and large-scale datasets of single statement bug fixes in Python

[[**DATASETS**](#datasets) | [**CODE ARTIFACT**](https://doi.org/10.5281/zenodo.5898547)]

Access to single statement bug fixes at massive scale is not only important for exploring how developers introduce bugs in code and fix them but it is also
a valuable ressource for research in data-driven
bug detection and automatic repair. Therefore, we are releasing multiple large-scale collections of single statement bug fixes mined from public Python repositories.

## Datasets
To facilitate future research, we are releasing three
datasets:
* [**TSSB-3M:**](https://tssb3m.s3.eu-west-1.amazonaws.com/tssb_data_3M.zip) A dataset of over 3 million isolated single statement bug fixes. Each bug fix is related to a commit in a public Python that does not change more 
than a single statement.

* [**SSB-9M:**](https://tssb3m.s3.eu-west-1.amazonaws.com/ssb_data_9M.zip) A dataset of over 9 million single statement bug fixes. Each fix modifies at least a single statement to fix a bug. However, the related code changes might incorporate changes to other files.

* [**SSC-28M:**](https://tssb3m.s3.eu-west-1.amazonaws.com/ssc_data_28M.zip) A dataset of over 28 million general single statement changes. We are releasing this dataset with the intention to faciliate research in software evoluation. Therefore, a code change might not necessarily relate to a bug fix.

All datasets are available at [Zenodo](https://doi.org/10.5281/zenodo.5845439).

## Mining tool
This project has lead to muliple open source libraries released in indepedent repositories:

* [code.diff:](https://github.com/cedricrupb/code_diff) A library for fast AST based code differencing. The library is employed to compute
AST edit script between code changes and the detection
of SStuB patterns.

* [code.tokenize:](https://github.com/cedricrupb/code_tokenize) A library for fast tokenization and AST analysis of program code. This library was mainly developed for parsing source code during code differencing and is therefore the base for code.diff.

This repository additionaly includes all scripts used for mining single line edits and for filtering the datasets for single statement bug fixes. A description of the mining process can be found [below](#Mining-Process).


## Dataset Info
In the following, we provide an overview over central
statistics of the released datasets and description of the stored
dataset entries.

### Statistics

SStuB statistic:

Pattern Name	|	TSSB-3M|	SSB-9M     
----------------|----------------|-----------------------
| Change Idenfier Used  	|   237K	|      659K      	
| Change Binary Operand  	|   174K	|      349K      
| Same Function More Args 	|   150K	|      457K   
| Wrong Function Name    	|   134K	|      397K
| Add Function Around Expression 	|   117K	|      244K 
| Change Attribute Used 	|   104K	|      285K      
| Change Numeric Literal 	|   97K	|      275K 
| More Specific If  	|   68K	|      121K
| Add Method Call  	|   60K	|      118K          	
| Add Elements To Iterable  	|   57K	|      175K
| Same Function Less Args 	|   50K	|      169K     
| Change Boolean Literal  	|   37K	|      82K
| Add Attribute Access  	|   32K	|      74K
| Change Binary Opertor  	|   29K	|      71K
| Same Function Wrong Caller  	|   25K	|      46K
| Less Specific If   	|   22K	|      45K
| Change Keyword Argument Used  	|   20K	|      59K
| Change Unary Operator 	|   15K	|      23K
| Same Function Swap Args 	|   8K	|      77K
| Change Constant Type	|   6K	|      12K                   
  

NonSStuB Statistic:
Pattern Name	|	TSSB-3M|	SSB-9M     
----------------|----------------|-----------------------
Single Statement|   1.15M      | 3.37M
Single Token    |   740K       | 2.2M

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





