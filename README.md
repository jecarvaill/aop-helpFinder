# AOP-HelpFinder : A tool to help users to establish adverse outcomes pathways.

---
## DESCRIPTION
This software linked adverse outcomes, diseases and key-events with reviews.
This is based on a text mining and parsing process on abstract.

Software implemented for Human Biomonintoring in Europe (HBM4EU) Work Package
13.1.

HBM4EU has received funding from the European Union’s H2020 research and innovation programme under grant agreement No 733032.

## Python Compatibility 
This program is compatible with python 3.x.


## Installation

### Installation & usage from sources

1. Clone this repo `git clone https://github.com/jcarvaill/aop-helpFinder`
2. Install dependancies:

   2.1. Using pip (and use python environment system)
    
      `sudo pip install -r requirements.txt` or `sudo pip3 install -r requirements.txt`
    
 
   2.2. Using virtualenv, suggested (use a virtual environment, leaving your python installation untouched)
    
      - To install virtualenv via pip:
        
        `sudo pip install virtualenv` or `sudo pip3 install virtualenv`

      - To create a virtual environment for aop-helpFinder:
        
        `virtualenv aop-helpFinder_venv`

      - Don't forget to activate environment with:
        
        `source {PATH}/aop-helpfinder_venv/bin/activate`

      - (To deactivate environment: `deactivate`)

      - Same as 2.1.

   2.3. (Easy) Using directly aop-helpFinder scripts

      `python {PATH}/aop-helpfinder/aop-helpFinder.py` or `python3 {PATH}/aop-helpfinder/aop-helpFinder.py`

   To proceed, bin directory should be conserved

3. Use aop-helpFinder scripts with `python {PATH}/aop-helpFinder/aop-helpFinder.py` or `python3 {PATH}/aop-helpFinder/aop-helpFinder.py`


## Dependancies and installation: 
Following packages are needed: 
  - argparse
  - argcomplete (for autocompletion, optional)
  - chardet
  - html
  - networkx
  - nltk
  - pdfminer.six
  - sqlite3
  - tqdm


## ARGUMENTS 
```text
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        path of the directory which contains files related to
                        the study molecule
  -d DATABASE, --database DATABASE
                        path or name of the database to used or to created
  -a ADVERSE_OUTCOME, --adverse_outcome ADVERSE_OUTCOME
                        path of the file which contains current adverse
                        outcomes. This file exist on AOPwiki website. This is
                        explained in readme file.
  -c CTD_FILE, --ctd_file CTD_FILE
                        path of the file which contains diseases in a tsv
                        format. This file should be performed by CTD database
                        beforehand. This is explained in the readme file.
  -k KE_FILE, --ke_file KE_FILE
                        path of the file which contains key-events in a tsv
                        format. This file should be performed with AOPwiki
                        beforehand. This is explained in the readme file.
  -r KER_FILE, --ker_file KER_FILE
                        path of the file which contains key-events-
                        relationships in a tsv format. This file should be
                        performed with AOPwiki beforehand. This is explained
                        in the readme file.
  -o OUTPUT, --output OUTPUT
                        write a result file which contains adverse outcomes or
                        diseases linked to corresponding occurence
  -cdt CYTOSCAPE_NODES, --cytoscape_nodes CYTOSCAPE_NODES
                        write a result file which contains nodes of a
                        cytoscape network
  -cne CYTOSCAPE_NETWORK, --cytoscape_network CYTOSCAPE_NETWORK
                        write a result file which contains adverse outcomes,
                        diseases or key-events linked to a specific review
  -ani ANIMALS, --animals ANIMALS
                        path of the file which contains common_name of animals
                        contributing generally in science
  -cpu [NUMBER_OF_CPU], --number_of_cpu [NUMBER_OF_CPU]
                        number of cpu to use at the execution of the software
```

-h, --help
Display help of the software.

`python3 aop_finder.py -h`

### Required arguments:

- -d DATABASE, --database DATABASE
  
path or name of the database to used or to created.

If the database is empty or does not exists, this argument is necessary.

- -i INPUT, --input INPUT
  
path of the directory which contains files related to the study molecule.

#### Format of files accepted:

These files are obtained with a request on DART, HSDB, TOXLINE databases.
Excepted for CCRIS and RTECS (private database).

  - CCRIS (.pdf)
  - DART (.txt)
  - HSDB (.txt)
  - RTECS (.pdf)
  - TOXLINE (.txt)

`python3 aop_finder.py -d database/bispenolS.db -i data/raw-data/BPS/`

### Optional arguments:

- -a ADVERSE_OUTCOME, --adverse_outcome ADVERSE_OUTCOME

path of the file which contains current adverse outcomes. This file is
performed with AOPwiki website. It corresponds to all adverse outcomes
indexed on AOPwiki website. See doc directory.

`python3 aop_finder.py -d ./database/bispenolS.db -i ./data/raw-data/BPS/
-a data/AOPwiki/61-current-AO-25Aout2017.txt`

- -c CTD_FILE, --ctd_file CTD_FILE

path of the file which contains diseases in a tsv format. This file should be
performed by CTD database beforehand. This file corresponds to the disease
vocabulary file downloadable on http://ctdbase.org/downloads/

`python3 aop_finder.py -d ./database/bispenolS.db -i ./data/raw-data/BPS/
-c data/diseases/CTD_diseases-2017-09-28.tsv`

- -k KE_FILE, --ke_file KE_FILE

path of the file which contains key-events in a tsv format. This file should
be performed with AOPwiki beforehand. This file corresponds to all key-events
indexed on AOPwiki website. See doc directory.

`python3 aop_finder.py -d ./database/bispenolS.db -i ./data/raw-data/BPS/
-k data/AOPWiki/Key-events-25August2017.txt`

- -r KER_FILE, --ker_file KER_FILE

path of the file which contains key-events- relationships in a tsv format.
This file should be performed with AOPwiki beforehand. This file corresponds
to all key-events-relationships indexed on AOPwiki website. See doc directory.

`python3 aop_finder.py -d ./database/bispenolS.db -i ./data/raw-data/BPS/
-r data/AOPWiki/KE-relationships-25August2017.txt`

- -o OUTPUT, --output OUTPUT

write a result file which contains adverse outcomes or diseases linked to
corresponding occurence.

`python3 aop_finder.py -d ./database/bispenolS.db -i ./data/raw-data/BPS/
-o output/disease_finded_BPS.csv`

- -cdt CYTOSCAPE_NODES, --cytoscape_nodes CYTOSCAPE_NODES

write a result file which contains nodes of a cytoscape network.

`python3 aop_finder.py -d ./database/bispenolS.db -i ./data/raw-data/BPS/
-ctd output/cytoscape_nodes_bisphenolS.tsv`

- -cne CYTOSCAPE_NETWORK, --cytoscape_network CYTOSCAPE_NETWORK

write a result file which contains adverse outcomes, diseases or key-events
linked to a specific review.

`python3 aop_finder.py -d ./database/bispenolS.db -i ./data/raw-data/BPS/
-cne output/cytoscape_network_bisphenolS.tsv`

- -ani ANIMALS, --animals ANIMALS

path of the file which contains common_name of animals contributing generally
in science.

`python3 aop_finder.py -d ./database/bispenolS.db -i ./data/raw-data/BPS/
-ani data/animals/common_name.txt`

- -cpu [NUMBER_OF_CPU], --number_of_cpu [NUMBER_OF_CPU]

number of cpu to use at the execution of the software.

`python3 aop_finder.py -d ./database/bispenolS.db -i ./data/raw-data/BPS/
-cpu 8`
    
## USAGE: 
cd src/aop_finder/

aop-helpFinder/data/raw-data directory contains abstracts of reviews in multiple files.
You can use these files to test the software.
aop-helpFinder/output directory contains results of the software in function of input file.

Command to launch an analyze on BPS reviews not including Comparative
Toxicogenomics Database diseases vocabulary file:

 ```text
 python3 aop_finder.py -d database/bisphenolS_AO.db -i data/raw-data/BPS/
-cdt output/cytoscape_nodes_bisphenolS_AO.tsv
-cne output/cytoscape_network_bisphenolS_AO.tsv
-a data/AOPwiki/61-current-AO-25Aout2017.txt -cpu 8
```

Command to launch an analyze on BPS reviews including Comparative
Toxicogenomics Database diseases vocabulary file:

 ```text
 python3 aop_finder.py -d database/bisphenolS.db -i data/raw-data/BPS/
-cdt output/cytoscape_nodes_bisphenolS.tsv
-cne output/cytoscape_network_bisphenolS.tsv
-a data/AOPwiki/61-current-AO-25Aout2017.txt 
-c data/diseases/CTD_diseases-2017-09-28.tsv -cpu 8
```

by default the results files are in output directory

## Licence
This program is under the GNU GPLv3 licence, which means that anyone who 
distributes this code or a derivative work has to make the source available under 
the same terms, and also provides an express grant of patent rights from 
contributors to users.
