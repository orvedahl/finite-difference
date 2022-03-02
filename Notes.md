# Python Package Structure

## Directory Tree
The basic directory structure for a Python package should look like:
```
Project_Name/
|
+-- src/
|   |
|   +-- packagename/
|       |
|       +-- __init__.py
|       +-- module1.py
|       +-- module2.py
|       +-- submodule1/
|           |
|           +-- module3.py
|       ...
|
+-- tests/
|   |
|   +-- ...
|
+-- docs/
|   |
|   +-- ...
|
+-- setup.py
```
Having the source code and test suite in separate directories prevents some unwanted
path issues. Placing the `packagename/` directory beneath the `src/` directory forces
you to install the code before testing, compared to simply importing from the local
current working directory. This forces you to test the installation of the project as
well as running the individual unit tests. There are most likely other advantages that
are not listed here.

## Setup Script
This script should be as simple as possible. This example is based on
a post from [stackoverflow](https://stackoverflow.com/questions/64950460/link-f2py-generated-so-file-in-a-python-package-using-setuptools),
but the tree and files are updated to reflect this project:
```
finite-difference/
|
+-- src/
|   |
|   +-- finite_difference/
|       |
|       +-- __init__.py
|       +-- fd.py
|       +-- fortran/
|           |
|           +-- fd.f90
|
+-- tests/
|   |
|   +-- test_fd.py
|
+-- setup.py
```
For this project, `fd.py` is a carbon copy of `fd.f90`, but written in Fortran.

In this case, the `setup.py` file is quite simple:
```
from setuptools import find_packages
from numpy.distutils.core import setup, Extension

ext = Extension(name='finite_difference.fortran',
                sources=['src/finite_difference.fortran/fd.f90'],
                f2py_options=['--quiet'],
               )

setup(name='finite_difference',
      version="0.0.1",
      package_dir={"": "src"},
      packages=find_packages(where="src"),
      ext_modules=[ext])
```
As we want to use `f2py`, the `Extension` function from `numpy` is used. Useful
options for the `Extension` function include:
 * `name` is how Python will import the extension
 * `sources` is a list of source files (relative to the top directory of the package),
    order matters if there are inter-file dependencies
 * `f2py_options` is a list of flags to send to `f2py`
Other options that are not listed above include:
 * `extra_compile_args` list of strings to pass to the compiler
 * `extra_link_args` list of strings to pass to the linker
 * `extra_f90_compile_args` list of strings to pass to the Fortran 90 compiler
 * `libraries` list of libraries to include when compiling/linking, each one should not
    include the leading `-l`
 * `library_dirs` list of directories where the libraries can be found
 * `include_dirs` list of include directories
Options for the `setup` call include (mostly all strings):
 * `name` the name of the package
 * `author` the author(s)
 * `author_email` to include contact information
 * `description` is a short description of the project
 * `long_description` is a more verbose description, most often this holds the contents
    of the `README` file
 * `license` describes the type of licences, where the actual licence contents usually
    appear in the `LICENSE` file
 * `version` is a numerical version number, usually formatted: `major.minor.micro`
 * `packages` is a list of packages to use, basically the directories that contain
    `__init__.py` files. The `setuptools` package provides a nice function for finding
    these automatically.
 * `package_dir` is a dictionary that tells Python where your package directories live.
    Packages in the `src/` directory would be accessed as `package_dir={'':'src'}`.
    The keys are package names and an empty key means "root package". The values
    are where the package can be found. With `packages=['bar']`, Python
    would expect to find the package `bar` in `src/bar` and the file
    `src/bar/__init__.py` is assumed to exist.
 * `ext_modules` is a list of `Extension` objects
 * `define_macros` list of tuples that define preprocessor macros.
   `define_macros=[('DEBUG', 1), ('COOL', None)]` is equivalent to having
   `#define DEBUG 1` and `#define COOL` at the top of every source file.

## Installing
Use `pip` to install your package:
```
cd PACKAGE_HOME

python3 -m pip install --user .
```

### Reinstalling
To reinstall the package:
```
cd PACKAGE_HOME

python3 -m pip install --user --upgrade --no-deps --force-reinstall .
```
which will reinstall the local package, but will not reinstall the dependencies (`--no-deps`).

### Uninstalling
Uninstalling packages can be a little tricky. `pip` can install dependencies that are used
by other packages. Using the `show` command will display information of the package:
```
python3 -m pip show finite_difference
```
The last two lines, `Requires` and `Required-by`, show the dependencies of this project and
the other packages that depend on this project. If no other package depends on this project,
the project can safely be removed. Each element listed in `Requires` should also be removed,
provided it is not required by other packages. The `show` command can help determine this
and the `uninstall` command can be applied to each element in `Requires` that you wish to
remove.

There is also some temporary data that should be removed, so a full uninstall should include:
```
cd PACKAGE_HOME/

python3 -m pip uninstall finite_difference
rm -rf ./build
rm -rf src/finite_difference.egg-info      # <-- this assumes a src/ directory tree

python3 -m pip uninstall <no-longer-needed-dependency-1>
python3 -m pip uninstall <no-longer-needed-dependency-2>
```

## Testing
This project will be using `pytest` to conduct the unit tests (covered somewhere else,
for now).

## Documentation
This is best done using Sphinx (covered somewhere else, for now).

