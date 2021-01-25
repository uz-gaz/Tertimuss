"""
This module provide math tools
"""
import functools
import math
from typing import List


def is_equal(number_a: float, number_b: float, rtol: float = 1e-03, atol: float = 1e-05):
    """
    Check if two float number are nearly equals
    :param number_a: first number
    :param number_b: second number
    :param rtol: relative tolerance
    :param atol: absolute tolerance
    :return: true if numbers are nearly equals
    """
    return math.isclose(number_a, number_b, rel_tol=rtol, abs_tol=atol)


def is_less_or_equal_than(number_a: float, number_b: float, rtol: float = 1e-03, atol: float = 1e-05):
    """
    Check if number_a <= number_b being booth floats
    :param number_a: first number
    :param number_b: second number
    :param rtol: relative tolerance
    :param atol: absolute tolerance
    :return: true if number_a <= number_b
    """
    return number_a < number_b or is_equal(number_a, number_b, rtol, atol)


def list_float_lcm(numbers: List[float], atol=1e-05) -> float:
    """
    Obtain the less common multiple of a list of floats
    :param numbers: number list
    :param atol: absolute tolerance
    :return: less common multiple
    """
    return functools.reduce(lambda a, b: abs(a * b) // math.gcd(a, b), [round(i / atol) for i in numbers]) * atol


def list_float_gcd(numbers: List[float], atol=1e-05) -> float:
    """
    Obtain the great common divisor of a list of floats
    :param numbers: number list
    :param atol: absolute tolerance
    :return: great common divisor
    """
    return functools.reduce(lambda a, b: math.gcd(a, b), [round(i / atol) for i in numbers]) * atol


def list_int_lcm(numbers: List[int]) -> int:
    """
    Obtain the less common multiple of a list of integers
    :param numbers: number list
    :return: less common multiple
    """
    return functools.reduce(lambda a, b: abs(a * b) // math.gcd(a, b), numbers)


def list_int_gcd(numbers: List[int]) -> int:
    """
    Obtain the great common divisor of a list of integers
    :param numbers: number list
    :return: great common divisor
    """
    return functools.reduce(lambda a, b: math.gcd(a, b), numbers)
