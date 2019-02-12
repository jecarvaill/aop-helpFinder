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
Parsing Module
INSERM UMR-S 1124 Team 1
jeancharles.carvaillo@inserm.fr
"""

######################################
# IMPORT
######################################

import html
import os.path
import re
import string

# PDF text extractions packages
from io import StringIO, BytesIO
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage

######################################
# CLASS
######################################


class DataReview():
    """This class defines an uniformized review with:

    - (str) name of source database
    - (str) first author
    - (str) name of journal
    - (str) title
    - (int) publication year
    - (str) abstract
    - (str) target of the study
    - (list - str) effects caused by the molecule
    - (str) species
    - (str) sex species

    """

    def __init__(self):
        """Constructor of the class."""
        self._db_source = ''
        self._author = ''
        self._journal = ''
        self._title = ''
        self._year = ''
        self._abstract = ''
        self._target = ''
        self._effects = []
        self._species = ''
        self._sex = ''

    def getDBsource(self):
        """Return a copy of database source of the review set."""
        if self._db_source is not None:
            return self._db_source

    def setDBsource(self, db_source):
        """Set database source of the review."""
        self._db_source = db_source

    def getAuthor(self):
        """Return a copy of first author of the review set."""
        if self._author is not None:
            return self._author

    def setAuthor(self, author):
        """Set first author of the review."""
        self._author = author

    def getJournal(self):
        """Return a copy of journal name of the review set."""
        if self._journal is not None:
            return self._journal

    def setJournal(self, journal):
        """Set journal name of the review."""
        self._journal = journal

    def getTitle(self):
        """Return a copy of title of the review set."""
        if self._title is not None:
            return self._title

    def setTitle(self, title):
        """Set title of the review."""
        self._title = title

    def getYear(self):
        """Return a copy of publication year of the review set."""
        return self._year

    def setYear(self, year):
        """Set publication year of the review."""
        self._year = year

    def getAbstract(self):
        """Return a copy of abstract in the review set."""
        if self._abstract is not None:
            return self._abstract

    def setAbstract(self, abstract):
        """Set abstract of the review."""
        self._abstract = abstract

    def getTarget(self):
        """Return a copy of target in the review set."""
        if self._target is not None:
            return self._target

    def setTarget(self, target):
        """Set target of the review."""
        self._target = target

    def getEffects(self):
        """Return a copy of effects in the review set."""
        if self._effects:
            return self._effects

    def setEffects(self, effects):
        """Set effects of the review."""
        self._effects = effects

    def getSpecies(self):
        """Return a copy of species in the review set."""
        if self._species is not None:
            return self._species

    def setSpecies(self, species):
        """Set species of the review."""
        self._species = species

    def getSex(self):
        """Return a copy of sex species in the review set."""
        if self._sex is not None:
            return self._sex

    def setSex(self, sex):
        """Set sex species of the review."""
        self._sex = sex

######################################
# FUNCTION
######################################


def cleanPDF(lines):
    """Method to clean a list which contains string not exploitable.

    Return:
        clean_lines (list): a list which contains strings
        considered like exploitable (useful for a study).

    """
    clean_lines = []
    lines = [line for line in lines if line.strip()]
    # list of stop_words contains in a line to delete
    stop_words = ['sur', 'à']
    # tuple of prefixes in a line to delete
    bad_starts = ('http', '\x0c', '•', '©')
    for line in lines:
        if not line.startswith(bad_starts):
            if not any(stop_word in line for stop_word in stop_words):
                clean_lines.append(line)
    return clean_lines


def CCRIS_extraction(lines):
    """Method to extract data of CCRIS database file.

    Returns:
        data_reviews (list): list which contains all data of review parsed.
        This list correspond to a list of instance of DataReview object.

    """
    print('CCRIS_format detected')
    i = 0
    year = 0
    reference = ""
    data_reviews = []
    # words in the next line which indicate the end of line (EOL)
    EOL = ['CARCINOGEN', 'PROMOTER', 'RESULTS', 'ROUTE', 'TARGET', 'TUMOR']
    # list of char or string to delete
    bad_words = ['<NOINDEX>', '</NOINDEX>', '[', ']']
    while i < len(lines):

        # new study detected
        if lines[i].endswith('STUDIES:'):
            # creation of a new object associated to a study
            data_review = DataReview()
            data_review.setDBsource('CCRIS')

        # species process
        if lines[i].startswith('SPECIES'):
            species = lines[i].split(':')[1].strip().lower()
            # set the species in DataReview object
            data_review.setSpecies(species)

        # test_system process
        if lines[i].startswith('TEST SYSTEM'):
            test_system = lines[i].split(':')[1].strip().lower()

        # route process
        if lines[i].startswith('ROUTE'):
            route = lines[i].split(':')[1].strip().lower()

        # strain/sex process
        if lines[i].startswith('STRAIN/SEX'):
            strain_sex = lines[i].lower()
            strain_sex = strain_sex.split(':')[1].strip()
            if strain_sex == '':
                strain_sex = lines[i+1].lower()
            strain_sex = strain_sex.split('/')
            if len(strain_sex) > 1:
                sex = strain_sex[1]
                if len(sex.split(',')) > 1:
                    sex = 'both'
                elif len(sex.split(' ')) > 1:
                    sex = sex.split(' ')[0]
                strain = strain_sex[0]
            # set the sex species in DataReview object
            data_review.setSex(sex)

        # strain indicator process
        if lines[i].startswith('STRAIN INDICATOR'):
            strain_indicator = lines[i].split(':')[1].strip().lower()

        # metabolic activation process
        if lines[i].startswith('METABOLIC ACTIVATION'):
            metabo_act = lines[i].split(':')[1].strip().lower()
            if metabo_act == 'none':
                metabo_act = ['']
            elif metabo_act != '':
                metabo_act = metabo_act.replace(' and ', ', ')
                metabo_act = metabo_act.split(', ')
            else:
                metabo_act = lines[i+1].strip().lower()
                metabo_act = metabo_act.replace(' and ', ', ')
                metabo_act = metabo_act.split(', ')

        # carcinogen process
        if lines[i].startswith('CARCINOGEN:'):
            carcinogen = lines[i].split(': ')
            if carcinogen[-1] == '':
                carcinogen = lines[i+1]
            else:
                carcinogen = carcinogen[-1]
            carcinogen = carcinogen.lower()

        # promoter process
        if lines[i].startswith('PROMOTER:'):
            promoter = lines[i].split(': ')
            if promoter[-1] == '':
                promoter = lines[i+1]
            else:
                promoter = promoter[-1]
            promoter = promoter.lower()

        # dose process
        if lines[i].startswith('DOSE'):
            if 'REGIMEN' not in lines[i]:
                dose = lines[i].strip().split(': ')
                try:
                    dose = dose[1]
                except:
                    dose = ''
                    while not lines[i+1].endswith(' '):
                        if any(lines[i+1].startswith(end_line)
                           for end_line in EOL):
                            break
                        dose += ' ' + lines[i+1].strip()
                        i += 1
                    dose = dose.strip()
                dose = dose.lower()

        # target process
        if lines[i].startswith(('TUMOR SITE', 'TARGET TISSUE', 'END POINT')):
            target = lines[i].strip().split(':')
            if target[-1] == '':
                target = ''
                while not lines[i+1].endswith(' '):
                    target += ' ' + lines[i+1].strip()
                    i += 1
                target = target.strip()
            elif target[1] == ' TYPE OF LESION':
                target = "".join(target[2:]).strip()
            else:
                target = "".join(target[1:]).strip()
            target = target.lower()
            # set the target in DataReview object
            data_review.setTarget(target)

        # result process
        if lines[i].startswith('RESULTS'):
            result = lines[i].strip().split(': ')
            try:
                result = result[1].strip()
            except:
                result = ''
                while not lines[i+1].endswith(' '):
                    result += ' ' + lines[i+1].strip()
                    i += 1
                result = result.strip()
            result = result.lower()

        # reference process
        if lines[i].startswith('<NOINDEX>'):
            while not lines[i].endswith('</NOINDEX>'):
                reference += ' ' + lines[i].strip()
                i += 1
        if lines[i].endswith('</NOINDEX>'):
            reference += ' ' + lines[i].strip()
            reference = reference.strip()

            # 1. step to clean reference
            for word in bad_words:
                reference = reference.replace(word, '')
            reference = reference.lower()
            reference = reference.split(';')

            # 2. step to get the author in the reference
            if ',' not in reference[0]:
                authors = ['']
            else:
                authors = reference[0].split(' ')
                if 'and' in authors:
                    authors.remove('and')
                author = 0
                while author < len(authors):
                    authors[author] = authors[author].replace(',', ' ')
                    author += 1
            if '' in authors:
                authors = ['']
            # set the author in DataReview object
            data_review.setAuthor(authors[0])

            # 3. step to get the title in the reference
            title = reference[1].strip()
            if title.split('.'):
                title = title.split('.')[0]
            title = title.split()
            title = " ".join(title)
            # set the title in DataReview object
            data_review.setTitle(title)

            # 4. step to get the source in the reference
            source = reference[-1]
            try:
                indicator = int(reference[-1].strip())
                source = reference[-2]
            except:
                source = source.split(', ')[-2]
                source = source.split('.')
                if len(source) == 1 or source[0].count(' ') == 1:
                    source = '.'.join(source)
                else:
                    source = source[1:]
                    source = '.'.join(source)
            source = source.strip()
            # set the title in DataReview object
            data_review.setJournal(source)

            # 5. step to get the year in the reference
            try:
                year = reference[-1][len(reference[-1])-4:len(reference[-1])]
                year = int(year)
            except:
                year = 0
            # set the year in DataReview object
            data_review.setYear(year)

            # store the DataReview object if positive result
            if 'positive' in result and data_review.getTarget() is not '':
                data_reviews.append(data_review)

            # reinitialize values for the next study
            reference = ''
            target = ''
            result = ''
            year = 0
        i += 1

    return data_reviews


def DART_extraction(lines):
    """Method to extract data of DART database file.

    Returns:
        data_reviews (list): list which contains all data of review parsed.
        This list correspond to a list of instance of DataReview object.

    """
    print('DART_format detected')
    data_reviews = DART_TOX_procedure(lines, 'DART')
    return data_reviews


def DART_TOX_procedure(lines, format):
    """Method to extract data of DART database file.

    Returns:
        data_reviews (list): list which contains all data of review parsed.
        This list correspond to a list of instance of DataReview object.

    """
    re_author = re.compile('^\s{6}[\w\'\-\s\;\&\#]+\,*[\w\s]+$')
    title = ''
    authors = []
    source = ''
    abstract = ''
    keywords = []
    data_reviews = []
    i = 0
    while i < len(lines):
        # new study detected
        if lines[i].startswith('TITLE:'):
            # creation of a new object associated to a study
            data_review = DataReview()
            data_review.setDBsource(format)
            # title process
            i += 1
            while lines[i] != '':
                title += ' ' + lines[i].strip()
                i += 1
            title = title.strip().lower()
            title = html.unescape(title)
            # set the title in DataReview object
            data_review.setTitle(title)
            # reinitialization of title for next study
            title = ''

        # authors process
        if lines[i].startswith('AUTHORS:'):
            i += 1
            while lines[i] != '':
                if re_author.match(lines[i]):
                    author = html.unescape(lines[i].strip().lower())
                    if ',' in lines[i]:
                        name = author.split(',')[0]
                        fnames = author.split(',')[1]
                        fnames = fnames.split()
                        fnames = [fname[0] for fname in fnames]
                        fnames = ''.join(fnames)
                        author = name + ' ' + fnames
                    authors.append(author)
                i += 1
            # set the first author in DataReview object
            if authors:
                data_review.setAuthor(authors[0])
            # reinitialization of authors for next study
            authors = []

        # source process
        if lines[i].startswith('SOURCE:'):
            i += 1
            while lines[i] != '':
                source += ' ' + lines[i].strip()
                i += 1
            source = html.unescape(source.strip().lower())
            # set the journal name in DataReview object
            data_review.setJournal(source)
            # reinitialization of journal name for next study
            source = ''

        # year process
        if lines[i].startswith('YEAR OF PUBLICATION:'):
            try:
                year = int(lines[i+1].strip())
            except:
                year = 0
            # set the publication year in DataReview object
            data_review.setYear(year)

        # abstract process
        if lines[i].startswith('ABSTRACT:'):
            i += 1
            while lines[i] != '' and not lines[i].startswith('KEYWORDS:'):
                abstract += ' ' + lines[i].strip()
                i += 1
            abstract = html.unescape(abstract.strip().lower())
            # set the abstract in DataReview object
            data_review.setAbstract(abstract)

            # reinitialize abstract for the next study
            abstract = ''
            # store the DataReview object in a list
            if data_review.getAbstract() is not '':
                data_reviews.append(data_review)

        # keywords process
        if lines[i].startswith('KEYWORDS:'):
            i += 1
            while lines[i] != '':
                keywords.append(html.unescape(lines[i].strip().lower()))
                i += 1
            keywords = []

        i += 1

    return data_reviews


def HSDB_extraction(lines):
    """Method to extract data of HSDB database file.

    Returns:
        data_reviews (list): list which contains all data of review parsed.
        This list correspond to a list of instance of DataReview object.

    """
    print("HSDB_format detected")
    bad_words = ['[', ']', ' et al']
    re_company = re.compile('\((\w+)\)')
    re_delimiter = re.compile('(\.)|\d+:|(\s\()')
    re_multi_refs = re.compile('\(\d\-?\d?\)')
    re_reference = re.compile('\[.+?\]')
    re_year = re.compile('(\d{4})(:|\))')
    i = 0
    abstract = ''
    data_reviews = []
    while i < len(lines):
        # abstract and reference process
        while 'REVIEWED**' not in lines[i-1]:
            if lines[i].startswith('      '):
                abstract += ' ' + lines[i].strip()
            i += 1
        abstract = abstract.strip().lower()
        abstract = html.unescape(abstract)
        if abstract is not '':

            # reference process
            reference = re.findall(re_reference, abstract)
            if reference:
                reference = reference[-1]
                for word in bad_words:
                    reference = reference.replace(word, '')

            # clean abstract process
            abstract = re.split(re_reference, abstract)[-2]

            # authors and source process
            if len(re.split(re_multi_refs, reference)) > 2:
                reference = re.split(re_multi_refs, reference)[1].strip()
            if '; ' in reference:
                authors = reference.split('; ')[0]
                source = reference.split('; ')[1]
            elif'. ' in reference:
                authors = reference.split('. ')[0]
                source = reference
                if ', ' in authors:
                    authors = authors.replace(', ', ' ')
                else:
                    authors = ''
            if authors and ')' in authors:
                authors = authors.split(') ')[-1]
            authors = [authors]

            # source process
            if authors[0] and re_company.search(authors[0]):
                source = re_company.search(authors[0])[1]
            else:
                if 'available ' in source:
                    source = source.split(' available')[0]
                if re_delimiter.search(source):
                    source = re.split(re_delimiter, source)[0]
                    source = source.split(',')[0]

            # year process
            year = re.findall(re_year, reference)
            if year:
                year = year[-1][0]
            else:
                year = 0

            # creation of a new object associated to a study
            data_review = DataReview()
            data_review.setDBsource('HSDB')
            # set the abstract in DataReview object
            data_review.setAbstract(abstract)

            # set the first author in DataReview object
            if authors:
                data_review.setAuthor(authors[0])
            # set the journal name in DataReview object
            data_review.setJournal(source)
            # set the publication year in DataReview object
            data_review.setYear(year)

            # store the DataReview object in a list
            if data_review.getAbstract() is not '':
                data_reviews.append(data_review)

        # reinitialization of abstract for next study
        abstract = ''

        i += 1

    return data_reviews


def isPDF(filename):
    """Method to detect a pdf file.

    Return:
        a boolean.

    """
    return os.path.splitext(filename)[1] == '.pdf'


def readPDF(pdfFile):
    """Method to read a pdf file.

    Return:
        textstr (string): string which contains the text extracted from
        a pdf file.

    """
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)

    interpreter = PDFPageInterpreter(rsrcmgr, device)
    password = ''
    maxpages = 0
    caching = True
    pagenos = set()

    for page in PDFPage.get_pages(pdfFile, pagenos,
                                  maxpages=maxpages, password=password,
                                  caching=caching, check_extractable=True
                                  ):
        interpreter.process_page(page)

    device.close()
    textstr = retstr.getvalue()
    retstr.close()
    return textstr


def RTECS_extraction(lines):
    """Method to extract data of RTECS database file.

    Returns:
        data_reviews (list): list which contains all data of review parsed.
        This list correspond to a list of instance of DataReview object.

    """
    print('RTECS_format detected')
    reference = ''
    effects = ''
    i = 0
    data_reviews = []
    while i < len(lines):
        # new study detected
        if lines[i].startswith('TYPE OF TEST'):
            # creation of a new object associated to a study
            data_review = DataReview()
            data_review.setDBsource('RTECS')
            test_system = lines[i].split(':')[-1].strip().lower()

        # route process
        if lines[i].startswith('ROUTE OF EXPOSURE'):
            route = lines[i].split(':')[-1].strip().lower()

        # species process
        if lines[i].startswith('SPECIES OBSERVED'):
            species = lines[i].lower()
            species = species.split(':')[1].split('-')
            category = species[0].strip()
            common_name = species[1].strip()
            # set the species in DataReview object
            data_review.setSpecies(common_name)

        # dose process
        if lines[i].startswith('DOSE'):
            dose = lines[i].split(':')[-1].strip().lower()

        # sexe/duration process
        if lines[i].startswith('SEX/DURATION'):
            sex_duration = lines[i].split(':')[-1].lower().split()
            sex = sex_duration[0]
            duration = " ".join(sex_duration[1:])
            # set the sex species in DataReview object
            data_review.setSex(sex)

        # effects process
        if lines[i].startswith('TOXIC EFFECTS'):
            i += 1
            while not lines[i].startswith('REFERENCE'):
                effects += ' ' + lines[i].strip()
                i += 1
            effects = effects.strip().lower()
            effects = effects.split(' - ')
            # set the effects of the molecule in DataReview object
            data_review.setEffects(effects)

        # reference and source process
        if lines[i].startswith('REFERENCE')\
           and not lines[i+1].startswith('LAST'):
            while not lines[i+1].startswith('TYPE OF TEST')\
               and lines[i+1].strip()[0] != '*':
                i += 1
                reference += ' ' + lines[i].strip()
            reference = reference.strip()
            reference = reference.split('Volume(issue)/page/year:')
            source = reference[0].split('. ')[0]
            source = source.lower()
            # set the journal name in DataReview object
            data_review.setJournal(source)

            # year process
            if len(reference[-1].split(',')) > 1:
                year = int(reference[-1].split(',')[-1])
            elif len(reference[-1].split('/')) > 1:
                year = int(reference[-1].split('/')[-1])
            else:
                year = 0
            # set the publication year in DataReview object
            data_review.setYear(year)

            if data_review.getEffects():
                data_reviews.append(data_review)

            effects = ''
            reference = ''

        if '***' in lines[i] and 'CHEMICAL'\
           not in lines[i] and 'HAZARD' not in lines[i]:
            break

        i += 1

    return data_reviews


def TOXLINE_extraction(lines):
    """Method to extract data of TOXLINE database file.

    Returns:
        data_reviews (list): list which contains all data of review parsed.
        This list correspond to a list of instance of DataReview object.

    """
    print('TOXLINE_format detected')
    data_reviews = DART_TOX_procedure(lines, 'TOXLINE')
    return data_reviews


def detect_format(filename):
    """Method to detect format of a database file.

    Returns:
        data_reviews (list): list which contains all data of review parsed.
        This list correspond to a list of instance of DataReview object.

    """
    data_reviews = []
    # dispatcher of extraction function
    parsing_dispatcher = {
        'CCRIS': CCRIS_extraction,
        'DART': DART_extraction,
        'HSDB': HSDB_extraction,
        'RTECS': RTECS_extraction,
        'TOXLINE': TOXLINE_extraction
    }
    f = None
    # try:
    if not isPDF(filename):
        f = open(filename, encoding='latin-1')
        lines = f.readlines()
        for i in range(len(lines)):
            lines[i] = lines[i].replace('\n', '')
        # the second line of a file should contains an identifier
        # of the original database
        format = lines[1]
        # remove punctuation
        for ch in string.punctuation:
            format = format.replace(ch, '')
        format = format.split()

    else:
        scrape = open(filename, 'rb')
        f = BytesIO(scrape.read())
        scrape.close()
        lines = readPDF(f)
        # convert pdf text to a list of strings
        lines = lines.split('\n')
        # clean obsoletes strings extracted
        lines = cleanPDF(lines)
        # the first line of a PDF should contains an indentifier
        # of the original database
        format = lines[0]
        format = format.split()

    # determine the parsing method to use
    for word in format:
        if word in parsing_dispatcher:
            data_reviews = parsing_dispatcher[word](lines)
            break
    # except:
    #     print('<<< format not detected in {0} >>>'.format(filename))
    # finally:
    if f is not None:
        f.close()

    return data_reviews
