## TSSB-3M: Mining single statement bugs at massive scale

Single statement bugs (and bug fixes) play a major role in the evaluation and design of automatic bug finders and
program repair. With the recent advances in data-driven
bug detection and repair, single statement bug fixes at the scale of millionth examples become more important than ever. For this reason, we are releasing three new
datasets consisting of single statement changes and bug fixes from over 500K Git projects.

### Datasets
To facilitate future research, we are releasing three datasets:

* [**TSSB-3M**](): A dataset of over 3 million isolated single statement bug fixes. Each bug fix is related to a commit in a public Python that does not change more than a single statement.

* [**SSB-9M**](): A dataset of over 9 million single statement bug fixes. Each fix modifies at least a single statement to fix a bug. However, the related code changes might incorporate changes to other files.

* [**SSC-28M**](): A dataset of over 28 million general single statement changes. We are releasing this dataset with the intention to faciliate research in software evoluation. Therefore, a code change might not necessarily relate to a bug fix.

All datasets are also available at [Zenodo](https://zenodo.org/record/5845439).
