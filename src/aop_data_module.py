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
AOP Data Extractor Module
INSERM UMR-S 1124 Team 1
jeancharles.carvaillo@inserm.fr
"""

######################################
# IMPORT
######################################

import os.path
PATH = os.path.dirname(os.path.realpath(__file__))
PATH = "/".join(PATH.split("/")[0:-1])

# text mining library
import tm_module

import nltk.stem
from nltk import word_tokenize

######################################
# GLOBAL VARIABLE
######################################

STOPWORDS = [' and ', ' but ', ' by ', ' down ', ' for ', ' from ', ' in ',
             ' into ', ' of ', ' on ', ' or ', ' other ', ' the ', ' to ',
             ' with ', ' without ', '\' ', '\'s ', '/', '-']


AO_FILE = PATH + '/data/AOPwiki/61-current-AO-25Aout2017.txt'
CTD_FILE = PATH + '/data/diseases/CTD_diseases-2017-09-28.tsv'
KE_FILE = PATH + '/data/AOPwiki/Key-events-25August2017.txt'
KER_FILE = PATH + '/data/AOPwiki/KE-relationships-25August2017.txt'
ANIMALS_FILE = PATH + '/data/animals/common_name.txt'

######################################
# FUNCTION
######################################


def AOD_file(filename, filetype):
    """Method to extract all diseases or adverse outcomes contain in a file.
       The file should be performed by CTD database or AOPwiki beforehand.

    Return:
        AOD (dict): a dict which contains strings corresponding to adverse
        outcomes or diseases. The keys of the dict correspond to stem of
        adverse outcomes or diseases.

    """
    AOD = {}
    f = open(filename, encoding='utf-8')
    lines = f.readlines()
    for line in lines:
        term = ''
        if filetype == 'D':
            if not line.startswith('#'):
                line = line.split('\t')[0]
            else:
                continue
        line = line.strip().lower()
        for word in STOPWORDS:
            line = line.replace(word, ' ')
        substr = line.split(',')[0]
        words = word_tokenize(line)
        words = tm_module.stem_process(words)
        stemline = ' '.join(words)
        term = stemline.split(',')[0]
        term = term.strip()
        stemline = stemline.replace(', ', ' ')
        stemline = stemline.replace(',', ' ')
        if stemline not in AOD.keys():
            AOD[stemline] = line
        if len(term.split()) > 1 and term not in AOD.keys():
            AOD[term] = substr

    f.close()
    return AOD


def AOD_merging(AO, D):
    """Method to merge two dicts in one dict with non-redundant information.

    Return:
        AOD (dict): a dict which contains strings corresponding to adverse
        outcomes and diseases. The keys of the dict correspond to stem of
        adverse outcomes or diseases.

    """
    # AOD = set(AO + D)
    AOD = {**AO, **D}
    return AOD


def load_AOD_data(AO_filename=AO_FILE, diseases_filename=CTD_FILE):
    """Method to get a dict of adverse outcomes and / or diseases in
       function of input file(s).

    Return:
        (dict): a dict which contains strings corresponding to adverse
        outcomes or diseases or both (values). The keys of the dict
        correspond to stem of adverse outcomes or diseases.

    """
    if AO_filename:
        AO = AOD_file(filename=AO_filename, filetype='AO')
    if diseases_filename:
        D = AOD_file(filename=diseases_filename, filetype='D')
    if AO_filename and diseases_filename:
        AOD = AOD_merging(AO, D)
        return AOD
    elif AO_filename:
        return AO
    elif diseases_filename:
        return D


def KEr_file(filename):
    """Method to extract key-events or key-events relationships contain in a
       file.
       The file should be performed from AOPwiki beforehand.

    Return:
        KEr (list): a list which contains lists of strings corresponding to
        key-events or key-events relationships data.

    """
    KEr = []
    f = open(filename, encoding='latin-1')
    lines = f.readlines()[1:]
    for line in lines:
        sent = line.strip().lower()
        for word in STOPWORDS:
            sent = sent.replace(word, ' ')
        sent = sent.replace(', ', ' ')
        sent = sent.replace('n a ', '')
        sent = sent.split('\t')
        if sent == ['']:
            break
        KEr.append(sent)
    f.close()
    return KEr


def load_KEr_data(KE_filename=KE_FILE, KER_filename=KER_FILE):
    """Method to get a list of key-events or key-events relationships in
       function of input file(s).

    Return:
        KE (list): a list which contains lists of strings corresponding to
        key-events data.
        KR (list): a list which contains lists of strings corresponding to
        key-events relationships data.

    """
    KE = KEr_file(KE_filename)
    KER = KEr_file(KER_filename)
    return KE, KER


def load_animals(animals_filename=ANIMALS_FILE):
    """Method to get a dict of common names of animals contributing generally
       in biology studies.

    Return:
        animals (dict): a dict which contains common names of animals
        (values). The keys of the dict correspond to stem of common names.

    """
    animals = {}
    filin = open(animals_filename, encoding='utf-8')
    species = filin.readlines()
    for common_name in species:
        animal = tm_module.clean_abstract(common_name, True)
        if animal not in animals.keys():
            animals[animal] = common_name.strip()
    return animals


######################################
# Main()
######################################

if __name__ == '__main__':
    # AOD = load_AOD_data()
    # print(AOD)
    # KE, KER = load_KEr_data()
    # for el in KE:
    #     print(el[1])
    print(load_animals())
