![Tests](https://github.com/orvedahl/finite-difference/actions/workflows/main.yml/badge.svg)

# Finite Differences

A very simple finite difference package, whose main purpose is to explore/refine/learn
various best-practices related to Python packages. Finite differences are easy to code/test
and can easily be ported to Fortran/C in order to include f2py/cython support.

These are not production Python routines, the emphasis is on the package building
process. This repo should be used as a guide for building better packages.

Many of the ideas are borrowed from the template: https://github.com/nschloe/pyfoobar

Topics to explore:

 * general setup.py
 * automated testing
 * continuous integration
   * github actions
   * travis ci
   * circle ci
 * badges on github?
 * random odds and ends
   * test coverage, i.e., codecov
   * tox
   * just (https://github.com/casey/just) or a basic shell script?

