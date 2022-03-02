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
For this project, `fd.f90` is a carbon copy of `fd.py` in that both provide identical
functionality.

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
    appear in the `LICENSE` file. [Choose a license](https://choosealicense.com) can
    help you determine the correct one for you.
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

### Setup Configuration
Sometimes it is useful to provide system-dependent customization to the user without
requiring changes to the `setup.py` file, e.g., compiler-based choices including
library directories and architecture-specific optimization flags. This is where
configuration files come in handy. Installers can override some defaults in the
`setup.py` by editing the config file. The configuration file will be called `fdiff.cfg`
and might look like:
```
[compiler-info]

# build project with Fortran support
INCLUDE_FORTRAN = True

# specify the compiler vendor that f2py should use. to see available ones:
#     f2py - --help-fcompiler
# common options include:
#     gnu95      GNU Gfortran
#     intelem    Intel
F90_COMPILER = intelem

# set custom flags, such as architecture optimizations
EXTRA_COMPILE_FLAGS = -O3 -xavx2

# space-separated list of libraries to use, without the leading "-l"
LIBRARIES = mkl_intel_ilp64 mkl_sequential mkl_core

# space-separated list of library directories to use
LIBRARY_DIRS = ${MKLROOT}/lib/intel64

# space-separated list of include directories to use
INCLUDE_DIRS = ${MKLROOT}/include
```
To use this information within the `setup.py` file, we must read the various values
using:
```
from configparser import ConfigParser

# build the configure object and parse the input file
config = ConfigParser()
config.read("fdiff.cfg")

# extract the variables
section = "compiler-info"
build_f90 = config.getboolean(section, "INCLUDE_FORTRAN")       # read a boolean
compiler  = config.get(section, "F90_COMPILER")                 # read/process a string
flags     = config.get(section, "EXTRA_COMPILE_FLAGS").split()  # read/process a string
libraries = config.get(section, "LIBRARIES").split()            # read/process a string
lib_dirs  = config.get(section, "LIBRARY_DIRS").split()         # read/process a string
includes  = config.get(section, "INCLUDE_DIRS").split()         # read/process a string
```
Now these variables can be passed on to the `Extension` objects and the `setup`
function call.

Configure files can also be used to document what options were ultimately used to
build the project.
```
used = ConfigParser()
section = "installed-options"

newconfig.set(section, "python_version", <py_version>)
newconfig.set(section, "compiler", <compiler_name>)
newconfig.set(section, "compiler_version", <compiler_version>)
newconfig.set(section, "compiler_flags", <compiler_flags>)

newconfig.set(section, "build_dir", <build_directory>)
newconfig.set(section, "build_time", <build_time>)
newconfig.set(section, "build_machine", <build_machine>)

with open(output_file, "w") as configfile:
    newconfig.write(configfile)    # write the installed values
    config.write(configfile)       # write the originally requested values
```

### Some Pitfalls
Specifying the compiler used by `f2py` in the configuration file leads to some subtle
difficulties. The default is GCC, but Intel is also supported. The only trick is that
the compiler you want to use should be the first one found in the `PATH`.

Currently, the NVIDIA HPC compiler does not work. The most robust way to change the
compiler that `f2py` uses is by changing the command line options using the
`sys.argv.extend(...)` function within the `setup.py` file. Using the `f2py_options`
argument does not work.

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

# Testing
Testing should make use of assertions through the `assert` statement. Assertions should
only be used to track down bugs during development; the user should never encounter them.
As the assertions take up time and resources, they should be disabled for production code.

The following statement:
```
if __debug__:
    if not expression:
        raise AssertionError(assertion_message)
```
is functionally equivalent to
```
assert expression, assertion_message
```
The value of `__debug__` depends on the mode in which Python is run. Normal mode uses
`__debug__ = True`, but production code should ideally use `__debug__ = False`.

One way to disable the assertions is to invoke python using
```
python -O ...
```
where the `-O` flag is a capital letter O, not zero. A second way to disable assertions
is to set the environment variable `PYTHONOPTIMIZE` to a non-empty string, such as
```
PYTHONOPTIMIZE=true
```

## Pytest
A great tool to perform testing is `pytest`. Often times multiple tests will make use
of the same test data. Instead of each individual test regenerating the test data,
a fixture can be used to hold that data where it can be accessed by multiple tests.
```
def test_is_prime():
    x = [1,2,3,4,5,6]
    primes = [is_prime(i) for i in x]
    assert primes == [False, True, True, False, True, False]

def test_is_even():
    x = [1,2,3,4,5,6]
    evens = [is_even(i) for i in x]
    assert primes == [False, True, False, True, False, True]
```
with fixtures, these would become
```
import pytest

@pytest.fixture
def numbers():
    return [1,2,3,4,5,6]

def test_is_prime(numbers):
    primes = [is_prime(i) for i in x]
    assert primes == [False, True, True, False, True, False]

def test_is_even(numbers):
    evens = [is_even(i) for i in x]
    assert primes == [False, True, False, True, False, True]
```

Fixtures can depend on other fixtures, which provides modularity and therefore versatility.
`pytest` will search for a file named `conftest.py` in whatever directory it is running.
This file is a great spot to store generic and frequently used fixtures. The `monkeypatch`
fixture can be used to replace values and behaviors, such as preventing real network calls
when testing.

Various tests can be grouped together to avoid running all tests when a single subset
of the tests is really wanted. `pytest` does this by marking a test as a particular
category. Use the `--strict-markers` flag when running `pytest`, this will ensure that all
marks have been registered in the `pytest` configuration. A very useful mark is
`parametrize`. It allows you to test multiple conditions with a single test definition.
For example,
```
def test_is_palindrome_empty_string():
    assert is_palindrome("")

def test_is_palindrome_single():
    assert is_palindrome("a")

def test_is_palindrome_mixed_case():
    assert is_palindrome("Bob")

def test_is_palindrome_spaces():
    assert is_palindrome("Never odd or even")

def test_is_palindrome_empty_punctuation():
    assert is_palindrome("Do geese see God?")

def test_is_palindrome_not_palindrome():
    assert is_palindrome("abc")

def test_is_palindrome_not_quite():
    assert is_palindrome("abab")
```
all have the form:
```
def test_is_palindrome_<some situation>():
    assert is_palindrome("<some string>")
```
The `parametrize` mark allows these to be collapsed significantly:
```
@pytest.mark.parametrize("palindrome", [
    "",
    "a",
    "Bob",
    "Never odd or even",
    "Do geese see God?",
])
def test_is_palindrome(palindrome):
    assert is_palindrome(palindrome)

@pytest.mark.parametrize("non_palindrome", [
    "abc",
    "abab",
])
def test_is_palindrome_no(non_palindrome):
    assert not is_palindrome(non_palindrome)
```
The first argument is a comma separated string of parameter names. The second argument
is a list of tuples or single values that represent the parameter value(s).
The above cases could be combined into a single test using:
```
@pytest.mark.parametrize("maybe_palindrome, expected_result", [
    ("", True),
    ("a", True),
    ("Bob", True),
    ("Never odd or even", True),
    ("Do geese see God?", True),
    ("abc", False),
    ("abab", False),
])
def test_is_palindrome(maybe_palindrome, expected_result):
    assert is_palindrome(maybe_palindrome) == expected_result
```
This shortened the code, but might make the test a little more opaque; be clear about
what the test is testing.

The `--durations=n` option to `pytest` can provide some duration reporting of the results;
`n` is an integer telling `pytest` to report on the `n` slowest results.

The `pytest-cov` plugin integrates the `coverage` package to see the test coverage report.

Tests can be used in a class as well:
```
class TestClass:
    def test_one(self): # should pass
        x = "this"
        assert "h" in x

    def test_two(self): # should fail
        x = "hello"
        assert hasattr(x, "check")
```
The name of the class should start with `Test` for it to be automatically found/run.

### Running Pytest
To actually run the test suite:
```
cd tests/
pytest [options]
```
By default, `pytest` will run all files of the form `test_*.py` or `*_test.py` in the
current directory and its subdirectories.

### Plugins


# Documentation
This is best done using Sphinx (covered somewhere else, for now).

