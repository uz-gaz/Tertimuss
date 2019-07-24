from random import randrange, uniform
from typing import List, Dict

from main.core.problem_specification.tasks_specification.PeriodicTask import PeriodicTask
from main.core.task_generator.template.AbstractTaskGeneratorAlgorithm import AbstractTaskGeneratorAlgorithm


class UUniFast(AbstractTaskGeneratorAlgorithm):

    def __init__(self):
        self.number_of_tasks = number_of_tasks
        self.utilization = utilization
        self.period_interval = period_interval
        self.processor_frequency = processor_frequency

    def generate(self, options: Dict[str, str]) -> List[PeriodicTask]:
        # random number in interval[a, b]
        # TODO: Obtain as parameter
        a = 6
        b = 20

        # Number of decimals of each return value
        # TODO: Obtain as parameter
        precision = 3

        t_i = [randrange(int(self.period_interval[0]), int(self.period_interval[1])) for _ in
               range(self.number_of_tasks)]
        e_i = [a + (b - a) * round(uniform(0, 1), precision) for _ in range(self.number_of_tasks)]

        sum_u = self.utilization  # the sum of n uniform random variables
        vector_u = self.number_of_tasks * [0]  # initialization

        for i in range(self.number_of_tasks - 1):
            next_sum_u = round(sum_u * round(uniform(0, 1) ** (1 / (self.number_of_tasks - 1 - i)), precision),
                               precision)
            vector_u[i] = sum_u - next_sum_u
            sum_u = next_sum_u

        vector_u[-1] = sum_u

        return [PeriodicTask(self.processor_frequency * vector_u[i] * t_i[i], t_i[i], e_i[i], None) for i in
                range(self.number_of_tasks)]
