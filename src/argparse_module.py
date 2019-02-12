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
Arguments Parsing Module
INSERM UMR-S 1124 Team 1
jeancharles.carvaillo@inserm.fr
"""
######################################
# IMPORT
######################################

import os.path
PATH = os.path.dirname(os.path.realpath(__file__))
PATH = "/".join(PATH.split("/")[0:-1])

from sys import exit
from os.path import exists
from multiprocessing import cpu_count
import argparse

######################################
# FUNCTION
######################################


def parsing_arguments():
    """Arguments parsing.

    Returns:
        args (argparse.Namespace object): object which contains args
            specified by the user.

    Raises:
        if a file gives in argument is not openable, the software stop.

    """
    parser = argparse.ArgumentParser(usage="python3 %(prog)s [-h] [-d]" +
                                     "[database_path]\n",
                                     description="Find association in abstract\
                                     between a molecule exposure and \
                                     MIE, KE, KR, AO and Diseases \
                                     contributing to perform an AOP")

    parser.add_argument("-i", "--input",
                        help="path of the directory which contains \
                        files related to the study molecule",
                        default=False,
                        nargs=1,
                        type=str,
                        action="store")

    parser.add_argument("-d", "--database",
                        help="path or name of the database to used \
                        or to created",
                        default=False,
                        nargs=1,
                        type=str,
                        action="store",
                        required=True)

    parser.add_argument("-a", "--adverse_outcome",
                        help="path of the file which contains \
                        current adverse outcomes. This file exist on AOPwiki \
                        website. This is explained in readme file.",
                        default=False,
                        nargs=1,
                        type=str,
                        action="store")

    parser.add_argument("-c", "--ctd_file",
                        help="path of the file which contains \
                        diseases in a tsv format. This file should be \
                        performed by CTD database beforehand. This is \
                        explained in the readme file.",
                        default=False,
                        nargs=1,
                        type=str,
                        action="store")

    parser.add_argument("-k", "--ke_file",
                        help="path of the file which contains \
                        key-events in a tsv format. This file should be \
                        performed with AOPwiki beforehand. This is \
                        explained in the readme file.",
                        default=False,
                        nargs=1,
                        type=str,
                        action="store")

    parser.add_argument("-r", "--ker_file",
                        help="path of the file which contains \
                        key-events-relationships in a tsv format. This file \
                        should be performed with AOPwiki beforehand. This is \
                        explained in the readme file.",
                        default=False,
                        nargs=1,
                        type=str,
                        action="store")

    parser.add_argument("-o", "--output",
                        help="write a result file which contains \
                        adverse outcomes or diseases linked to \
                        corresponding occurence",
                        default=False,
                        nargs=1,
                        type=str,
                        action="store")

    parser.add_argument("-cdt", "--cytoscape_nodes",
                        help="write a result file which contains \
                        nodes of a cytoscape network",
                        default=False,
                        nargs=1,
                        type=str,
                        action="store")

    parser.add_argument("-cne", "--cytoscape_network",
                        help="write a result file which contains \
                        adverse outcomes, diseases or key-events linked to a \
                        specific review",
                        default=False,
                        nargs=1,
                        type=str,
                        action="store")

    parser.add_argument("-ani", "--animals",
                        help="path of the file which contains common_name of \
                        animals contributing generally in science",
                        default=False,
                        nargs=1,
                        type=str,
                        action="store")

    parser.add_argument("-cpu", "--number_of_cpu",
                        help="number of cpu to use at the execution of the \
                        software",
                        default=1,
                        nargs='?',
                        type=int)

    args = parser.parse_args()

    if not args.database:
        exit("ERROR: The database to used should be specified.\n" +
             "[cmd]: python aop_finder.py -d database_path\n" +
             "[cmd]: python aop_finder.py -h (Help display)")

    if args.input:
        if not exists(args.input[0]):
            exit("ERROR : The directory specified doesn't exist.\n")
    else:
        args.input = [""]

    if args.adverse_outcome:
        if not exists(args.adverse_outcome[0]):
            exit("ERROR: The file specified doesn't exist.\n")
    else:
        args.adverse_outcome = [""]

    if args.ctd_file:
        if not exists(args.ctd_file[0]):
            exit("ERROR: The file specified doesn't exist.\n")
    else:
        args.ctd_file = [""]

    if args.ke_file:
        if not exists(args.ke_file[0]):
            exit("ERROR: The file specified doesn't exist.\n")
    else:
        args.ke_file = [""]

    if args.ker_file:
        if not exists(args.ker_file[0]):
            exit("ERROR: The file specified doesn't exist.\n")
    else:
        args.ker_file = [""]

    if not args.output:
        args.output = [PATH + "/output/diseases_finded.tsv"]

    if not args.cytoscape_nodes:
        args.cytoscape_nodes = [PATH + "/output/cytoscape_nodes.tsv"]

    if not args.cytoscape_network:
        args.cytoscape_network = [PATH + "/output/cytoscape_network.tsv"]

    if args.animals:
        if not exists(args.animals[0]):
            exit("ERROR: The file specified doesn't exist.\n")
    else:
        args.animals = [""]

    if args.number_of_cpu > cpu_count():
        exit("ERROR:\tYou can not specified more cpu than available.\n" + 
             "\tMaximum number of cpu: {0}\n".format(cpu_count()))

    return (args.database[0], args.input[0], args.adverse_outcome[0],
            args.ctd_file[0], args.ke_file[0], args.ker_file[0],
            args.output[0], args.cytoscape_nodes[0],
            args.cytoscape_network[0], args.animals[0], args.number_of_cpu)
