from random import randrange, uniform
from typing import List, Dict

from main.core.problem_specification.tasks_specification.PeriodicTask import PeriodicTask
from main.core.task_generator.template.AbstractTaskGeneratorAlgorithm import AbstractTaskGeneratorAlgorithm


class UUniFast(AbstractTaskGeneratorAlgorithm):

    def generate(self, options: Dict) -> List[PeriodicTask]:
        """
        Generate a list of periodic tasks
        :param options: parameter to the algorithm
                        number_of_tasks: int -> Number of tasks
                        utilization: float -> utilization
                        min_period_interval: int -> min possible value of periods
                        max_period_interval: int -> max possible value of periods
                        processor_frequency: int -> max processor frequency in Hz
        :return: List of tasks
        """
        # Obtain options
        number_of_tasks = options["number_of_tasks"]
        utilization = options["utilization"]
        min_period_interval = options["min_period_interval"]
        max_period_interval = options["max_period_interval"]
        processor_frequency = options["processor_frequency"]

        # random number in interval[a, b]
        a = 6
        b = 20

        # Number of decimals of each return value
        precision = 3

        t_i = [randrange(int(min_period_interval), int(max_period_interval)) for _ in
               range(number_of_tasks)]
        e_i = [a + (b - a) * round(uniform(0, 1), precision) for _ in range(number_of_tasks)]

        sum_u = utilization  # the sum of n uniform random variables
        vector_u = number_of_tasks * [0]  # initialization

        for i in range(number_of_tasks - 1):
            next_sum_u = round(sum_u * round(uniform(0, 1) ** (1 / (number_of_tasks - 1 - i)), precision),
                               precision)
            vector_u[i] = sum_u - next_sum_u
            sum_u = next_sum_u

        vector_u[-1] = sum_u

        return [PeriodicTask(int(processor_frequency * vector_u[i] * t_i[i]), t_i[i], t_i[i], e_i[i]) for i in
                range(number_of_tasks)]
