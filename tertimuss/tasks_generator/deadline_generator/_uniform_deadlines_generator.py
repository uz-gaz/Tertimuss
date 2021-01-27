import math
import random
from typing import List

from ._abstract_deadlines_generator import AbstractDeadlineGenerator


def _divisor_generator(n: int):
    large_divisors = []
    for i in range(1, int(math.sqrt(n) + 1)):
        if n % i == 0:
            yield i
            if i * i != n:
                large_divisors.append(n / i)
    for divisor in reversed(large_divisors):
        yield divisor


class UniformIntegerDeadlineGenerator(AbstractDeadlineGenerator):
    @staticmethod
    def generate(number_of_tasks: int, min_deadline: float, max_deadline: float, major_cycle: float,
                 **kwargs) -> List[float]:
        """
        Generate deadlines for tasks
        :param number_of_tasks: Number of tasks
        :param min_deadline: Minimum deadline
        :param max_deadline: Maximum deadline
        :param major_cycle: Major cycle
        :param kwargs: Algorithm dependant arguments
        :return: List of deadlines
        """
        possible_deadlines = [int(i) for i in _divisor_generator(int(major_cycle)) if min_deadline <= i <= max_deadline]
        return random.choices(possible_deadlines, k=number_of_tasks)
