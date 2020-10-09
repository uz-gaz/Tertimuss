import functools
import math
import random
from random import uniform
from typing import List, Dict

from main.core.problem_specification.tasks_specification.PeriodicTask import PeriodicTask
from main.core.problem_specification.automatic_task_generator.template.AbstractTaskGeneratorAlgorithm import \
    AbstractTaskGeneratorAlgorithm


class UUniFastCycles(AbstractTaskGeneratorAlgorithm):
    """
    UUniFast task generation algorithm
    """

    @staticmethod
    def list_lcm(values: List[int]) -> int:
        return functools.reduce(lambda a, b: abs(a * b) // math.gcd(a, b), values)

    def generate(self, options: Dict) -> List[PeriodicTask]:
        """
        Generate a list of periodic tasks
        :param options: parameter to the algorithm
                        number_of_tasks: int -> Number of tasks
                        utilization: float -> utilization
                        min_period_interval: int -> min possible value of periods in cycles
                        max_period_interval: int -> max possible value of periods in cycles
                        processor_frequency: int -> max processor frequency in Hz
        :return: List of tasks
        """
        # Obtain options
        number_of_tasks = options["number_of_tasks"]
        utilization = options["utilization"]
        min_period_interval = options["min_period_interval"]
        max_period_interval = options["max_period_interval"]
        processor_frequency = options["processor_frequency"]

        # Divisors of major cycle
        t_i = random.choices(list(range(min_period_interval, max_period_interval + 1)), k=number_of_tasks)

        # Major cycle
        major_cycle = round(self.list_lcm(t_i))

        total_cycles = round(major_cycle * utilization * processor_frequency)

        # Utilization
        sum_u = utilization  # the sum of n uniform random variables

        cc_i: List[int] = []

        for i in range(number_of_tasks - 1):
            next_sum_u = sum_u * (uniform(0, 1) ** (1 / (number_of_tasks - 1 - i)))
            task_cycles_actual = round(processor_frequency * (sum_u - next_sum_u) * t_i[i])
            cc_i.append(task_cycles_actual)
            sum_u = next_sum_u
            total_cycles = total_cycles - (task_cycles_actual * (major_cycle // t_i[i]))

        cc_i.append(total_cycles)

        return [PeriodicTask(cc, float(t), float(t), 1.0) for (cc, t) in zip(cc_i, t_i)]

    @staticmethod
    def divisor_generator(n):
        large_divisors = []
        for i in range(1, int(math.sqrt(n) + 1)):
            if n % i == 0:
                yield i
                if i * i != n:
                    large_divisors.append(n / i)
        for divisor in reversed(large_divisors):
            yield divisor
