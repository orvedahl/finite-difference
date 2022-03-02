from setuptools import find_packages
from numpy.distutils.core import setup, Extension

ext = Extension(name='finite_difference.fortran',
                sources=['src/finite_difference/fortran/fd.f90'],
                f2py_options=['--quiet'],
               )

setup(name='finite_difference',
      version='0.0.1',
      package_dir={"":"src"},
      packages=find_packages(where="src"),
      ext_modules=[ext])
