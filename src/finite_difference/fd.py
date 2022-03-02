import numpy as np

def fd2(x, f):
    """
    2nd order centered derivative of f with respect to x. f is assumed 1D.
    """
    nx = len(x)
    dfdx = np.zeros_like(f)

    # interior points
    for i in range(1,nx-1):
        dx01 = x[i-1] - x[i]; dx10 = x[i+1] - x[i]
        num = dx01**2*f[i+1] + (dx10**2-dx01**2)*f[i] - dx10**2*f[i-1]
        den = dx10*dx01*(dx01-dx10)
        dfdx[i] = num/den

    # left/right boundary points
    dfdx[0]    = one_sided_fd2(x[:3], f[:3])
    dfdx[nx-1] = one_sided_fd2(x[-3:], f[-3:], right_edge=True)

    return dfdx

def one_sided_fd2(x, f, right_edge=False):
    """
    One sided 2nd order derivative. The first element of x is assumed to be the
    left boundary and the second element of x is the first interior point. If
    right_edge=True, then the last element of x is right edge and the second to
    last element is the first interior point.
    """
    if (right_edge):
        x = x[::-1]; f = f[::-1]

    dx20 = x[2] - x[0]; dx10 = x[1] - x[0]; dx21 = x[2] - x[1]
    num = dx20**2*f[1] - dx10**2*f[2] + (dx10**2 - dx20**2)*f[0]
    den = dx10*dx20*dx21

    return num/den

