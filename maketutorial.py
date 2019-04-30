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
MODE_TAG = 1
MODE_INLINE = 2


INLINE_TAG_RE = re.compile(r'^(###|\%\%\%) (.*)')

QFILTER_RE = [
    (re.compile(r'=.*(\s[#%].+)\s*##deval'), r'= ... \t\1'),
    (re.compile(r'=.*\s*##deval'), r'= ...'),
    (re.compile(r'eqn.? [\d.]+(.*)\s*##deeqn'), r'\1'),
    (re.compile(r'return .*(\s[#%].*?)\s*##deret'), r'return ... \t\1'),
    (re.compile(r'return .*##deret'), r'return ...'),
    (re.compile(r'(\s*).+##repl[ \t]?([^\n]+)'), r'\1\2'),
    (re.compile(r'.+##repl[ \t]*'), r''),
    (re.compile(r'\s+#\s*$', re.MULTILINE), r''),
]

AFILTER_RE = [
    (re.compile(r'\s*##deval'), ''),
    (re.compile(r'\s*##deeqn'), ''),
    (re.compile(r'\s*##deret'), ''),
    (re.compile(r'\s*##repl.*'), ''),
]


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

def cell_first_line(cell):
    lines = cell['source']
    if not lines:
        return None
    return lines.splitlines()[0]

def clear_tags(cells, mode):
    """ filter out special tutorial tags from the cells """
    bad_tags = ('answer', 'clear', 'template', 'omit')

    for cell, tags in tagged_cells(cells, mode):
        if mode == MODE_TAG:
            cell['metadata']['tags'] = [tag for tag in tags if tag not in bad_tags]
        elif mode == MODE_INLINE:
            line = cell_first_line(cell)
            if line:
                cell['source'] = "".join(cell['source'].splitlines(True)[1:])


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


def filter_source_q(source):
    return _filter_source(QFILTER_RE, source)


def filter_source_a(source):
    return _filter_source(AFILTER_RE, source)


def has_tags(cell, mode):
    """ determine whether the cell has any tags """
    if mode == MODE_TAG:
        return 'metadata' in cell and 'tags' in cell['metadata']

    if mode == MODE_INLINE:
        line = cell_first_line(cell)
        return line and INLINE_TAG_RE.match(line)


    raise ValueError("Unknown mode: %s" % mode)


def get_tags(cell, mode):
    """ get the tags list for a cell """
    if mode == MODE_TAG:
        return cell['metadata']['tags'] if has_tags(cell, mode) else []

    if mode == MODE_INLINE:
        line = cell_first_line(cell)
        if line:
            match = INLINE_TAG_RE.match(line)
            if match:
                tags = match.group(2).split()
                if VERBOSE:
                    print(tags)
                return tags
        return []

    raise ValueError("Unknown mode: %s" % mode)


def tagged_cells(cells, mode):
    """ iterator to return all cells that have tags """
    for cell in cells:
        if has_tags(cell, mode):
            yield cell, get_tags(cell, mode)


def filter_omitted_cells(cells, mode):
    return [c for c in cells if 'omit' not in get_tags(c, mode)]


def clean_whitespace(cell):
    cell['source'] = "\n".join(s.rstrip() for s in cell['source'].splitlines())


def make_question_sheet(infile, outfile, mode):
    """ make the question sheet """
    with open(infile, 'r') as infh, open(outfile, 'w') as outfh:
        notebook = nbformat.read(infh, nbformat.NO_CONVERT)
        for cell, tags in tagged_cells(notebook.cells, mode):
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
            clean_whitespace(cell)
        notebook.cells = filter_omitted_cells(notebook.cells, mode)
        clear_tags(notebook.cells, mode)
        nbformat.write(notebook, outfh, nbformat.NO_CONVERT)

    nbformat.validate(nbformat.read(open(outfile), nbformat.NO_CONVERT))


def make_answer_sheet(infile, outfile, mode):
    """ make the worked answers sheet """
    with open(infile, 'r') as infh, open(outfile, 'w') as outfh:
        notebook = nbformat.read(infh, nbformat.NO_CONVERT)
        for cell, tags in tagged_cells(notebook.cells, mode):
            if 'answer' in tags:
                if 'template' in tags:
                    # process the source to elide some details
                    # particularly the markup for filtering
                    cell['source'] = filter_source_a(cell['source'])
            clean_whitespace(cell)

        clear_tags(notebook.cells, mode)
        nbformat.write(notebook, outfh, nbformat.NO_CONVERT)

    nbformat.validate(nbformat.read(open(outfile), nbformat.NO_CONVERT))
    return True


def convert_from_tags(infile, outfile):
    """ convert metadata tags to inline tags """
    with open(infile, 'r') as infh, open(outfile, 'w') as outfh:
        notebook = nbformat.read(infh, nbformat.NO_CONVERT)
        for cell, tags in tagged_cells(notebook.cells, MODE_TAG):
            is_code = cell['cell_type'] != 'markdown'
            fmt = "### %s\n%s" if is_code else "%%%%%% %s\n\n%s"
            if tags:
                cell['source'] = fmt % (
                    " ".join(tags),
                    cell['source']
                )
            clean_whitespace(cell)

        clear_tags(notebook.cells, MODE_TAG)
        nbformat.write(notebook, outfh, nbformat.NO_CONVERT)

    nbformat.validate(nbformat.read(open(outfile), nbformat.NO_CONVERT))


def is_conversion_needed(infile):
    """ figure out of the file needs converting first """
    with open(infile, 'r') as infh:
        notebook = nbformat.read(infh, nbformat.NO_CONVERT)
        for cell, tags in tagged_cells(notebook.cells, MODE_TAG):
            if tags and 'answer' in tags:
                return True
    return False


def process_filename(infile):
    convert = is_conversion_needed(infile)

    if convert:
        print("Converting from tags to inline markers")
        backupfile = '%s.bak' % infile
        os.rename(infile, backupfile)
        convert_from_tags(backupfile, infile)

    # Work out the supersecret paths to obfuscate the file location
    qdir = find_output_dir('questions-%s')
    adir = find_output_dir('answers-%s')

    outfile, outext = os.path.splitext(infile)
    outfile_q = os.path.join(qdir, "%s-questions%s" % (outfile, outext))
    outfile_a = os.path.join(adir, "%s-answers%s" % (outfile, outext))

    tagmode = MODE_INLINE

    make_question_sheet(infile, outfile_q, tagmode)
    make_answer_sheet(infile, outfile_a, tagmode)


if __name__ == '__main__':

    VERBOSE = False

    if len(sys.argv) < 2:
        print("Usage: %s filename" % sys.argv[0])
        sys.exit(1)

    sys.exit(not process_filename(sys.argv[1]))
