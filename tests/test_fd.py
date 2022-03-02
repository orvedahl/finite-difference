import numpy as np
import finite_difference.fd as py_fd
import finite_difference.fortran as f90_fd # name of Extension

def test_fd2():
    tol = 1e-2
    n = 256
    x = np.linspace(-1, 1, num=n, endpoint=True)

    f = np.cos(3*np.pi*x) + 3.0
    true = -3*np.pi*np.sin(3*np.pi*x)

    dfdx_py = py_fd.fd2(x,f)
    dfdx_f90 = f90_fd.fd.fd2(x,f) # Extension_name.Module_name.Subroutine_name

    py_err = np.max(np.abs(true - dfdx_py))
    f90_err = np.max(np.abs(true - dfdx_f90))

    print("Python error : {}".format(py_err))
    print("Fortran error: {}".format(f90_err))

    passing = (py_err < tol) and (f90_err < tol)

    print(passing)
    #return passing

if __name__ == "__main__":
    test_fd2()

