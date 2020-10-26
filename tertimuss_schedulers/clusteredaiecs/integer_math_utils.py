import functools
import math
from typing import List


def list_lcm(values: List[int]) -> int:
    return round(functools.reduce(lambda a, b: abs(a * b) // math.gcd(a, b), values))


def get_number_divisors(number: int):
    return [actual_divisor for actual_divisor in range(1, number + 1) if number % actual_divisor == 0]
