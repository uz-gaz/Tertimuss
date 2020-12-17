import functools
import math
from typing import List


def is_equal(number_a: float, number_b: float, rtol: float = 1e-03, atol: float = 1e-05):
    return math.isclose(number_a, number_b, rel_tol=rtol, abs_tol=atol)


# True if number_a <= number_b
def is_less_or_equal_than(number_a: float, number_b: float, rtol: float = 1e-03, atol: float = 1e-05):
    return number_a < number_b or is_equal(number_a, number_b, rtol, atol)


def list_float_lcm(numbers: List[float], atol=1e-05) -> float:
    return functools.reduce(lambda a, b: abs(a * b) // math.gcd(a, b), [round(i / atol) for i in numbers]) * atol


def list_float_gcd(numbers: List[float], atol=1e-05) -> float:
    return functools.reduce(lambda a, b: math.gcd(a, b), [round(i / atol) for i in numbers]) * atol


def list_int_lcm(values: List[int]) -> int:
    return functools.reduce(lambda a, b: abs(a * b) // math.gcd(a, b), values)


def list_int_gcd(values: List[int]) -> int:
    return functools.reduce(lambda a, b: math.gcd(a, b), values)
