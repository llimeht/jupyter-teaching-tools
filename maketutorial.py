#!/usr/bin/python3

import glob
import os
import os.path
import random
import re
import string
import sys

import nbformat


VERBOSE = False


def find_output_dir(pattern):
    """ find (or create) the obfuscated output directories """
    dirname = glob.glob(pattern % '*')
    if dirname:
        return dirname[0]

    # make the required directory if one doesn't exist
    dirrand = ''.join(random.sample(string.ascii_lowercase, 10))
    dirname = pattern % dirrand
    os.mkdir(dirname)
    return dirname


def clear_tags(cells):
    """ filter out special tutorial tags from the cells """
    bad_tags = ('answer', 'clear', 'template', 'omit')

    for cell, tags in tagged_cells(cells):
        cell['metadata']['tags'] = [tag for tag in tags if tag not in bad_tags]


def _filter_source(filters, source):
    orig_source = source
    for pattern, subst in filters:
        source = pattern.sub(subst, source)
    source = source.expandtabs()
    if VERBOSE and source != orig_source:
        print('=============')
        print(orig_source)
        print('-------------')
        print(source)
    return source


qfilter_re = [
    (re.compile(r'=.*(\s[#%].+)\s*##deval'), r'= ... \t\1'),
    (re.compile(r'=.*\s*##deval'), r'= ...'),
    (re.compile(r'eqn.? [\d.]+(.*)\s*##deeqn'), r'\1'),
    (re.compile(r'return .*(\s[#%].*?)\s*##deret'), r'return ... \t\1'),
    (re.compile(r'return .*##deret'), r'return ...'),
    (re.compile(r'(\s*).+##repl[ \t]?([^\n]+)'), r'\1\2'),
    (re.compile(r'.+##repl[ \t]*'), r''),
    (re.compile(r'\s+#\s*$', re.MULTILINE), r''),
]


def filter_source_q(source):
    return _filter_source(qfilter_re, source)


afilter_re = [
    (re.compile('\s*##deval'), ''),
    (re.compile('\s*##deeqn'), ''),
    (re.compile('\s*##deret'), ''),
    (re.compile('\s*##repl.*'), ''),
]


def filter_source_a(source):
    return _filter_source(afilter_re, source)


def has_tags(cell):
    """ determine whether the cell has any tags """
    return 'metadata' in cell and 'tags' in cell['metadata']


def get_tags(cell):
    """ get the tags list for a cell """
    return cell['metadata']['tags'] if has_tags(cell) else []


def tagged_cells(cells):
    """ iterator to return all cells that have tags """
    for cell in cells:
        if has_tags(cell):
            yield cell, get_tags(cell)


def filter_omitted_cells(cells):
    return [c for c in cells if 'omit' not in get_tags(c)]


def make_question_sheet(infile, outfile):
    """ make the question sheet """
    with open(infile, 'r') as infh, open(outfile, 'w') as outfh:
        nb = nbformat.read(infh, nbformat.NO_CONVERT)
        for cell, tags in tagged_cells(nb.cells):
            is_code = cell['cell_type'] != 'markdown'

            if 'answer' in tags:
                if 'omit' in tags:
                    # omit the cell from the output
                    cell['source'] = ' '
                elif 'template' in tags:
                    # process the source to elide some details
                    cell['source'] = filter_source_q(cell['source'])
                else:
                    # default action is to clear the in/out of the cell
                    # if it is executable
                    cell['source'] = '' if is_code else ' '

                # always clear out the output
                if is_code:
                    cell['outputs'] = []

            if is_code:
                cell['execution_count'] = None

        nb.cells = filter_omitted_cells(nb.cells)
        clear_tags(nb.cells)
        nbformat.write(nb, outfh, nbformat.NO_CONVERT)

    nbformat.validate(nbformat.read(open(outfile), nbformat.NO_CONVERT))


def make_answer_sheet(infile, outfile):
    """ make the worked answers sheet """
    with open(infile, 'r') as infh, open(outfile, 'w') as outfh:
        nb = nbformat.read(infh, nbformat.NO_CONVERT)
        for cell, tags in tagged_cells(nb.cells):
            if 'answer' in tags:
                if 'template' in tags:
                    # process the source to elide some details
                    # particularly the markup for filtering
                    cell['source'] = filter_source_a(cell['source'])

        clear_tags(nb.cells)
        nbformat.write(nb, outfh, nbformat.NO_CONVERT)

    nbformat.validate(nbformat.read(open(outfile), nbformat.NO_CONVERT))


if __name__ == '__main__':

    VERBOSE = False

    if len(sys.argv) < 2:
        print("Usage: %s filename" % sys.argv[0])
        sys.exit(1)

    infile = sys.argv[1]

    # Work out the supersecret paths to obfuscate the file location
    qdir = find_output_dir('questions-%s')
    adir = find_output_dir('answers-%s')

    outfile, outext = os.path.splitext(infile)
    outfile_q = os.path.join(qdir, "%s-questions%s" % (outfile, outext))
    outfile_a = os.path.join(adir, "%s-answers%s" % (outfile, outext))

    make_question_sheet(infile, outfile_q)
    make_answer_sheet(infile, outfile_a)
