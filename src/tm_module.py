#!/usr/bin/python3
# -*- coding: utf-8 -*-

######################################
# DESCRIPTION
######################################

__author__ = "Jean-Charles CARVAILLO"
__version__  = "1.0"
__license__ = "GNU GPLv3"
__date__ = "2019/02"

"""
Text Mining Module
INSERM UMR-S 1124 Team 1
jeancharles.carvaillo@inserm.fr
"""

######################################
# IMPORT
######################################

# set the path of nltk_data
import os.path
PATH = os.path.dirname(os.path.realpath(__file__))
PATH = "/".join(PATH.split("/")[0:-1])
import nltk.data
nltk.data.path.append(PATH + '/data/nltk_data/')

import nltk.corpus
import nltk.stem
from nltk.tokenize import sent_tokenize
from nltk import word_tokenize
import re
import string

######################################
# FUNCTION
######################################


def clean_abstract(abstract, case):
    """Method to clean and simplify an abstract by text mining process.
        1. Split abstract by sentences
        2. Split sentences by words
        3. Remove sentences which contain a negation word
        4. Remove stopwords from words in a sentence
        5. Stem process

    Return:
        abstract (str): cleaned and simplified abstract

    """
    # set list of tools
    negations = ['never', 'neither', 'no', 'none', 'nor', 'not', 'ain',
                 'aren', 'couldn', 'didn', 'doesn', 'hadn', 'hasn', 'haven',
                 'isn', 'mightn', 'mustn', 'needn', 'shan', 'shouldn', 'wasn',
                 'weren', 'won', 'wouldn']
    punctuation = list(string.punctuation)
    stop = nltk.corpus.stopwords.words('english') + punctuation + ['\'s']

    # 1. split abstract by sentences
    sents = sent_tokenize(abstract)

    sents = [sent for sent in sents if not (bool(re.search('\d', sent) and
             'body weight' in sent))]

    # 2. split sentences by words
    abstract = [word_tokenize(sent) for sent in sents]

    # 3. remove sentences which contain a negation word
    abstract = [sent for sent in abstract if not
                any(negation in sent for negation in negations)]

    # 4. remove stopwords in sentences
    for i in range(len(abstract)):
        abstract[i] = [word for word in abstract[i] if word not in stop]

    # 5. stem process
    for i in range(len(abstract)):
        abstract[i] = stem_process(abstract[i])
        abstract[i] = ' '.join(abstract[i])

    # 6. AOD or KEr search case
    if case is True:
        abstract = ' '.join(abstract)
        return abstract
    else:
        return abstract


def stem_process(words):
    """Method to stem each words in a list.

    Return:
        words (list): a list which contains stemmed words.

    """
    # snowball stemmers developed by Martin Poter
    sno = nltk.stem.SnowballStemmer('english')
    # search if a particular word is in words
    for i in range(len(words)):
        words[i] = sno.stem(words[i])
    return words

######################################
# Main()
######################################

if __name__ == '__main__':
    abstract = "/genotoxicity/ ... the present study was designed to determine genotoxic and mutagenic effects of bisphenol a (bpa) using in-vivo and in-vitro assays. the adult male and female rats were orally administered with various doses of bpa (2.4 ug, 10 ug, 5mg and 50mg/kg bw) once a day for six consecutive days. animals were sacrificed, bone marrow and blood samples were collected and subjected to series of genotoxicity assay such as micronucleus, chromosome aberration and single cell gel electrophoresis (scge) assay respectively. mutagenicity was determined using tester strains of salmonella typhimurium (ta 98, ta 100 and ta 102) in the presence and absence of metabolically active microsomal fractions (s9). further, we estimated the levels of 8-hydroxydeoxyguanosine, lipid peroxidation and glutathione activity to decipher the potential genotoxic mechanism of bpa. /the investigators/ observed that bpa exposure caused a significant increase in the frequency of micronucleus (mn) in polychromatic erythrocytes (pces), structural chromosome aberrations in bone marrow cells and dna damage in blood lymphocytes. these effects were observed at various doses tested except 2.4 ug compared to vehicle control. /the investigators/ did not observe the mutagenic response in any of the tester strains tested at different concentrations of bpa. /the investigators/ found an increase in the level of 8-hydroxydeoxyguanosine in the plasma and increase in lipid peroxidation and decrease in glutathione activity in liver of rats respectively which were exposed to bpa. in conclusion, the data obtained clearly documents that bpa is not mutagenic but exhibit genotoxic activity and oxidative stress could be one of the mechanisms leading to genetic toxicity."
    abstract1 = clean_abstract(abstract, True)
    print(abstract1)
    abstract2 = clean_abstract(abstract, False)
    print(abstract2)
