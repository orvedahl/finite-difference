#
# Customize the compiler options by setting the appropriate
# environment variables then source this shell using:
#     source user_options.sh
#

# build the project with Fortran support (true)
export FD_USE_FORTRAN="true"

# specify the compiler vendor that f2py should use. to see available ones:
#     f2py -c --help-fcompiler
# common options include:
#     gcc
#     intel
export FD_F90_COMPILER="intel"

# set custom flags, such as architecture optimizations
export FD_EXTRA_COMPILE_FLAGS="-O3 -xavx2"

# space-separated list of libraries to use, without the leading "-l"
export FD_LIBRARIES="mkl_intel_ilp64 mkl_sequential mkl_core"

# space-separated list of library directories to use
export FD_LIBRARY_DIRS="${MKLROOT}/lib/intel64"

# space-separated list of include directories to use
export FD_INCLUDE_DIRS="${MKLROOT}/include"

