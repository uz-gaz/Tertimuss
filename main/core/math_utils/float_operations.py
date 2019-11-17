import math
from typing import List

import scipy


def is_equal(number_a: float, number_b: float, rtol: float = 1e-03, atol: float = 1e-05):
    return math.isclose(number_a, number_b, rel_tol=rtol, abs_tol=atol)


# True if number_a <= number_b
def is_less_or_equal_than(number_a: float, number_b: float, rtol: float = 1e-03, atol: float = 1e-05):
    return number_a < number_b or is_equal(number_a, number_b, rtol, atol)


# Taken from https://stackoverflow.com/questions/45323619/python-greatest-common-divisor-gcd-for-floats-preferably-in-numpy
def __float_gcd(a: float, b: float, rtol: float = 1e-03, atol: float = 1e-05) -> float:
    t = min(abs(a), abs(b))
    while abs(b) > rtol * t + atol:
        a, b = b, a % b
    return a


def float_gcd(numbers: List[float], rtol=1e-03, atol=1e-05) -> float:
    if len(numbers) > 0:
        gcd_accumulated = numbers[0]
        for number in numbers[1:]:
            gcd_accumulated = __float_gcd(gcd_accumulated, number, rtol, atol)
        return gcd_accumulated
    else:
        return 1


def float_lcm(numbers: List[float], rtol=1e-03, atol=1e-05) -> float:
    lcm = scipy.lcm.reduce([int(i / atol) for i in numbers])
    return lcm * atol
