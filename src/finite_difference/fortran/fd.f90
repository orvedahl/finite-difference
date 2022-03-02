module fd

  implicit none

  contains

  subroutine fd2(n, x, f, dfdx)
    integer, intent(in) :: n
    double precision, intent(in) :: x(0:n-1), f(0:n-1)
    double precision, intent(out) :: dfdx(0:n-1)

    integer :: i
    double precision :: dx01, dx10, num, den

    ! interior points
    do i=1,n-2
      dx01 = x(i-1) - x(i)
      dx10 = x(i+1) - x(i)
      num = dx01**2 * f(i+1) + (dx10**2 - dx01**2)*f(i) - dx10**2*f(i-1)
      den = dx10*dx01*(dx01 - dx10)
      dfdx(i) = num/den
    enddo

    ! boundary points
    call one_sided_fd2(x(0:2), f(0:2), dfdx(0), .false.)
    call one_sided_fd2(x(n-3:n-1), f(n-3:n-1), dfdx(n-1), .true.)

  end subroutine fd2

  subroutine one_sided_fd2(x, f, dfdx, right_edge)
    double precision, intent(in) :: x(0:2), f(0:2)
    double precision, intent(out) :: dfdx
    logical, intent(in), optional :: right_edge

    integer :: zero, one, two
    double precision :: dx20, dx10, dx21, num, den

    ! do the left edge by default:
    !   x     x     x     ...interior points...
    !   zero  one   two
    zero = 0
    one = 1
    two = 2

    if (present(right_edge)) then
      if (right_edge) then
        ! do the right edge
        !   ...interior points...   x     x     x
        !                           two   one   zero
        zero = 2
        one = 1
        two = 0
      endif
    endif

    dx20 = x(two) - x(zero)
    dx10 = x(one) - x(zero)
    dx21 = x(two) - x(one)

    num = dx20**2*f(one) - dx10**2*f(two) + (dx10**2 - dx20**2)*f(zero)
    den = dx10*dx20*dx21

    dfdx = num/den

  end subroutine one_sided_fd2

end module fd

