import math
import random
from random import uniform
from typing import List, Dict

from main.core.problem_specification.tasks_specification.PeriodicTask import PeriodicTask
from main.core.problem_specification.automatic_task_generator.template.AbstractTaskGeneratorAlgorithm import \
    AbstractTaskGeneratorAlgorithm
from main.core.problem_specification.tasks_specification.TasksSpecification import TasksSpecification


class UUniFast(AbstractTaskGeneratorAlgorithm):
    """
    UUniFast task generation algorithm
    """

    def generate(self, options: Dict) -> List[PeriodicTask]:
        """
        Generate a list of periodic tasks
        :param options: parameter to the algorithm
                        number_of_tasks: int -> Number of tasks
                        utilization: float -> utilization
                        min_period_interval: int -> min possible value of periods in cycles
                        max_period_interval: int -> max possible value of periods in cycles
                        processor_frequency: int -> max processor frequency in Hz
                        hyperperiod: int -> hyperperiod in second
        :return: List of tasks
        """
        # Obtain options
        number_of_tasks = options["number_of_tasks"]
        utilization = options["utilization"]
        min_period_interval = options["min_period_interval"]
        max_period_interval = options["max_period_interval"]
        hyperperiod = options["hyperperiod"]
        processor_frequency = options["processor_frequency"]

        # Divisors of hyperperiod
        selected = [int(i) for i in self.divisor_generator(hyperperiod) if
                    min_period_interval <= i <= max_period_interval]
        t_i = random.choices(selected, k=number_of_tasks)

        # random number in interval[a, b]
        a = 6
        b = 20

        e_i = [a + (b - a) * uniform(0, 1) for _ in range(number_of_tasks)]

        sum_u = utilization  # the sum of n uniform random variables
        vector_u = number_of_tasks * [0]  # initialization

        for i in range(number_of_tasks - 1):
            next_sum_u = sum_u * (uniform(0, 1) ** (1 / (number_of_tasks - 1 - i)))
            vector_u[i] = sum_u - next_sum_u
            sum_u = next_sum_u

        vector_u[-1] = sum_u

        tasks_inst1 = [PeriodicTask(int(processor_frequency * vector_u[i] * t_i[i]) if int(
            processor_frequency * vector_u[i] * t_i[i]) > 0 else 1, t_i[i], t_i[i], e_i[i]) for i in
                       range(number_of_tasks)]

        hyperperiod_final = TasksSpecification(tasks_inst1).h

        cycles_in_hyperperiod = int(processor_frequency * hyperperiod_final * utilization)

        for i in tasks_inst1:
            c_in_hyperperiod = int(i.c * round(hyperperiod_final / i.d))
            cycles_in_hyperperiod = cycles_in_hyperperiod - c_in_hyperperiod

        if cycles_in_hyperperiod > 0:
            task_index = 0
            while cycles_in_hyperperiod != 0 and task_index < number_of_tasks:
                c_in_hyperperiod = int(tasks_inst1[task_index].c * round(hyperperiod_final / tasks_inst1[task_index].d))
                cycles_left_in_hyperperiod = processor_frequency * hyperperiod_final - c_in_hyperperiod
                if cycles_left_in_hyperperiod > cycles_in_hyperperiod:
                    cycles_left_in_hyperperiod = cycles_in_hyperperiod

                tasks_inst1[task_index].c += int(
                    cycles_left_in_hyperperiod / round(hyperperiod_final / tasks_inst1[task_index].d))

                cycles_in_hyperperiod = cycles_in_hyperperiod - int(
                    cycles_left_in_hyperperiod / round(hyperperiod_final / tasks_inst1[task_index].d)) * round(
                    hyperperiod_final / tasks_inst1[task_index].d)

                task_index = task_index + 1

        if cycles_in_hyperperiod < 0:
            task_index = 0
            while cycles_in_hyperperiod != 0 and task_index < number_of_tasks:
                c_in_hyperperiod = int(
                    (tasks_inst1[task_index].c - 1) * round(hyperperiod_final / tasks_inst1[task_index].d))
                if c_in_hyperperiod > cycles_in_hyperperiod:
                    c_in_hyperperiod = cycles_in_hyperperiod

                tasks_inst1[task_index].c -= int(
                    c_in_hyperperiod / round(hyperperiod_final / tasks_inst1[task_index].d))

                cycles_in_hyperperiod = cycles_in_hyperperiod - int(
                    c_in_hyperperiod / round(hyperperiod_final / tasks_inst1[task_index].d)) * round(
                    hyperperiod_final / tasks_inst1[task_index].d)

                task_index = task_index + 1

        return tasks_inst1

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
