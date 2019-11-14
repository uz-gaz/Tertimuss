import math


def is_float_close(number_a: float, number_b: float, rtol: float = 1e-05, atol: float = 1e-08):
    return math.isclose(number_a, number_b, rel_tol=rtol, abs_tol=atol)
