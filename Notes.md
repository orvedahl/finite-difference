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
This script should be as simple as possible. This example is based on a post from
[stackoverflow](https://stackoverflow.com/questions/64950460/link-f2py-generated-so-file-in-a-python-package-using-setuptools),
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
`setup.py` by editing the config file.
The configuration file will be called `fdiff.cfg` and might look like:
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
The configure file approach is perfectly fine if the user is expected to:
  1. Clone the repo
  2. Modify the config file
  3. Manually install package with `pip install --user .`
This has issues if the goal is to bundle the code into a package that gets distributed
and then installed. Packaging involves essentially building a tarball that the user
downloads and installs with no other input required. The question becomes how do you
package a configure file into a tarball that would be user-editable? One solution is
to switch to custom environment variables. Place the relevant environment variables
in a user-editable shell script and have the user source that script before installing.
Then the `setup.py` file would extract the environment variable information, using the
default values when necessary.

Specifying the compiler used by `f2py` in the configuration file leads to some subtle
difficulties. The default is GCC, but Intel is also supported. The only trick is that
the compiler you want to use should be the first one found in the `PATH`.

Currently, the NVIDIA HPC compiler does not work.

The most robust way to change the
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
which will reinstall the local package, but will not reinstall the dependencies
(`--no-deps`).

### Uninstalling
Uninstalling packages can be a little tricky. `pip` can install dependencies that are used
by other packages. Using the `show` command will display information of the package:
```
python3 -m pip show finite_difference
```
The last two lines, `Requires` and `Required-by`, show the dependencies of this project
and the other packages that depend on this project. If no other package depends on this
project, the project can safely be removed. Each element listed in `Requires` should also
be removed, provided it is not required by other packages. The `show` command can help
determine this and the `uninstall` command can be applied to each element in `Requires`
that you wish to remove.

There is also some temporary data that should be removed, so a full uninstall should
include:
```
cd PACKAGE_HOME/

python3 -m pip uninstall finite_difference
rm -rf ./build
rm -rf src/finite_difference.egg-info      # <-- this assumes a src/ directory tree

python3 -m pip uninstall <no-longer-needed-dependency-1>
python3 -m pip uninstall <no-longer-needed-dependency-2>
```

# Testing
There are three types of tests:
 * unit : test individual modules in an isolated manner, i.e., without dependencies
 * integration : verify that different modules work together when combined as a group
 * functional : check that the entire application is behaving as expected
As an example, build a phone with a battery and a sim card:
 * unit test : check battery for life/capacity, check sim card for activation
 * integration test : battery and sim card are combined/integrated so start the phone
 * functional test : check phone for features from the user point of view, e.g.,
   does it connect using the sim card, is the battery supplying adequate power.
Usually these tests are done in order: first unit, then integration, finally functional.

Unit tests are used to verify that individual functions do what they advertise; correct
behavior, correct output with valid input, appropriate failure with invalid input. This
is done in an isolated manner, so there are no dependencies on other modules/functions.

Integration tests allow for dependencies between modules/functions in order to test
how well they place with one another. Multiple modules are combined/integrated together
and testing of their combined behavior is completed. There are three approaches:
 * Big Bang
 * Top Down
 * Bottom Up
In the Big Bang approach, all modules are integrated and tested as a whole at one time.
This is good if multiple modules are ready to go at the same time, but it can be quite
difficult to track down failures. In the Top Down approach, modules are integrated
one by one until all modules have been integrated. The modules are added starting at the
higher levels and moves down to the lower levels. This is very organic in that it
mimics how things happen in the real environment. The major functionality is only
tested at the very end. With the Bottom Up approach, modules are integrated starting
at the lower levels and moving up towards the higher levels. This means higher-level
issues are only identified at the end of the process.

Functional testing looks at the entire application for correct behavior compared to
expected behavior. In this way, it is more of a black-box type testing.

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
A great tool to perform testing is `pytest`.

### Fixtures
Often times multiple tests will make use
of the same test data. Instead of each individual test regenerating the test data,
a fixture can be used to hold that data where it can be requested by multiple tests.
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
    primes = [is_prime(i) for i in numbers]
    assert primes == [False, True, True, False, True, False]

def test_is_even(numbers):
    evens = [is_even(i) for i in numbers]
    assert primes == [False, True, False, True, False, True]
```

Fixtures can request other fixtures, which provides modularity and therefore versatility.
Test functions (and fixtures) can request multiple fixtures:
```
import pytest

@pytest.fixture
def numbers():
    return [1,2,3,4,5,6]

@pytest.fixture
def prime_numbers():
    return [False, True, True, False, True, False]

def test_is_prime(numbers, prime_numbers):
    primes = [is_prime(i) for i in numbers]
    assert primes == prime_numbers
```

`pytest` will search for a file named `conftest.py` in whatever directory it is running.
This file is a great spot to store generic and frequently used fixtures. Fixtures can
be given scopes. Usually a fixture is invoked once per test function, but specifying
the scope can reduce that to once per module. This is particularly useful if the
fixture is expensive, such as large data or a time-consuming network connection.
Placing the fixture within the `conftest.py` file and using:
```
# conftest.py
import pytest
import smtplib

@pytest.fixture(scope="module")
def smtp_connection():
    return smtplib.SMTP("smtp.gmail.com", 587, timeout=5)

# test_module.py
def test_noop(smtp_connection):
    res, msg = smtp_connection.noop()
    assert response == 250
```
The fixture will be shared among all test functions that request it within the
`test_module.py` file. Available scopes include:
  * `function`: default scope, rebuilt for every test function
  * `class`: fixture is destroyed after the last test in the class
  * `module`: fixture is destroyed after all tests within a single file/module are done
  * `package`: fixture is destroyed after the last test of the package
  * `session`: fixture is destroyed at the end of the test session

Standard fixtures use the `return` construct, it is possible to use the `yield` construct
instead. An alternative is to use finalizers to shutdown fixtures.

Fixtures can be made to run multiple times which helps write exhaustive functional tests
for components that can be configured in multiple ways.
```
@pytest.fixture(scope="module", params=[1,2,3,4,5])
def numbers(request):
    return request.param

def test_is_even(numbers):
    assert numbers % 2 == 0
```
In the above example, there is only one test function, but it will be run 5 times, each
time with a different number from the `numbers` fixture. The magic happens due to the
special `request` fixture that provides access to the parameters. Specific parameters
can be marked (more on this later) for special treatment using:
```
@pytest.fixture(params=[0, 1, pytest.param(2, marks=pytest.mark.skip))
def data_set(request):
    return request.param

def test_data(data_set):
    pass
```
The above will run using parameters `0` and `1`, but it will always skip the parameter `2`.

When reporting results, a particular ID is given to each test, these IDs can be customized
using the `ids` argument when describing the fixture.

### Markers
Markers allow you to organize and customize some of the test functions and fixtures.
Some builtin markers include:
  * `skip`: always skip a test function
  * `skipif`: skip a test function if a condition is true
  * `xfail`: produce an "expected failure" outcome if a certain condition is met
  * `parametrize`: perform multiple calls to the same test function

Marks can only be applied to tests, having no effect on fixtures.

Custom marks can be registered in the `conftest.py` file using:
```
def pytest_configure(config):
    config.addinivalue_line("markers",
                            "slow: marks tests as slow (deselect with '-m \"not slow\"')")
    config.addinivalue_line("markers", "serial")
```
The marks would then be used by adding `@pytest.mark.serial` or `@pytest.mark.slow`
decorators to the appropriate test function.
The magic here is that you are changing the ini values from within Python. This means
you can specify the exact same information from within a `pytest.ini` configuration file.
The first argument `"markers"` specifies what part of the ini file to adjust and the
second argument is the actual entry. The name of the mark should appear to the left of
the colon and anything after the `:` is an optional description.
Use the `--strict-markers` flag when running `pytest`, this will ensure that all
marks have been registered in the `pytest` configuration. This can also be done by
including the line `addopts = --strict-markers` to the ini file or `pytest_configure`
function.

The `parametrize` mark is great for testing multiple conditions with a single test
definition. For example,
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

An entire matrix of parameter combinations can be run using:
```
@pytest.mark.parametrize("x", [0,1])
@pytest.mark.parametrize("y", [1,3])
def test_foo(x,y):
    pass
```
This will run all four combinations of `(x,y)` pairs.

Tests can be made even more general compared to the parametrize approach by using the
`pytest_generate_tests` hook. This can allow you to add command line arguments to
`pytest` and generate test functions dynamically.

### Mock Modules/Environments
Sometimes tests need to invoke functions that change global parameters or require code that
cannot be easily tested, such as network connections. The `monkeypatch` fixture provides a
way to build mock environments and modules that safely change parameters. The changes are
safely undone after the requesting test function is complete.

### Running Pytest
To actually run the test suite:
```
cd tests/
pytest [options]
```
By default, `pytest` will run all files of the form `test_*.py` or `*_test.py` in the
current directory and its subdirectories. Tests can be used in a class as well:
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

A specific test within a module can be run using
```
pytest test_mod.py::test_func
```
and a specific method within a class can be run as
```
pytest test_mod.py::TestClass::test_method
```

Options to `pytest`:
 * `--durations=n` will provide some duration reporting for the `n` slowest results.
   This can be used with `--durations-min=<m>` to show the `n` slowest results that
   took longer than `m` seconds.
 * `-k <string>` will run tests that contain names matching the given string. It can
   also be of the form `-k <string> and not <key>`, for example,
   `pytest -k "MyClass and not method"` will run `TestMyClass.test_something`, but
   will not run `TestMyClass.test_method_simple`.
 * `-m <marker>` will run all tests that have the specified marker
 * `--fixtures` will display the available fixtures
 * `--cov=<name>` will report coverage data for the specified package name (requires
   the `pytest-cov` package)

`pytest` can also be called from within Python as
```
options = ["opt-1", "opt-2", ...] # list of strings holding the options and arguments
retcode = pytest.main(options)
```

### Plugins
There are multiple plugins that extend the functionality of `pytest`. Most plugins are
automatically incorporated into `pytest`. To disable a particular plugin (for example
in a CI server), a line can be added to the `pytest.ini` file or the environment variable
`PYTEST_ADDOPTS` can be used:
```
export PYTEST_ADDOPTS=-p no:NAME
```
where `NAME` is the name of the plugin to disable.

## Multiple Python Versions
In order to run multiple versions of Python, those versions must
already be available on your system. [Pyenv](https://github.com/pyenv/pyenv) is a
powerful tool to manage the multiple Python versions, it can even "load" a different
version of Python automatically depending on your current directory.

First install the Python dependencies for Fedora using:
```
su -c
dnf install make gcc zlib-devel bzip2 bzip2-devel readline-devel sqlite sqlite-devel \
            openssl-devel tk-devel libffi-devel xz-devel
```
Even if Python is already installed, some of the devel packages might be missing.

To install pyenv:
 1. Clone the repo
 2. Setup the shell environment and re-source/login/load the session
 3. Install Python build dependencies (above `dnf` command)
 4. Install new/old Python versions

Upgrading pyenv:
```
cd $(pyenv root)
git pull
```
or to upgrade to a specific release:
```
cd $(pyenv root)
git fetch
git tag
git checkout v0.0.0
```

To disable/uninstall pyenv:
 * Disable: remove the `pyenv init` command from the `.bashrc`. The `pyenv` command
   will still be available and `python` will point to the system Python.
 * Uninstall: remove all pyenv related commands from the `.bashrc`, then remove the
   root directory, `rm -rf $(pyenv root)`

Installing pyenv and the pyenv-virturalenv plugin:
```
cd /path/where/software/is/installed   # <-- call this directory my_PYENV_HOME
git clone https://github.com/pyenv/pyenv.git

# optionally, compile a dynamic Bash extension to speed up pyenv
# if it fails, pyenv will still work normally:
cd pyenv
src/configure
make -C src

cd plugins
git clone https://github.com/pyenv/pyenv-virtualenv.git
```
Simply cloning the repos and properly setting the environment variables is enough to
install pyenv. If the Environment Modules (e.g., `module load`) package is used to
load versions of Python, then pyenv may not work properly, since the magic of pyenv
is managing the `PATH` and intercepting calls to `python` and `pip`. If the
`module load python` command changes the `PATH`, then `python` and `pip` will never
be redirected to pyenv.

Environment setup:
 * Set `PYENV_ROOT` to point to the git-cloned directory
 * Put `PYENV_ROOT/bin` at the beginning of the PATH
 * Initialize pyenv
 * Initialize pyenv-virtualenv plugin
Assuming `.bash_profile` sources `.bashrc`, the above is accomplished by placing
the following at the end of `~/.bashrc`:
```
export PYENV_ROOT=/path/where/software/is/installed/pyenv
export PATH=$PYENV_ROOT/bin:$PATH
eval "$(pyenv init -)"
eval "$(pyenv init --path)"
eval "$(pyenv virtualenv-init -)"
```
Be sure to place these commands at the bottom of the `.bashrc` so the `PATH` is set last
and not overwritten by something else.

### Pyenv Commands
To list the available Python versions that can be installed: `pyenv install --list`

Install a particular version: `pyenv install 3.8.12`, or `pyenv install -v <version>` to
see more information. It may take a minute or two to complete.

Uninstall: `pyenv uninstall 3.8.12`

List installed versions: `pyenv versions`, the `*` indicates what version is active. To
only show information about the currently active version: `pyenv version`.

The default Python is the `system` one, but `which python` will point to the pyenv
directory structure. Pyenv is intercepting the `python` call (due to the `PATH`) and
redirecting it to use
the system Python. Using `pyenv which python` will show the actual path being used,
which does correspond to the expected system location.

Switch the default: `pyenv global 3.8.12` or `pyenv global system`

Set an application-specific Python version: `pyenv local 3.8.12`. This will create a file
named `.python-version` in the current directory. Whenever pyenv is active, the file will
automatically activate that version. It can be unset using `pyenv local --unset`.

Pyenv follows a simple decision tree to determine how to set the Python version, in order:
 1. `pyenv shell <version>` which sets `$PYENV_VERSION` environment variable
 2. `pyenv local <version>` which sets the `.python-version` file
 3. `pyenv global <version>` which sets the global default in the `$PYENV_ROOT/version` file
 4. System Python
Whatever pyenv finds first will be used. The local version is a top-down approach, i.e., the
`.python-version` file will apply to current directory and any subdirectories.

### Virtual Environments with Pyenv
Pyenv handles multiple Python versions, the standard virtualenv/venv manages multiple
virtual environments for a specific Python version. The pyenv-virtualenv combines the best
of both worlds and manages multiple environments for multiple Python versions.

Create an environment: `pyenv virtualenv <version> <name>`, where `<version>` is optional,
but very strongly encouraged. The `<name>` is for you to keep them separate. A standard
practice is to name the environment the same as the project for which it was built.

Activate an environment: `pyenv local <name>`, this will generate/update the
`.python-version` file, which means the environment will be automatically activated when
you enter that directory.

To make a second version of Python available in an already active environment, you can
use the `local` command: `pyenv local <name> 3.9.10`. This will adjust the
`.python-version` file to automatically activate the version associated with the
`<name>` environment, but also make `python3.9` available as well.

## Tox
Tox allows you to use multiple virtual environments to perform testing in Python, thus
making it quite easy to:
 * Test against multiple versions of Python
 * Test against different dependency versions, i.e., numy, scipy, etc.
 * Capture any run setup steps and/or commands
 * Isolate environment variables
 * Do all of the above across Linux/Windows/MacOS
The tox approach presents a clean syntax which can be lifted and dropped into the CI
configuration, greatly reducing its necessary configuration (a potentially very
difficult task). Broadly speaking, tox will
 * Generate a series of virtual environments
 * Install dependencies for each environment
 * Run the setup commands for the package
 * Return the results from each environment to the user
The storage all takes place inside the `.tox` directory, so the repo does not become too
messy.

To install it, use pip: `pip install tox tox-pyenv`. The extra plugin allows tox to
recognize pyenv environments when searching for the proper Python version.

### Configuration
The magic happens in a configuration file. Tox will look in three locations,
prioritized in the following order:
 1. `pyproject.toml`
 2. `tox.ini`
 3. `setup.cfg`
Although, there is some debate about the merits of using `pyproject.toml`.

The `tox.ini` file takes the form of a config file, with `[sections]` and multiple
`key = value` entries per section:
```
# global settings
[tox]
envlist = my_env
skipsdist = true

# settings specific to the test environment, testenv is a reserved word
[testenv]
deps = pytest
commands = pytest
```
Comments can be included with the standard `# this is a comment`, but putting
comments on the same line as a `key = value` could lead to some hard-to-debug unwanted
behavior. `envlist` tells tox what environments to run when the `tox` command is issued.
In the above, the `my_env` environment will be stored in the `.tox` directory.
`skipsdist` is set to `true` when there is no `setup.py` file, otherwise an error will
occur. For the test environment, `deps` is the list of dependencies required to run
the tests, in the above it's just `pytest`. The `commands` value stores the command
that will be triggered as part of the run for a particular environment.

Tox is not tied to `pytest`, it could easily be configured to run your own bash
scripts or any arbitrary commands.

The best idea is to define package requirements in the `setup.py` file as well as
a `requirements.txt` file. This seems redundant, but the locations serve different
purposes; one for installing and one for building/deploying the actual package. The
`requirements.txt` file should be regarded as the necessary packages that any given
Python environment needs to build and run the package. Then the `deps` line would
simply read this file using: `deps = -rrequirements.txt`.

To run tox, simply type `tox` from the same directory as the `tox.ini` file. It should
build the environments and run the test commands.

The full `tox.ini` file is quite simple:
```
[tox]
envlist = 3.7.12,py38,py39,system

[testenv]
deps = -rrequirements.txt
install_command =
    pip install {opts} {packages}
commands =
    pytest tests/

passenv =
    PYTHONPATH
    FD_USE_FORTRAN
    FD_F90_COMPILER
    FD_EXTRA_COMPILE_FLAGS
    FD_LIBRARIES
    FD_LIBRARY_DIRS
    FD_INCLUDE_DIRS
```
Multiple Python versions are run by placing pyenv environment names in the `envlist`,
although the tox standard ones can also be used (`py38`, `py39`) provided the Python
executables can be found. To make multiple Python versions work in a single instance,
they must all be found in the `PATH`.
We can leverage pyenv to make the requested Python versions available, using
`pyenv local system system 3.7.12 3.8.12 3.9.10`. The first entry is considered the
default version to use. Now you can rerun `tox` and
it will show the entire test suite being run in all four environments.

The `install_command` is how the dependencies will be installed, this does not have
to be a `pip` command, although that is the default. Above lists a generic `pip install`,
but with the magic variables `{opts}` and `{packages}`, which are expanded by tox as
necessary. The command can involve multiple separate sub commands, one per line.
Similarly for the `commands` entry, each line represents a separate command that will
be executed; these tests are quite simple in that they only use pip and pytest, but
a custom command could be included, such as forcing a ML algorithm to train first
by calling a python script.

The `passenv` entry is a list of environment variables that will be passed from the
"host" environment into each testing environment.

The package does not need to be pre-built in order to run tox. Tox will end up building
the package for each environment anyway.

# Continuous Integration
Continuous Integration (CI) automates the integration of code changes from multiple
developers into a single project. Usually, it involves buliding the code, documentation,
running various tests and/or benchmarks. If anything fails, the proposed change will not
be included into the main branch. Version control is integral in the CI process.

## GitHub Actions
GitHub Actions (GH Actions) offers a free tier with about 500 minutes per week using Linux
OS, Windows will require about 2x the minutes to build and Mac OS will require about 10x
more minutes, so Linux is by far the cheapest OS to use for testing. You can develop a
build matrix to execute multiple builds in parallel, reducing the minutes you consume.
There is no support for GPU enabled builds and it is only available for GitHub repos.

## Circle CI
Circle CI has a free plan that include both public and private repos, but the free plan
will offer a limited number of credits. Credits are used to track the amount of resources
available to you. The credit rate is related to what OS you use
and the size of the virtual image on which your code will run; these are similar to NASA's
idea of the SBU, with different rates for different hardware systems. The free plan offers
roughly 2500 credits per week (about 250 minutes on a medium Linux OS). Windows builds will
require more credits (less minutes) and the free plan does not provide Mac OS builds.
Circle CI does not support as many languages as Travis CI. Circle CI can be integrated with
GitHub and Bitbucket. It does offer some GPU builds.

## Travis CI
Travis CI is free for public repos, but you must pay a monthly fee to use it with private
projects. There is support for quite a few different languages. It allows you to generate
a matrix of different build configurations that can be run concurrently. The plans are
more expensive compared to the pay plans of Circle CI

## Which One to Choose
If the goal is to learn CI, then the free plans are the only plans that should be under
consideration. Not all of my codes are public and including support for private repos would
be nice. GitHub does allow you to change repos from public to private and vice versa,
Bitbucket probably allows the same.

The free plan from Travis CI does not support private repos. Developing in private is not
necessarily required, but beneficial for some projects. Paying on the order of $50/month
is too much for just trying to learn CI.

The free plan from Circle CI can integrate with both GitHub and Bitbucket.
It also includes GPU builds, but does not provide Mac OS builds. The credits (minutes)
are adequate for personal development, but could become restrictive if multiple projects
use the same account balance.

GitHub actions provides more minutes as well as a single location for hosting code and
accessing the CI service. It does provide Mac OS, but no GPU builds.

## Configuration
GitHub Actions seems to be the best way forward, so we focus on its configuration and
setup.

# Documentation
This is best done using Sphinx (covered somewhere else, for now).

