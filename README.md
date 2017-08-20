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


## maketutorial:

The philosophy behind this tool is that the instructor should only have
information in one place: a tutorial *template* from which the *question*
and *answer* sheets are generated. Altering a question or fixing an answer
should only ever be done in the template file and then the children notebooks
regenerated.

Tags are added to the notebook metadata either by editing the JSON file in a
text editor or through the Jupyter editor. At present, only `code` cells are
altered, Markdown cells are passed through unchanged.

The tags that are understood are:

* `answer`: the cell is an answer cell. Its output should be cleared from the
  *questions* version and further tags should be used to determine how to
  determine how the cell is to be presented in the *answers* version.
* `template`: the cell should have some replacements applied to it based on the
  in-code comments listed below.
* `omit`: the cell should be completely omitted from the *answers* output.

The replacements in `template` cells are applied in *questions* mode as described
below. In *answers* mode, the replacement code is simply deleted.

* `##deval`: removes the value that will be set to a variable, leaving an ellipsis to indicate that something is missing
    ```python
    v = 20.0                                 ##deval
    w = 10.0      # comment is preserved     ##deval
    ```
    becomes
    ```python
    v = ...
    w = ...       # comment is preserved
    ```

* `##deeqn`: remove a comment to see a particular equation from the notes
    ```python
    y = m * x + b        # use the gradient, eqn 3.2          ##deval ##deeqn
    ```
    becomes
    ```python
    y = ...              # use the gradient,
    ```

* `##deret`: removes what follows a `return` statement
    ```python
    def dxdt(x):
        return A.dot(x)                      ##deret
    ```
    becomes
    ```python
    def dxdt(x):
        return ...
    ```

* `##repl`: replaces the beginning of line with what follows, for use when
  syntax doesn't let you just chop a line up as with the other tags.
    ```python
    T = odeint(dTdt, T0, t, hmax=0.01/f)               ##repl T = odeint(... ... , hmax=0.01/f)
    ```
    becomes
    ```python
    T = odeint(... ... , hmax=0.01/f)
    ```

The output files are created in obscurely named directories for delivery via
links from an LMS system to CoCalc.

Usage:
```
    maketutorial tutorial1.ipynb
```
