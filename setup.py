from setuptools import find_packages
from numpy.distutils.core import setup, Extension

import io
import sys
import os
import os.path as osp
from configparser import ConfigParser
from glob import glob

def process_path(path):
    """
    adjust path by expanding variables and "~" characters
    """
    p = osp.expanduser(path) # expand "~"
    p = osp.abspath(p)       # normalize the path, ./src/../ --> ./
    p = osp.expandvars(p)    # expand environment variables
    return p

def read(*names, **kwargs):
    """
    read a file, names holds the split path, i.e., all subdirectories
    as well as the filename, but no separation characters (e.g., "/")
    """
    with io.open(osp.join(osp.dirname(__file__), *names),
                 encoding=kwargs.get('encoding', 'utf8')) as fh:
        return fh.read()

def get_version(*path):
    """
    parse the source code for the version number
    """
    version = ""
    for line in read(*path).splitlines():
        if line.lstrip().startswith("__version__"):
            version = (line.split("=")[1]).strip()
            break

    # strip off the start/end quotes
    if (version.startswith('"') or version.startswith("'")):
        version = version[1:-1]

    return version

# package name and source tree may be different
package_name = "finite_difference"

version = get_version("src", "finite_difference", "_version.py")

options = {}

# meta data
options['name'] = package_name
options['author'] = 'Ryan Orvedahl'
options['author_email'] = 'ryan.orvedahl@gmail.com'
options['version'] = version
options['url'] = 'https://github.com/orvedahl/finite-difference'
options['project_urls'] = {'Issue Tracker':
                           'https://github.com/orvedahl/finite-difference/issues'}
options['license'] = 'GNU GPLv3;'

# descriptions
options['description'] = 'Explore best practices with package deployment'
options['long_description'] = read('README.md')
options['long_description_content_type'] = 'text/markdown'
options['keywords'] = ['python', 'template', 'CI', 'learning']

# where to find packages/modules
options['packages'] = find_packages(where="src")
options['package_dir'] = {"":"src"}
options['py_modules'] = [osp.splitext(osp.basename(p))[0] for p in glob("src/**/*.py")]

# requirements, be careful listing minimum versions
options['python_requires'] = '>=3.6'
options['install_requires'] = ['docopt',
                               'numpy>=1.19',
                               'pytest',
                               'pytest-cov',
                               'pytest-benchmark']

# define default options that can be changed by user
defaults = {}
defaults['build_f90'] = "true"
defaults['compiler']  = "gcc" # GCC
defaults['flags']     = "-O3"
defaults['libraries'] = ""
defaults['lib_dirs']  = ""
defaults['includes']  = ""

# extract user defined options
build_f90 = os.getenv("FD_USE_FORTRAN", defaults["build_f90"])
compiler  = os.getenv("FD_F90_COMPILER", defaults["compiler"])
flags     = os.getenv("FD_EXTRA_COMPILE_FLAGS", defaults["flags"]).split()
libraries = os.getenv("FD_LIBRARIES", defaults["libraries"]).split()
lib_dirs  = os.getenv("FD_LIBRARY_DIRS", defaults["lib_dirs"]).split()
includes  = os.getenv("FD_INCLUDE_DIRS", defaults["includes"]).split()

# some options require a bit more processing
if ("1" in build_f90 or "true" in build_f90.lower()):
    build_f90 = True
else:
    build_f90 = False

if ("gcc" in compiler.lower() or "gnu" in compiler.lower()): # convert to F2PY language
    compiler = "gnu95"
elif ("intel" in compiler.lower()):
    compiler = "intelem"
else:
    raise ValueError("Unrecognized compiler = {}".format(compiler))

lib_dirs = [process_path(d) for d in lib_dirs]
includes = [process_path(d) for d in includes]

# this seems to be the most robust way to change the compiler
sys.argv.extend(["config_fc", "--fcompiler={}".format(compiler)])

# build Extension objects for the Fortran codes
ext = Extension(name='finite_difference.fortran',
                sources=['src/finite_difference/fortran/fd.f90'],
                f2py_options=['--quiet', # run quietly
                             ],
                libraries=libraries,
                library_dirs=lib_dirs,
                include_dirs=includes,
                extra_f90_compile_args=flags,
                extra_compile_args=flags,
                extra_link_args=flags
               )

extensions = [ext]

if (build_f90):
    options['ext_modules'] = extensions

# build/deploy/compile the package
setup(**options)

