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
AOP Help Finder Software
INSERM UMR-S 1124 Team 1
jeancharles.carvaillo@inserm.fr
"""

######################################
# IMPORT
######################################

# to find packages in bin directory
import os.path
import sys
PATH = os.path.dirname(os.path.realpath(__file__))
PATH = "/".join(PATH.split("/")[0:-1])
sys.path.append(PATH + "/bin")

import aop_data_module
import argparse_module
import db_module
import parsing_module
import tm_module
from glob import glob
from os import remove
from os.path import exists
import resource
from sys import platform as _platform
from time import time

######################################
# Main()
######################################

if __name__ == "__main__":

    start_time = time()

    arguments = argparse_module.parsing_arguments()
    database = arguments[0]
    input_dir = arguments[1]
    ao_file = arguments[2]
    ctd_file = arguments[3]
    ke_file = arguments[4]
    ker_file = arguments[5]
    output_file = arguments[6]
    out_nodes_file = arguments[7]
    out_network_file = arguments[8]
    animals_file = arguments[9]
    cpus = arguments[10]
    choice = ''

    print("\n****************************************************")
    print("* INITIALIZING DISEASES AND ADVERSE OUTCOMES (AOD) *")
    print("****************************************************\n")

    if not ao_file and not ctd_file:
        AOD = aop_data_module.load_AOD_data()
    elif not ctd_file:
        AOD = aop_data_module.load_AOD_data(AO_filename=ao_file,
                                            diseases_filename='')
    elif not ao_file:
        AOD = aop_data_module.load_AOD_data(diseases_filename=ctd_file,
                                            AO_filename='')
    else:
        AOD = aop_data_module.load_AOD_data(ao_file, ctd_file)
    print('Total number of diseases: {0}'.format(len(AOD)))

    print("\n***********************************************************")
    print("* INITIALIZING KEY-EVENTS (KE) AND KE-RELATIONSHIPS (KER) *")
    print("***********************************************************\n")

    if not ke_file and not ker_file:
        KE, KER = aop_data_module.load_KEr_data()
    elif ke_file and ker_file:
        KE, KER = aop_data_module.load_KEr_data(KE_filename=ke_file,
                                                KER_filename=ker_file)
    elif ke_file:
        KE, KER = aop_data_module.load_KEr_data(KE_filename=ke_file)
    elif ker_file:
        KE, KER = aop_data_module.load_KEr_data(KER_filename=ker_file)
    print('Total number of key-events (KE): {0}\n'.format(len(KE)))
    print('Total number of KE-relationships (KER): {0}'.format(len(KER)))

    print("\n**********************************")
    print("* CREATE DATABASE AND STORE DATA *")
    print("**********************************\n")

    if exists(database):
        while choice not in ['Y', 'N']:
            choice = input("Do you want to delete the previous "
                           "database ? (Y/N) : ")
        if choice is 'Y':
            remove(database)
            db_module.create_tables(database)

    if not exists(database):
        db_module.create_tables(database)

    if (choice is 'Y' or choice is '') and not input_dir:
        if choice is '':
            remove(database)
        exit("ERROR : No input directory specified.\n"
             "\tYou should specified the directory which contains file linked "
             "\n\tto the molecule study. This is explained in the readme "
             "file.\n")

    if input_dir and choice is not 'N':
        # initialization of a list which will contains reviews data object
        data_reviews = []
        all_data_reviews = []

        for file in glob(input_dir + '/*'):
            data_reviews = parsing_module.detect_format(file)
            if len(data_reviews) > 0:
                print('Number of study: {0}'.format(len(data_reviews)))
                all_data_reviews += data_reviews
        print('\nTotal number of studies considered: {0}\n'
              .format(len(all_data_reviews)))

        db_module.to_database(all_data_reviews, database)
        if not animals_file:
            animals = aop_data_module.load_animals()
        else:
            animals = aop_data_module.load_animals(animals_file)

        print("\nFind Systems:")
        print("=============\n")

        revids_systems = db_module.multiprocess_find_systems(database,
                                                            animals,
                                                            cpus) 
        db_module.store_systems_in_db(database, revids_systems)

    print('\n\nTotal number of distinct reviews in database: {0}'
          .format(db_module.total_studies(database)))

    print("\n*****************************")
    print("* FIND DISEASES IN DATABASE *")
    print("*****************************\n")

    if choice is 'Y' or choice is '':
        revids_AODs = db_module.multiprocess_find_diseases(database,
                                                           AOD,
                                                           cpus)
        db_module.store_diseases_in_db(database, revids_AODs)
        db_module.biai_surocc_diseases(database)

    print('\nSorted by alphabetic order')
    AOD_finded = db_module.all_finded_AOD_alpha(database)
    print(AOD_finded)

    print('\nSorted by higher occurence')
    AOD_finded = db_module.all_finded_AOD_occ(database)
    print(AOD_finded)

    print('\nTotal number of different diseases: {0}'.format(len(AOD_finded)))

    # preoutput results
    total_occ_disease = 0
    filout = open(output_file, 'w')
    for disocc in AOD_finded:
        filout.write('{0}\t{1}\n'.format(disocc[0], disocc[1]))
        total_occ_disease += disocc[1]
    filout.close()

    print('Total occurence of diseases: {0}'.format(total_occ_disease))

    print("\n************************************")
    print("* FIND KEY-EVENTS (KE) IN DATABASE *")
    print("************************************\n")

    if choice is 'Y' or choice is '':
        # db_module.find_key_events(database, KE)
        revids_KEs = db_module.multiprocess_key_events(database, KE, cpus)
        db_module.store_KEs_in_db(database, revids_KEs)
        db_module.biai_surocc_key_event(database)

    print('\n\nSorted by alphabetic order')
    KE_finded = db_module.all_finded_KE_alpha(database)
    print(KE_finded)

    print('\nSorted by higher occurence')
    KE_finded = db_module.all_finded_KE_occ(database)
    print(KE_finded)

    print('\nTotal number of different key-events: {0}'.format(len(KE_finded)))

    total_occ_ke = 0
    for keocc in KE_finded:
        total_occ_ke += keocc[1]

    print('Total occurence of key-events: {0}'.format(total_occ_ke))

    print("\n**********************************")
    print("* GENERATE INPUT CYTOSCAPE FILES *")
    print("**********************************\n")

    AOD_finded = db_module.all_asso_AOD_DT(database)
    KE_finded =  db_module.all_asso_KE_DT(database)

    AOD_nodes = [[aod[0], aod[1]] for aod in AOD_finded]
    AOD_nodes = [list(aod) for aod in set(tuple(aod) for aod in AOD_nodes)]
    KE_nodes = [[ke[0], ke[1]] for ke in KE_finded]
    KE_nodes = [list(ke) for ke in set(tuple(ke) for ke in KE_nodes)]
    RE_nodes = [aod[3] for aod in AOD_finded] + [ke[3] for ke in KE_finded]
    RE_nodes = set(RE_nodes)

    filout = open(out_nodes_file, 'w')
    filout.write('node_id\tobject\n')
    for aod in AOD_nodes:
        filout.write('{0}\t{1}\n'.format('AO' + str(aod[0]), aod[1]))
    for ke in KE_nodes:
        filout.write('{0}\t{1}\n'.format('KE' + str(ke[0]), ke[1]))
    for re in RE_nodes:
        filout.write('{0}\t{1}\n'.format('RE' + str(re), re))
    filout.close()

    print('Cytoscape Data Table (Nodes) input file generated: {0}\n'
          .format(out_nodes_file))

    filout = open(out_network_file, 'w')
    filout.write('node_id\ttarget\tcategory\tweight\tsource\n')
    for aod in AOD_finded:
        filout.write('{0}\t{1}\t{2}\t{3}\t{4}\n'
                     .format('AO' + str(aod[0]), aod[1], 'AO', aod[2],
                             'RE' + str(aod[3])))
    for ke in KE_finded:
        filout.write('{0}\t{1}\t{2}\t{3}\t{4}\n'
                     .format('KE' + str(ke[0]), ke[1], 'KE', ke[2],
                             'RE' + str(ke[3])))
    filout.close()

    print('Cytoscape Network input file generated: {0}'
          .format(out_network_file))

    ressources = resource.getrusage(resource.RUSAGE_SELF)
    elapsed_time = time() - start_time
    print ("\n===============================")
    print ("User's time: {0:13.2f} sec".format(elapsed_time))
    print ("System's time: {0:11.2f} sec".format(ressources[1]))
    if _platform == "linux" or _platform == "linux2":
        print ("Maximum RAM: {0:7.2f} Mo".format(ressources[2] / 1024.0))
    elif _platform == "darwin":
        print ("Maximum RAM: {0:13.2f} Mo".format(ressources[2] / 1024.0**2))
    print ("===============================")
