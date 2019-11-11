# Jupyter Teaching Tools

This (small but hopefully growing) collection of tools is designed to help
people teach using Jupyter. The
[Jupyter Notebook](https://jupyter.org/)
is a convenient tool in
which to learn various aspects of programming, including the application of
programming skills to science and engineering problems that include
numerical methods and statistics.

The tools currently available in the repository are:

* `maketutorial.py`: takes a jupyter notebook with included metadata tags
  on each cell and creates a pair of new notebooks for a *questions* sheet
  and an *answers* sheet.


## maketutorial: template-generated Question and Answer sheets

The philosophy behind this tool is that the instructor should only have
information in one place: a tutorial *template* from which the *question*
and *answer* sheets are generated. Altering a question or fixing an answer
should only ever be done in the template file and then the children notebooks
can be regenerated.

### Concept of maketutorial

* cells to be processed have specially formatted comments added to them to
  indicate what sort of processing should be done
* some lines within `template` type cells can be manipulated using specially
  formatted comments on the relevant line
* `maketutorial` is run in *questions* mode to generate the question sheet
  and then in *answers* mode to generate the solutions.
* the separate questions and answers output notebooks are published to the
  students as required.

### Details

The cells in the Jupyter notebook are tagged using specially formatted
comments within the cell contents. Both code cells and Markdown cells
can be decorated in this way, although more processing options are available
for code cells.
The special comments to tag a cell must be in the first line of text of the
cell and start either with `###` or `%%%` for use in Python, Octave and
Markdown cells.

The cell-level tags that are understood are:

* `answer`: the cell is an answer cell. Its output should be cleared from the
  *questions* version and further tags should be used to determine how to
  determine how the cell is to be presented in the *answers* version.
* `template`: the cell should have some replacements applied to it based on the
  in-code comments listed below.
* `omit`: the cell should be completely omitted from the *answers* output.

In `template` mode,  textual replacements may be made on each line of the cell
to manipulate the contents of the cell, for instance to redact parts of the
answer (leaving hints behind).
The replacements in `template` cells are only applied when the program is run
in *questions* mode; in *answers* mode, the replacement code is simply deleted.

* `##deval`: removes the value that will be set to a variable, leaving an ellipsis to indicate that something is missing
    ```python
    v = 20.0                                 ##deval
    w = 10.0      # comment is preserved     ##deval
    ```
    becomes in *questions* mode
    ```python
    v = ...
    w = ...       # comment is preserved
    ```

* `##deeqn`: remove a cross-reference to an equation in the course notes
    ```python
    y = m * x + b        # use the gradient, eqn 3.2          ##deval ##deeqn
    ```
    becomes in *questions* mode
    ```python
    y = ...              # use the gradient,
    ```

* `##deret`: removes what follows a `return` statement
    ```python
    def dxdt(x):
        return A.dot(x)                      ##deret
    ```
    becomes in *questions* mode
    ```python
    def dxdt(x):
        return ...
    ```

* `##repl`: replaces the beginning of line with the text that follows, for
  use when syntax doesn't let you just chop a line up as with the other tags.
    ```python
    T = odeint(dTdt, T0, t, hmax=0.01/f)               ##repl T = odeint(... ... , hmax=0.01/f)
    ```
    becomes in *questions* mode
    ```python
    T = odeint(... ... , hmax=0.01/f)
    ```

The output files are created in obscurely named directories for delivery via
links from an LMS system to CoCalc.

Usage:
```
    maketutorial tutorial1.ipynb
```

### Notes

A previous version of the `maketutorial` tool used tag metadata within the
Jupyter notebook for the tagging. This is a technically superior interface
but editing the tags and visibility of the tags was sufficiently difficult
that it was found not to be a good option. Notebooks with metadata-based
tagging are automatically converted to comment-based tagging by
`maketutorial`.


## Installation

`maketutorial` is a simple, self-contained Python script and can be copied
to a suitable location, such as `/usr/local/bin/` or the top-level folder
of a set of course tutorials. There is also a `setup.py` script provided:

```bash
    python setup.py install
```

The Python module `nbformat` is required; this module is part of the Jupyter
suite.
