## TSSB-3M: Mining single statement bugs at massive scale

Single statement bugs (and bug fixes) play a major role in the evaluation and design of automatic bug finders and
program repair. With the recent advances in data-driven
bug detection and repair, single statement bug fixes at the scale of millionth examples become more important than ever. For this reason, we are releasing three new
datasets consisting of single statement changes and bug fixes from over 500K Python Git projects.

## :warning: Deduplicated Datasets
We came to notice that our datasets contain a significant number of duplicate patches that were missed by our deduplication procedure. To mitigate this, we are releasing cleaned versions of **TSSB-3M** and **SSB-9M**:

* [**CTSSB-1M**](https://tssb3m.s3.eu-west-1.amazonaws.com/ctssb_data_1M.zip) A cleaned version of TSSB-3M containing nearly a million isolated single statement bug fixes. 

* [**CSSB-2.6M**](https://tssb3m.s3.eu-west-1.amazonaws.com/cssb_data_2_6M.zip) A cleaned version of SSB-9M containing over 2.6 million single statement bug fixes.

 The cleaned datasets are also available on [Zenodo](https://doi.org/10.5281/zenodo.10217373). 

### Datasets
To download our datasets, use:

* [TSSB-3M](https://tssb3m.s3.eu-west-1.amazonaws.com/tssb_data_3M.zip): A dataset of over 3 million isolated single statement bug fixes. Each bug fix is related to a commit in a public Python that does not change more than a single statement.

* [SSB-9M](https://tssb3m.s3.eu-west-1.amazonaws.com/ssb_data_9M.zip): A dataset of over 9 million single statement bug fixes. Each fix modifies at least a single statement to fix a bug. However, the related code changes might incorporate changes to other files.

* [SSC-28M](https://tssb3m.s3.eu-west-1.amazonaws.com/ssc_data_28M.zip): A dataset of over 28 million general single statement changes. We are releasing this dataset with the intention to faciliate research in software evoluation. Therefore, a code change might not necessarily relate to a bug fix.

All datasets are also available at [Zenodo](https://zenodo.org/record/5845439).

### Main Takeaways
Datasets of single statement bugs such as [ManySStuBs4J](https://github.com/mast-group/mineSStuBs) in Java or [PySStuBs](https://zenodo.org/record/4589607) in Python have helped us a lot in our research. However, their size limited the upscaling of experiments and data analyses. Therefore, we are excited to release three new datasets several magnitudes larger than any existing bug collections.
Here are our main takeaways for our datasets:
* [Dataset statistics:](#dataset-info) SSB-9M contains more than 50x more SStuBs than PySStuBs. With focus on isolated bug fixes, TSSB-3M still contains more than 20x more SStuBs than PySStuBs. This gives us access to not only a larger quantity of simple bugs but also
to a higher variety.

* [NonSStuBs:](#nonsstubs) Most single statement bugs can be repaired with the same operations as needed for repairing SStuBs. It is likely that effective detection and repair methods for SStuBs will be effective for general single statement bugs.

* [Bug-fix complexity:](#complexity-of-a-bug-fix) Single statement bugs typically require simple fixes. A bug is typically fixed by 4 to 5 AST modifications.

* [Typos:](#typos) Typos are more common than expected for single statement bugs. At least 20% of single statement bugs are likely caused by a typo.

### Dataset Info
In the following, we provide a closer look at the dataset statsistics of TSSB-3M and SSB-9M.

Pattern Name	|	TSSB-3M|	SSB-9M     
----------------|----------------|-----------------------
Change Idenfier Used  	|   237K	|      659K      
Change Binary Operand  	|   174K	|      349K      
Same Function More Args 	|   150K	|      457K   
Wrong Function Name    	|   134K	|      397K
Add Function Around Expression 	|   117K	|      244K 
Change Attribute Used 	|   104K	|      285K      
Change Numeric Literal 	|   97K	|      275K 
More Specific If  	|   68K	|      121K
Add Method Call  	|   60K	|      118K          	
Add Elements To Iterable  	|   57K	|      175K
Same Function Less Args 	|   50K	|      169K     
Change Boolean Literal  	|   37K	|      82K
Add Attribute Access  	|   32K	|      74K
Change Binary Opertor  	|   29K	|      71K
Same Function Wrong Caller  	|   25K	|      46K
Less Specific If   	|   22K	|      45K
Change Keyword Argument Used  	|   20K	|      59K
Change Unary Operator 	|   15K	|      23K
Same Function Swap Args 	|   8K	|      77K
Change Constant Type	|   6K	|   12K  

Some examples for Python bug fixes that are classified as SStuBs will be coming soon in our [repository](https://github.com/cedricrupb/TSSB3M). Until then, [ManySStuBs4J](https://github.com/mast-group/mineSStuBs) provides a nice overview of examples for Java.

### NonSStuBs
Only around 40% of all single statement bugs in our datasets can be classified by a SStuB pattern (in one of the categories of the previous section). For this reason, we analysed the remaining single statement bugs in the TSSB-3M dataset.

![NonSStub image](/TSSB3M/assets/nonsstub.png)

We found that NonSStuBs (i.e. bugs that do not classify as a SStuB) are actually quite similar to SStuBs. In the previous image, we compared the edit operations needed to fix a SStuB with the operations needed to fix a NonSStuB. 
We observed that most NonSStuB employ the same or similar operation types to fix a bug. Still, there exists some infrequent bugs (SStuB-unrelated) that are not covered by any SStuB category.

### Complexity of a Bug-Fix
Most existing methods in automatic repair focus on bugs
that can be fixed within a few edit operations. Therefore, we analyzed how many edit operations are needed in our TSSB-3M dataset.

![Complexity image](/TSSB3M/assets/complexity.png)

The figure shows the distribution of the length of individual bug fixes. We find that most bugs can be fixed within a few edit operations (4-5 operations). However, there still exists bugs that require a much higher number of fix operations.

### Typos
Humans commonly mistype during writting text. Since code is also written text, we expect that typos occur often in code and hence are also common for single statement bug fixes.

![Typo image](/TSSB3M/assets/typos.png)

In the shown image, we count how often a bug is fixed by inserting, removing or transposing up to two characters. Unsurprisingly, we found that typos occur often both in SSB-9M and TSSB-3M (atleast 20% of all bug fixes). In addition, they have a frequency for fixes that address identifiers or strings.
