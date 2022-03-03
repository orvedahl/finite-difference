from setuptools import find_packages
from numpy.distutils.core import setup, Extension

import io
import sys
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
                               'tox',
                               'pytest',
                               'pytest-cov',
                               'pytest-benchmark']

# extract information from the configure file
config = ConfigParser()
config.read("fdiff.cfg")
section = "compiler-info"
build_f90 = config.getboolean(section, "INCLUDE_FORTRAN")
compiler  = config.get(section, "F90_COMPILER")
flags     = config.get(section, "EXTRA_COMPILE_FLAGS").split()
libraries = config.get(section, "LIBRARIES").split()
lib_dirs  = config.get(section, "LIBRARY_DIRS").split()
includes  = config.get(section, "INCLUDE_DIRS").split()

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
