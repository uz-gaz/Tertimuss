import math


def is_equal(number_a: float, number_b: float, rtol: float = 1e-05, atol: float = 1e-08):
    return math.isclose(number_a, number_b, rel_tol=rtol, abs_tol=atol)


# True if number_a <= number_b
def is_less_or_equal_than(number_a: float, number_b: float, rtol: float = 1e-05, atol: float = 1e-08):
    return number_a < number_b or is_equal(number_a, number_b, rtol, atol)
