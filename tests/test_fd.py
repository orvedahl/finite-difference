import pytest
import numpy as np
import finite_difference.fd as pFD
import finite_difference.fortran as fFD

using_pytest = True

def test_fd2():
    name = "FD2"
    n = 256
    tol = 0.01 # expect error ~= 0.008 when n=256

    # define grid, function and true derivative
    x = np.linspace(-1, 1, num=n, endpoint=True)
    f = np.cos(3*np.pi*x) + 3.0
    true = -3*np.pi*np.sin(3*np.pi*x)

    # Package_name.Module_name.Function_name
    dfdx_py = pFD.fd2(x,f)

    # Extension_name is defined in setup.py as Package_name.fortran
    dfdx_f90 = fFD.fd.fd2(x,f) # Extension_name.Module_name.Function_name

    py_err = np.max(np.abs(true - dfdx_py))
    f90_err = np.max(np.abs(true - dfdx_f90))

    passing = (py_err < tol) and (f90_err < tol)

    if (using_pytest):
        assert passing
    else:
        print("{} --- {}".format(name, passing))

def test_convergence_fd2():
    name = "FD2 convergence"
    Nref = 64
    N = [128, 256, 512]

    # build grid, function, and true deriv
    def funcs(n):
        x = np.linspace(-1, 1, num=n, endpoint=True)
        f = np.cos(np.pi*x) + 3.0
        true = -np.pi*np.sin(np.pi*x)
        return x, f, true

    def error(x,y):
        return np.max(np.abs(x-y))

    # compute reference state
    xref, fref, fpref = funcs(Nref)
    py = pFD.fd2(xref, fref)
    f90 = fFD.fd.fd2(xref, fref)
    py_err_ref = error(py, fpref)
    f90_err_ref = error(f90, fpref)

    # compute errors for the rest of the resolutions
    perrors = []; ferrors = []
    for n in N:
        xref, fref, fpref = funcs(n)
        py = pFD.fd2(xref, fref)
        f90 = fFD.fd.fd2(xref, fref)
        perr = error(py, fpref)
        ferr = error(f90, fpref)

        perrors.append(perr)
        ferrors.append(ferr)

    # normalize errors by reference
    perrors = py_err_ref / np.array(perrors)
    ferrors = f90_err_ref / np.array(ferrors)

    # second order should show a factor of 4 decrease in error
    # for every increase in resolution by 2
    Nres = len(N)
    norm = 4**np.arange(1,Nres+1)

    pnorm = perrors / norm
    fnorm = ferrors / norm

    tol = 0.04
    passing = np.allclose(pnorm, 1, atol=tol) and np.allclose(fnorm, 1, atol=tol)

    if (using_pytest):
        assert passing
    else:
        print("{} --- {}".format(name, passing))

if __name__ == "__main__":
    using_pytest = False
    test_fd2()
    test_convergence_fd2()

