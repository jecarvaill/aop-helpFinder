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
Database Module
INSERM UMR-S 1124 Team 1
jeancharles.carvaillo@inserm.fr
"""

######################################
# IMPORT
######################################

# text mining library
import tm_module

# multiprocessing library
from functools import partial
from multiprocessing import Pool, cpu_count
# progress bar
import tqdm
# graph algorithms library
import networkx as nx
# sqlite3 database library
import sqlite3

######################################
# FUNCTION
######################################


def create_tables(database_name):
    """Method to create tables of a database.

    Raises:
        if a table already exist, the software stop.

    """
    # creation of the database
    db_loc = sqlite3.connect(database_name)
    # cursor which take SQL command
    cur = db_loc.cursor()
    # creation of database source table
    cur.execute('''CREATE TABLE Db_source(
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        db_source VARCHAR(25)
                   );''')
    # creation of author table
    cur.execute('''CREATE TABLE Author(
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        author VARCHAR(50)
                   );''')
    # creation of journal table
    cur.execute('''CREATE TABLE Journal(
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        journal VARCHAR(50)
                   );''')
    # creation of reference table
    cur.execute('''CREATE TABLE Reference(
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title VARCHAR(100),
                        year INTEGER,
                        authorid INTEGER,
                        journalid INTEGER,
                        CONSTRAINT fk_authorid
                            FOREIGN KEY(authorid)
                            REFERENCES Author(id),
                        CONSTRAINT fk_journalid
                            FOREIGN KEY(journalid)
                            REFERENCES Journal(id)
                   );''')
    # creation of data text table
    cur.execute('''CREATE TABLE Data_text(
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        abstract VARCHAR(550),
                        target VARCHAR(50),
                        referenceid INTEGER,
                        CONSTRAINT fk_referenceid
                            FOREIGN KEY(referenceid)
                            REFERENCES Reference(id)

                   );''')
    # creation of effect table
    cur.execute('''CREATE TABLE Effect(
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        effect VARCHAR(50)
                   );''')
    # creation of asso_effect_data_text table
    cur.execute('''CREATE TABLE Asso_effect_data_text(
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        effectid INTEGER,
                        data_textid INTEGER,
                        CONSTRAINT fk_effectid
                            FOREIGN KEY(effectid)
                            REFERENCES Effect(id),
                        CONSTRAINT fk_data_textid
                            FOREIGN KEY(data_textid)
                            REFERENCES Data_text(id)
                   );''')
    # creation of asso_system_data_text table
    cur.execute('''CREATE TABLE Asso_system_data_text(
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        systemid INTEGER,
                        data_textid INTEGER,
                        CONSTRAINT fk_systemid
                            FOREIGN KEY(systemid)
                            REFERENCES System(id),
                        CONSTRAINT fk_data_textid
                            FOREIGN KEY(data_textid)
                            REFERENCES Data_text(id)
                   );''')
    # creation of animal table
    cur.execute('''CREATE TABLE Animal(
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        species VARCHAR(50)
                   );''')
    # creation of sex table
    cur.execute('''CREATE TABLE Sex(
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        sex VARCHAR(10)
                   );''')
    # creation of system table
    cur.execute('''CREATE TABLE System(
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        animalid INTEGER,
                        sexid INTEGER
                   );''')
    # creation of review table
    cur.execute('''CREATE TABLE Review(
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        db_sourceid INTEGER,
                        referenceid INTEGER,
                        data_textid INTEGER,
                        CONSTRAINT fk_db_sourceid
                            FOREIGN KEY(db_sourceid)
                            REFERENCES Db_source(id),
                        CONSTRAINT fk_referenceid
                            FOREIGN KEY(referenceid)
                            REFERENCES Reference(id),
                        CONSTRAINT fk_data_textid
                            FOREIGN KEY(data_textid)
                            REFERENCES Data_text(id)
                   );''')
    # creation of disease table
    cur.execute('''CREATE TABLE Disease(
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        disease VARCHAR(100),
                        occurence INTEGER DEFAULT 0
                   );''')
    # creation of asso_disease_data_text table
    cur.execute('''CREATE TABLE Asso_disease_data_text(
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        diseaseid INTEGER,
                        data_textid INTEGER,
                        last_index INTEGER DEFAULT 0,
                        weight REAL DEFAULT 0.0,
                        CONSTRAINT fk_diseaseid
                            FOREIGN KEY(diseaseid)
                            REFERENCES Disease(id),
                        CONSTRAINT fk_data_textid
                            FOREIGN KEY(data_textid)
                            REFERENCES Data_text(id)
                   );''')
    # creation of key_event table
    cur.execute('''CREATE TABLE Key_event(
                    id INTEGER PRIMARY KEY,
                    key_event VARCHAR(100),
                    occurence INTEGER DEFAULT 0
                   );''')
    # creation of asso_ke_data_text table
    cur.execute('''CREATE TABLE Asso_ke_data_text(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key_eventid INTEGER,
                    data_textid INTEGER,
                    score REAL DEFAULT 0.0,
                    CONSTRAINT fk_key_eventid
                        FOREIGN KEY(key_eventid)
                        REFERENCES Key_event(id),
                    CONSTRAINT fk_data_textid
                        FOREIGN KEY(data_textid)
                        REFERENCES Data_text(id)
                   );''')

    db_loc.commit()
    db_loc.close()


def fill_tables(data_review, cur):
    """Method to fill tables in function of data contain in a review."""
    # check if a review already exist
    if data_review.getAbstract():
        cur.execute('''SELECT id FROM Data_text WHERE abstract=:abstract;''',
                    {'abstract': data_review.getAbstract()})
        if cur.fetchone():
            return

    # fill the db_source table
    cur.execute('''SELECT id FROM Db_source WHERE db_source=:db_source;''',
                {'db_source': data_review.getDBsource()})
    db_sourceid = cur.fetchone()
    if not db_sourceid:
        cur.execute('''INSERT INTO Db_source(db_source)
                       VALUES (:db_source);
                    ''',
                    {'db_source': data_review.getDBsource()})
        cur.execute('''SELECT id FROM Db_source
                       WHERE db_source=:db_source;
                    ''',
                    {'db_source': data_review.getDBsource()})
        db_sourceid = cur.fetchone()[0]
    else:
        db_sourceid = db_sourceid[0]

    # fill the author table
    cur.execute('''SELECT id FROM Author WHERE author= :author;''',
                {'author': data_review.getAuthor()})
    authorid = cur.fetchone()
    if not authorid:
        cur.execute('''INSERT INTO Author(author) VALUES (:author);''',
                    {'author': data_review.getAuthor()})
        cur.execute('''SELECT id FROM Author WHERE author= :author;''',
                    {'author': data_review.getAuthor()})
        authorid = cur.fetchone()[0]
    else:
        authorid = authorid[0]

    # fill the journal table
    cur.execute('''SELECT id FROM Journal WHERE journal= :journal;''',
                {'journal': data_review.getJournal()})
    journalid = cur.fetchone()
    if not journalid:
        cur.execute('''INSERT INTO Journal(journal) VALUES (:journal);''',
                    {'journal': data_review.getJournal()})
        cur.execute('''SELECT id FROM Journal WHERE journal=:journal;''',
                    {'journal': data_review.getJournal()})
        journalid = cur.fetchone()[0]
    else:
        journalid = journalid[0]

    # fill the reference table
    cur.execute('''SELECT id FROM Reference
                   WHERE title = :title
                   AND year = :year
                   AND authorid = :authorid
                   AND journalid = :journalid;
                ''',
                {'title': data_review.getTitle(),
                 'year': data_review.getYear(),
                 'authorid': authorid,
                 'journalid': journalid})
    referenceid = cur.fetchone()
    if not referenceid:
        cur.execute('''INSERT INTO Reference(title, year, authorid, journalid)
                       VALUES (:title, :year, :authorid, :journalid);
                    ''',
                    {'title': data_review.getTitle(),
                     'year': data_review.getYear(),
                     'authorid': authorid,
                     'journalid': journalid})
        cur.execute('''SELECT id FROM Reference
                       WHERE title = :title
                       AND year = :year
                       AND authorid = :authorid
                       AND journalid = :journalid;
                    ''',
                    {'title': data_review.getTitle(),
                     'year': data_review.getYear(),
                     'authorid': authorid,
                     'journalid': journalid})
        referenceid = cur.fetchone()[0]
    else:
        referenceid = referenceid[0]

    # fill the data text table
    cur.execute('''SELECT id FROM Data_text
                   WHERE abstract = :abstract
                   AND target = :target
                   AND referenceid = :referenceid;
                ''',
                {'abstract': data_review.getAbstract(),
                 'target': data_review.getTarget(),
                 'referenceid': referenceid})
    data_textid = cur.fetchone()
    if not data_textid:
        cur.execute('''INSERT INTO Data_text(abstract, target, referenceid)
                       VALUES (:abstract, :target, :referenceid);
                    ''',
                    {'abstract': data_review.getAbstract(),
                     'target': data_review.getTarget(),
                     'referenceid': referenceid})
        cur.execute('''SELECT id FROM Data_text
                       WHERE abstract = :abstract
                       AND target = :target
                       AND referenceid = :referenceid;
                    ''',
                    {'abstract': data_review.getAbstract(),
                     'target': data_review.getTarget(),
                     'referenceid': referenceid})
        data_textid = cur.fetchone()[0]
    else:
        data_textid = data_textid[0]

    # fill the effect and asso_effect_data_text tables
    if data_review.getEffects():
        for effect in data_review.getEffects():
            cur.execute('''SELECT id FROM Effect WHERE effect = :effect;''',
                        {'effect': effect})
            effectid = cur.fetchone()
            if not effectid:
                cur.execute('''INSERT INTO Effect(effect) VALUES (:effect);''',
                            {'effect': effect})
                cur.execute('''SELECT id FROM Effect
                               WHERE effect = :effect;
                            ''',
                            {'effect': effect})
                effectid = cur.fetchone()[0]
            else:
                effectid = effectid[0]
            cur.execute('''SELECT id FROM Asso_effect_data_text
                           WHERE effectid = :effectid
                           AND data_textid = :data_textid;
                           ''',
                        {'effectid': effectid, 'data_textid': data_textid})
            aedtid = cur.fetchone()
            if not aedtid:
                cur.execute('''INSERT INTO
                               Asso_effect_data_text(data_textid, effectid)
                               VALUES (:data_textid, :effectid);
                            ''',
                            {'data_textid': data_textid,
                             'effectid': effectid})

    # fill the table animal
    if data_review.getSpecies():
        cur.execute('''SELECT id FROM Animal WHERE species = :species;''',
                    {'species': data_review.getSpecies()})
        animalid = cur.fetchone()
        if not animalid:
            cur.execute('''INSERT INTO Animal(species) VALUES (:species);''',
                        {'species': data_review.getSpecies()})
            cur.execute('''SELECT id FROM Animal WHERE species = :species;''',
                        {'species': data_review.getSpecies()})
            animalid = cur.fetchone()[0]
        else:
            animalid = animalid[0]

    # fill the table sex species
    cur.execute('''SELECT id FROM Sex WHERE sex = :sex;''',
                {'sex': data_review.getSex()})
    sexid = cur.fetchone()
    if not sexid:
        cur.execute('''INSERT INTO Sex(sex) VALUES (:sex);''',
                    {'sex': data_review.getSex()})
        cur.execute('''SELECT id FROM Sex WHERE sex = :sex;''',
                    {'sex': data_review.getSex()})
        sexid = cur.fetchone()[0]
    else:
        sexid = sexid[0]

    # fill the table system
    if data_review.getSpecies():
        cur.execute('''SELECT id FROM System
                       WHERE animalid = :animalid
                       AND sexid = :sexid;
                    ''',
                    {'animalid': animalid,
                     'sexid': sexid})
        systemid = cur.fetchone()
        if not systemid:
            cur.execute('''INSERT INTO System(animalid, sexid)
                           VALUES (:animalid, :sexid);
                        ''',
                        {'animalid': animalid,
                         'sexid': sexid})
            cur.execute('''SELECT id FROM System
                           WHERE animalid = :animalid
                           AND sexid = :sexid;
                        ''',
                        {'animalid': animalid,
                         'sexid': sexid})
            systemid = cur.fetchone()[0]
        else:
            systemid = systemid[0]

        # fill the table asso_system_data_text
        cur.execute('''SELECT id FROM Asso_system_data_text ASDT
                       WHERE ASDT.systemid = :systemid
                       AND ASDT.data_textid = :data_textid;
                    ''',
                    {'systemid': systemid,
                     'data_textid': data_textid})
        asdtid = cur.fetchone()
        if not asdtid:
            cur.execute('''INSERT INTO
                           Asso_system_data_text(systemid, data_textid)
                           VALUES (:systemid, :data_textid);
                        ''',
                        {'systemid': systemid,
                         'data_textid': data_textid})

    # fill the table review
    cur.execute('''SELECT id FROM Review
                   WHERE referenceid = :referenceid
                   AND data_textid = :data_textid;
                ''',
                {'referenceid': referenceid,
                 'data_textid': data_textid})
    reviewid = cur.fetchone()
    if not reviewid:
        cur.execute('''INSERT INTO
                       Review(db_sourceid, referenceid, data_textid)
                       VALUES (:db_sourceid, :referenceid, :data_textid);
                    ''',
                    {'db_sourceid': db_sourceid,
                     'referenceid': referenceid,
                     'data_textid': data_textid})


def to_database(data_reviews, database_name):
    """Method to fill database with all data extracted from reviews."""
    # open the database
    db_loc = sqlite3.connect(database_name)
    # cursor which take SQL command
    cur = db_loc.cursor()

    for data_review in tqdm.tqdm(data_reviews):
        fill_tables(data_review, cur)

    db_loc.commit()
    db_loc.close()


def total_studies(database_name):
    """Method to count the total number of review in a database.

    Return:
        total (int): an int corresponding to the total number of review
        contained in a database.

    """
    # open the database
    db_loc = sqlite3.connect(database_name)
    # cursor which take SQL command
    cur = db_loc.cursor()

    cur.execute('''SELECT COUNT(*) FROM Review;''')
    total = cur.fetchone()[0]

    db_loc.commit()
    db_loc.close()

    return total


def multiprocess_find_systems(database_name, species, cpus):
    """Method to distribute systems finding amongst several processors.

    Return:
        threads (list): a list which contains every dictionaries of all 
        systems linked with a data_text id.

    """
    if cpus > cpu_count():
        cpus = cpu_count()

    # open the database
    db_loc = sqlite3.connect(database_name)
    # cursor which take SQL command
    cur = db_loc.cursor()

    cur.execute('''SELECT id FROM Data_text;''')
    data_textids = cur.fetchall()
    dt_ids = [data_textid[0] for data_textid in data_textids]

    db_loc.commit()
    db_loc.close()

    pool = Pool(cpus)
    threads = []
    # to associate variables to a function
    with tqdm.tqdm(total=len(data_textids)) as pbar:
        func = partial(find_systems, [database_name, species])
        for i, thr in tqdm.tqdm(enumerate(pool.imap_unordered(func, dt_ids))):
            pbar.update()
            threads.append(thr)

    pbar.close()
    pool.close()
    pool.join()

    return threads


def find_systems(args, data_textid):
    """Method to find biological systems in an abstract.

    Return:
        revid_systems (dict): a dictionary which contains all systems
        associated to a specific data_text id.

    """
    database_name = args[0]
    species = args[1]
    # initialization of storing dictionary
    revid_systems = {}
    all_systems = {}
    # open the database
    db_loc = sqlite3.connect(database_name)
    # cursor which take SQL command
    cur = db_loc.cursor()

    cur.execute('''SELECT abstract FROM Data_text
                   WHERE id = :id;
                ''',
                {'id': data_textid})
    abstract = cur.fetchone()[0]

    db_loc.commit()
    db_loc.close()

    if abstract:
        # text mining process
        abstract = tm_module.clean_abstract(abstract, True)

        # system process
        sex = find_sex(abstract)
        for common_name in species.keys():
            # to search a match of an animal in the species list
            animal = find_animal(abstract, common_name)
            if animal not in ['human', '']:
                # to store a new system in all_systems dictionary
                all_systems = store_system(all_systems, species[animal], sex)
            else:
                # to store a new system in all_systems dictionary
                all_systems = store_system(all_systems, animal, sex)

    if all_systems:
        revid_systems[data_textid] = all_systems
        return revid_systems


def store_system(all_systems, species, sex):
    """Method to store a system in a dictionary.

    Return:
        all_systems (dict): a dictionary which contains multiple data text id
        associated to multiple systems.

    """
    if species not in all_systems.keys():
        all_systems[species] = {'sex': sex}

    return all_systems


def store_systems_in_db(database_name, revids_systems):
    """Method to store all systems in a database."""
    # open the database
    db_loc = sqlite3.connect(database_name)
    # cursor which take SQL command
    cur = db_loc.cursor()

    for revid_systems in revids_systems:
        if revid_systems:
            data_textid = list(revid_systems.keys())[0]
            all_systems = revid_systems[data_textid]
            for species in all_systems.keys():
                make_system_association(cur, data_textid, species,
                                        all_systems[species]['sex'])

    db_loc.commit()
    db_loc.close()


def make_system_association(cur, data_textid, species, sex):
    """Method to make the association between tables related to an in vivo
       system.

    """
    cur.execute('''SELECT id FROM Animal WHERE species = :species;''',
                {'species': species})
    animalid = cur.fetchone()
    if not animalid:
        cur.execute('''INSERT INTO Animal(species) VALUES(:species);''',
                    {'species': species})
        cur.execute('''SELECT id FROM Animal WHERE species = :species;''',
                    {'species': species})
        animalid = cur.fetchone()[0]
    else:
        animalid = animalid[0]

    cur.execute('''SELECT id FROM Sex WHERE sex = :sex;''',
                {'sex': sex})
    sexid = cur.fetchone()
    if not sexid:
        cur.execute('''INSERT INTO Sex(sex) VALUES(:sex);''',
                    {'sex': sex})
        cur.execute('''SELECT id FROM Sex WHERE sex = :sex;''',
                    {'sex': sex})
        sexid = cur.fetchone()[0]
    else:
        sexid = sexid[0]

    cur.execute('''SELECT id FROM System
                   WHERE animalid = :animalid
                   AND sexid = :sexid;
                ''',
                {'animalid': animalid,
                 'sexid': sexid})
    systemid = cur.fetchone()
    if not systemid:
        cur.execute('''INSERT INTO System(animalid, sexid)
                       VALUES(:animalid, :sexid);
                    ''',
                    {'animalid': animalid,
                     'sexid': sexid})
        cur.execute('''SELECT id FROM System
                       WHERE animalid = :animalid
                       AND sexid = :sexid;
                    ''',
                    {'animalid': animalid,
                     'sexid': sexid})
        systemid = cur.fetchone()[0]
    else:
        systemid = systemid[0]

    cur.execute('''SELECT id FROM Asso_system_data_text ASDT
                   WHERE systemid = :systemid
                   AND data_textid = :data_textid;
                ''',
                {'systemid': systemid,
                 'data_textid': data_textid})
    asdtid = cur.fetchone()
    if not asdtid:
        cur.execute('''INSERT INTO
                       Asso_system_data_text(systemid, data_textid)
                       VALUES (:systemid, :data_textid);
                    ''',
                    {'systemid': systemid,
                     'data_textid': data_textid})


def find_sex(abstract):
    """Method to find sex of biological systems in an abstract.

    Return:
        (str): a string corresponding to a sex. a void string if nothing is
        found in an abstract.

    """
    # synonyms of human sex description
    males = ['boy', 'man', 'men', 'male']
    females = ['girl', 'woman', 'women', 'femal']
    # initialization of booleans
    bool_male = False
    bool_female = False

    # find a male in an abstract
    for male in males:
        if abstract.startswith(male + " "):
            bool_male = True
        elif abstract.endswith(" " + male):
            bool_male = True
        elif " " + male + " " in abstract:
            bool_male = True

    # find a female in an abstract
    for female in females:
        if abstract.startswith(female + " "):
            bool_female = True
        elif abstract.endswith(" " + female):
            bool_female = True
        elif " " + female + " " in abstract:
            bool_female = True

    if bool_male and bool_female:
        return 'both'
    elif bool_male:
        return 'male'
    elif bool_female:
        return 'female'
    return ''


def find_animal(abstract, species):
    """Method to find animal test species in an abstract.

    Return:
        (str): a string corresponding to a species. a void string if nothing is
        found in an abstract.

    """
    # synonyms of human description
    human = ['boy', 'man', 'men', 'girl', 'woman', 'women', 'adolesc',
             'child', 'children']

    # find a species in an abstract which is not human
    if species not in human:
        if abstract.startswith(species + " "):
            return species
        elif abstract.endswith(" " + species):
            return species
        elif " " + species + " " in abstract:
            return species

    # find a human
    if species in human:
        if abstract.startswith(species + " "):
            return 'human'
        elif abstract.endswith(" " + species):
            return 'human'
        elif " " + species + " " in abstract:
            return 'human'
    return ''


def make_disease_association(cur, data_textid, disease, index, len_abstract):
    """Method to make the association between tables related to a disease."""
    cur.execute('''SELECT id FROM Disease WHERE disease = :disease;''',
                {'disease': disease})
    diseaseid = cur.fetchone()

    if not diseaseid:
        cur.execute('''INSERT INTO Disease(disease) VALUES(:disease);''',
                    {'disease': disease})
        cur.execute('''SELECT id FROM Disease WHERE disease = :disease;''',
                    {'disease': disease})
        diseaseid = cur.fetchone()[0]
    else:
        diseaseid = diseaseid[0]

    cur.execute('''SELECT id FROM Asso_disease_data_text
                   WHERE diseaseid = :diseaseid
                   AND data_textid = :data_textid;
                ''',
                {'diseaseid': diseaseid, 'data_textid': data_textid})
    already_exist = cur.fetchone()

    if not already_exist:
        cur.execute('''UPDATE Disease SET occurence = occurence + 1
                       WHERE id = :diseaseid;
                    ''',
                    {'diseaseid': diseaseid})
        if index:
            weight = index / len_abstract

        elif index == 0:
            weight = 1.00

        cur.execute('''INSERT INTO
                       Asso_disease_data_text(diseaseid, data_textid,
                                              last_index, weight)
                       VALUES(:diseaseid, :data_textid, :last_index,
                              :weight);
                    ''',
                    {'diseaseid': diseaseid,
                     'data_textid': data_textid,
                     'last_index': index,
                     'weight': weight})


def multiprocess_find_diseases(database_name, AOD, cpus):
    """Method to distribute diseases and adverse outcomes finding amongst
        several processors.

    Return:
        threads (list): a list which contains every dictionaries of all 
        diseases and adverse outcomes linked with a data_text id.

    """
    if cpus > cpu_count():
        cpus = cpu_count()

    # open the database
    db_loc = sqlite3.connect(database_name)
    # cursor which take SQL command
    cur = db_loc.cursor()

    cur.execute('''SELECT id FROM Data_text;''')
    data_textids = cur.fetchall()
    dt_ids = [data_textid[0] for data_textid in data_textids]

    db_loc.commit()
    db_loc.close()

    pool = Pool(cpus)
    threads = []
    # to associate variables to a function
    with tqdm.tqdm(total=len(data_textids)) as pbar:
        func = partial(find_diseases, [database_name, AOD])
        for i, thr in tqdm.tqdm(enumerate(pool.imap_unordered(func, dt_ids))):
            pbar.update()
            threads.append(thr)

    pbar.close()
    pool.close()
    pool.join()

    return threads


def find_diseases(args, data_textid):
    """Method to find diseases and their index in a text."""
    database_name = args[0]
    AOD = args[1]
    # initialization of storing dictionary
    revid_AODs = {}
    all_AODs = {}
    # open the database
    db_loc = sqlite3.connect(database_name)
    # cursor which take SQL command
    cur = db_loc.cursor()

    cur.execute('''SELECT abstract, target FROM Data_text
                   WHERE id = :id;
                ''',
                {'id': data_textid})
    data = cur.fetchall()
    abstract = data[0][0]
    target = data[0][1]
    if abstract:
        # text mining process
        abstract = tm_module.clean_abstract(abstract, True)
        len_abstract = len(abstract)

        # AOD process
        for disease in AOD.keys():
            if abstract.startswith(disease + " "):
                index = abstract.rfind(disease + " ") + 1
                # to store a key-event in all_AODs dictionary
                all_AODs = store_disease(all_AODs, AOD[disease], index,
                                         len_abstract)

            elif abstract.endswith(" " + disease):
                index = abstract.rfind(" " + disease) + 1
                # to store a key-event in all_AODs dictionary
                all_AODs = store_disease(all_AODs, AOD[disease], index,
                                         len_abstract)

            elif " " + disease + " " in abstract:
                index = abstract.rfind(" " + disease + " ") + 1
                # to store a key-event in all_AODs dictionary
                all_AODs = store_disease(all_AODs, AOD[disease], index,
                                         len_abstract)

    elif target:
        # stemming process
        target = tm_module.stem_process(target.split())
        # AOD process
        for disease in AOD.keys():
            if disease in target:
                index = 0
                len_abstract = 0
                # to store a key-event in all_AODs dictionary
                all_AODs = store_disease(all_AODs, AOD[disease], index,
                                         len_abstract)

    else:
        # AOD process
        cur.execute('''SELECT effectid FROM Asso_effect_data_text AEDT
                       WHERE AEDT.data_textid = :data_textid;
                    ''',
                    {'data_textid': data_textid})
        effectids = cur.fetchall()
        for effectid in effectids:
            cur.execute('''SELECT effect FROM Effect
                           WHERE id = :effectid;
                        ''',
                        {'effectid': effectid[0]})
            effect = cur.fetchone()[0]
            # stemming process
            effect = tm_module.stem_process(effect.split())
            for disease in AOD.keys():
                if disease in effect:
                    index = 0
                    len_abstract = 0
                    # to store a key-event in all_AODs dictionary
                    all_AODs = store_disease(all_AODs, AOD[disease], index,
                                             len_abstract)

    db_loc.commit()
    db_loc.close()

    if all_AODs:
        revid_AODs[data_textid] = all_AODs
        return revid_AODs


def store_disease(all_AODs, AOD_name, index, len_abstract):
    """Method to store a disease or an adverse outcome and an associated index
        and len_abstract in a dictionary.

    Return:
        all_AODs (dict): a dictionary which contains multiple data text id
        associated to multiple adverse outcomes or diseases.

    """
    if AOD_name not in all_AODs.keys():
        all_AODs[AOD_name] = {'index': index, 'len_abstract': len_abstract}

    return all_AODs


def store_diseases_in_db(database_name, revids_AODs):
    """Method to store all adverse outcomes and diseases in a database."""
    # open the database
    db_loc = sqlite3.connect(database_name)
    # cursor which take SQL command
    cur = db_loc.cursor()

    for revid_AODs in revids_AODs:
        if revid_AODs:
            data_textid = list(revid_AODs.keys())[0]
            all_AODs = revid_AODs[data_textid]
            for AOD_name in all_AODs.keys():
                make_disease_association(cur, data_textid, AOD_name,
                                         all_AODs[AOD_name]['index'],
                                         all_AODs[AOD_name]['len_abstract'])

    db_loc.commit()
    db_loc.close()


def key_event_process(tokens, words):
    """Method to compute the plausibility of a key-event.
        This method is based on a dijkstra graph's computing and on the
        shortest path's finding.
        This graph modelize the position of words in a key-event relative to
        each other.

    Return:
        best (float): a float which contains the best score for a key-event.

    """
    # initialization of variables to compute the plausibility of a KE
    index = {}
    cpt = 0
    best = 0.0

    for token in tokens:
        if token in words:
            # to count the number of token found in an abstract
            cpt += 1
            # to save the position of a token in an abstract
            index[token] = [pos + 1 for pos, value in enumerate(words)
                            if value == token]

    # process to compute plausibility on a KE characterized by 70% of token
    proportion = cpt / len(tokens)
    if 0.75 <= proportion and len(tokens) != 1:

        # find the nearest index between words
        values = index.values()
        values = [sorted(value) for value in values]
        values = sorted(values, key=lambda k: k[-1])

        # declaration of a graph
        G = nx.Graph()

        # to compute all edges and nodes of the dijkstra graph
        for i in range(len(values) - 1):
            for j in range(len(values[i])):
                for l in range(len(values[i + 1])):

                    G.add_edge(values[i][j], values[i + 1][l],
                               weight=abs(values[i + 1][l] - values[i][j]))

        # to compute all possible shortest paths
        shortest_paths = {}
        for start in values[0]:
            for end in values[-1]:

                shortest_path = nx.dijkstra_path(G, start, end)
                tot_weight = nx.dijkstra_path_length(G, start, end)

                shortest_paths[tot_weight + 1] = shortest_path

        # to keep the best shortest path
        best = min(shortest_paths, key=shortest_paths.get)

    # exception for target and effect token
    elif proportion == 1.0 and len(tokens) == 1:
        best = 1.0

    if proportion < 1.0:
        best = -best

    return best


def make_KE_association(cur, data_textid, KE_id, KE_name, score):
    """Method to make the association between tables related to a key-event."""
    cur.execute('''SELECT id FROM Key_event WHERE id = :id;''',
                {'id': KE_id})
    key_eventid = cur.fetchone()

    if not key_eventid:
            cur.execute('''INSERT INTO Key_event(id, key_event)
                           VALUES(:id, :key_event);''',
                        {'id': KE_id,
                         'key_event': KE_name})

    cur.execute('''UPDATE Key_event SET occurence = occurence + 1
                   WHERE id = :key_eventid;
                ''',
                {'key_eventid': KE_id})

    cur.execute('''INSERT INTO
                   Asso_ke_data_text(key_eventid, data_textid, score)
                   VALUES(:key_eventid, :data_textid, :score);
                ''',
                {'key_eventid': KE_id,
                 'data_textid': data_textid,
                 'score': score})


def store_key_event(all_KEs, KE_id, KE_name, score):
    """Method to store a key-event and an associated score in a dictionary.
        The score is overwrite if a better score is found.

    Return:
        all_KEs (dict): a dictionary which contains multiple data text id
        associated to multiple key-events.

    """
    if KE_id not in all_KEs.keys():
        all_KEs[KE_id] = {'name': KE_name, 'score': score}

    # to compare two scores related to a same key-event
    else:
        score2 = all_KEs[KE_id]['score']
        # the best score is 1.0
        if 0 < abs(1 - score) < abs(1 - score2):
            all_KEs[KE_id]['score'] = score

    return all_KEs


def store_KEs_in_db(database_name, revids_KEs):
    """Method to store all key-events in a database."""
    # open the database
    db_loc = sqlite3.connect(database_name)
    # cursor which take SQL command
    cur = db_loc.cursor()

    for revid_KEs in revids_KEs:
        if revid_KEs:
            data_textid = list(revid_KEs.keys())[0]
            all_KEs = revid_KEs[data_textid]
            for KE_id in all_KEs.keys():
                make_KE_association(cur, data_textid, KE_id,
                                    all_KEs[KE_id]['name'],
                                    all_KEs[KE_id]['score'])

    db_loc.commit()
    db_loc.close()


def multiprocess_key_events(database_name, KE, cpus):
    """Method to distribute key-events finding amongst several processors.

    Return:
        threads (list): a list which contains every dictionaries of all 
        key-events linked with a data_text id.

    """
    if cpus > cpu_count():
        cpus = cpu_count()

    # open the database
    db_loc = sqlite3.connect(database_name)
    # cursor which take SQL command
    cur = db_loc.cursor()

    cur.execute('''SELECT id FROM Data_text;''')
    data_textids = cur.fetchall()
    dt_ids = [data_textid[0] for data_textid in data_textids]

    db_loc.commit()
    db_loc.close()

    pool = Pool(cpus)
    threads = []
    # to associate variables to a function
    with tqdm.tqdm(total=len(data_textids)) as pbar:
        func = partial(find_key_events, [database_name, KE])
        for i, thr in tqdm.tqdm(enumerate(pool.imap_unordered(func, dt_ids))):
            pbar.update()
            threads.append(thr)

    pbar.close()
    pool.close()
    pool.join()

    return threads


def find_key_events(args, data_textid):
    """Method to find key-events in an abstract.

    Return:
        revid_KEs (dict): a dictionary which contains all key-events
        associated to a specific data_text id.

    """
    database_name = args[0]
    KE = args[1]
    # initialization of storing dictionary
    revid_KEs = {}
    all_KEs = {}
    # open the database
    db_loc = sqlite3.connect(database_name)
    # cursor which take SQL command
    cur = db_loc.cursor()

    cur.execute('''SELECT abstract, target FROM Data_text
                   WHERE id = :id;
                ''',
                {'id': data_textid})
    data = cur.fetchall()
    abstract = data[0][0]
    target = data[0][1]

    if abstract:
        # text mining process
        abstract = tm_module.clean_abstract(abstract, False)

        # KE process
        for key_event in KE:
            # text mining process
            tokens = tm_module.clean_abstract(key_event[1], True)
            tokens = list(set(tokens.split()))

            if not tokens:
                continue

            # to split words of a sentence in an abstract
            for i in range(len(abstract)):
                words = abstract[i].split()
                # to compute the plausability score of a key-event
                best = key_event_process(tokens, words)

                # to store a key-event in all_KEs dictionary
                if best:
                    score = best / len(tokens)
                    all_KEs = store_key_event(all_KEs, key_event[0],
                                              key_event[1], score)

    elif target:
        # text mining process
        target = tm_module.clean_abstract(target, True)
        words = target.split()

        # KE process
        for key_event in KE:
            # text mining process
            tokens = tm_module.clean_abstract(key_event[1], True)
            tokens = list(set(tokens.split()))

            if not tokens:
                continue

            # to compute the plausability score of a key-event
            best = key_event_process(tokens, words)

            # to store a key-event in all_KEs dictionary
            if best:
                score = best / len(tokens)
                all_KEs = store_key_event(all_KEs, key_event[0], key_event[1],
                                          score)

    else:
        cur.execute('''SELECT effectid FROM Asso_effect_data_text AEDT
                       WHERE AEDT.data_textid = :data_textid;
                    ''',
                    {'data_textid': data_textid})
        effectids = cur.fetchall()
        for effectid in effectids:
            cur.execute('''SELECT effect FROM Effect
                           WHERE id = :effectid;
                        ''',
                        {'effectid': effectid[0]})
            effect = cur.fetchone()[0]
            # text mining process
            effect = tm_module.clean_abstract(effect, True)
            words = effect.split()

            # KE process
            for key_event in KE:
                tokens = tm_module.clean_abstract(key_event[1], True)
                tokens = list(set(tokens.split()))

                if not tokens:
                    continue

                # to compute the plausability score of a key-event
                best = key_event_process(tokens, words)

                # to store a key-event in all_KEs dictionary
                if best:
                    score = best / len(tokens)
                    all_KEs = store_key_event(all_KEs, key_event[0],
                                              key_event[1], score)

    db_loc.commit()
    db_loc.close()

    if all_KEs:
        revid_KEs[data_textid] = all_KEs
        return revid_KEs


def biai_surocc_diseases(database_name):
    """Method to supress the suroccurence of diseases in database."""
    # open the database
    db_loc = sqlite3.connect(database_name)
    # cursor which take SQL command
    cur = db_loc.cursor()

    cur.execute('''SELECT id, disease, occurence from Disease;''')
    diseases = cur.fetchall()
    for i in range(len(diseases)-1):
        for j in range(i+1, len(diseases)):
            if diseases[i][1] in diseases[j][1]:
                cur.execute('''UPDATE Disease
                               SET occurence = occurence - :occurence
                               WHERE id = :diseaseid;
                            ''',
                            {'diseaseid': diseases[i][0],
                             'occurence': diseases[j][2]})
    db_loc.commit()
    db_loc.close()


def biai_surocc_key_event(database_name):
    """Method to supress the suroccurence of key-events in database."""
    # open the database
    db_loc = sqlite3.connect(database_name)
    # cursor which take SQL command
    cur = db_loc.cursor()

    cur.execute('''SELECT id, key_event, occurence from Key_event;''')
    key_events = cur.fetchall()
    for i in range(len(key_events)-1):
        for j in range(i+1, len(key_events)):
            if key_events[i][1] in key_events[j][1]:
                cur.execute('''UPDATE Key_event
                               SET occurence = occurence - :occurence
                               WHERE id = :key_eventid;
                            ''',
                            {'key_eventid': key_events[i][0],
                             'occurence': key_events[j][2]})
    db_loc.commit()
    db_loc.close()


def all_finded_AOD_alpha(database_name):
    """Method to get all diseases sorted by alphabetic order.

    Return:
        all_AOD (list): a list which contains tuples of all adverse outcomes or
        diseases characterized by a name and an occurence.

    """
    # open the database
    db_loc = sqlite3.connect(database_name)
    # cursor which take SQL command
    cur = db_loc.cursor()

    cur.execute('''SELECT disease, occurence FROM Disease
                   WHERE occurence > 0 ORDER BY disease;
                ''')
    all_AOD = cur.fetchall()

    db_loc.commit()
    db_loc.close()

    return all_AOD


def all_finded_AOD_occ(database_name):
    """Method to get all diseases sorted by descending order of occurence.

    Return:
        all_AOD (list): a list which contains tuples of all adverse outcomes or
        diseases characterized by a name and an occurence.

    """
    # open the database
    db_loc = sqlite3.connect(database_name)
    # cursor which take SQL command
    cur = db_loc.cursor()

    cur.execute('''SELECT disease, occurence FROM Disease
                   WHERE occurence > 0 ORDER BY occurence DESC;
                ''')
    all_AOD = cur.fetchall()

    db_loc.commit()
    db_loc.close()

    return all_AOD


def all_finded_KE_alpha(database_name):
    """Method to get all key-events sorted by alphabetic order.

    Return:
        all_KE (list): a list which contains tuples of all key-events
        characterized by a name and an occurence.

    """
    # open the database
    db_loc = sqlite3.connect(database_name)
    # cursor which take SQL command
    cur = db_loc.cursor()

    cur.execute('''SELECT key_event, occurence FROM Key_event
                   WHERE occurence > 0 ORDER BY key_event;
                ''')
    all_KE = cur.fetchall()

    db_loc.commit()
    db_loc.close()

    return all_KE


def all_finded_KE_occ(database_name):
    """Method to get all key-events sorted by descending order of occurence.

    Return:
        all_KE (list): a list which contains tuples of all key-events
        characterized by a name and an occurence.

    """
    # open the database
    db_loc = sqlite3.connect(database_name)
    # cursor which take SQL command
    cur = db_loc.cursor()

    cur.execute('''SELECT key_event, occurence FROM Key_event
                   WHERE occurence > 0 ORDER BY occurence DESC;
                ''')
    all_KE = cur.fetchall()

    db_loc.commit()
    db_loc.close()

    return all_KE


def all_asso_AOD_DT(database_name):
    """Method to get all diseases associated to normalized position and
       review.

    Return:
        all_AOD (list): a list which contains tuples of all adverse outcomes or
        diseases characterized by an id, a name, a weight and a data_text id.

    """
    # open the database
    db_loc = sqlite3.connect(database_name)
    # cursor which take SQL command
    cur = db_loc.cursor()

    cur.execute('''SELECT Disease.id, disease, weight, data_textid
                   FROM Disease, Asso_disease_data_text ADDT
                   WHERE Disease.id = ADDT.diseaseid;
                ''')
    all_AOD = cur.fetchall()

    db_loc.commit()
    db_loc.close()

    return all_AOD


def all_asso_KE_DT(database_name):
    """Method to get all key-events associated to score and review.

    Return:
        all_KE (list): a list which contains tuples of all key-events
        characterized by an id, a name, a score and a data_text id.

    """
    # open the database
    db_loc = sqlite3.connect(database_name)
    # cursor which take SQL command
    cur = db_loc.cursor()

    cur.execute('''SELECT Key_event.id, key_event, score, data_textid
                   FROM Key_event, Asso_ke_data_text AKDT
                   WHERE Key_event.id = AKDT.key_eventid;
                ''')
    all_KE = cur.fetchall()

    db_loc.commit()
    db_loc.close()

    return all_KE


######################################
# Main()
######################################
if __name__ == "__main__":
    # find_diseases("./database/bisphenol.db")
    print(all_finded_AOD_alpha('./database/bisphenol.db'))
    print(all_finded_AOD_occ('./database/bisphenol.db'))
