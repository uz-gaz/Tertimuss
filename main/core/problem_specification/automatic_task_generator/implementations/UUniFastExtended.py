import math
import random
from random import uniform
from typing import List, Dict

from main.core.problem_specification.tasks_specification.PeriodicTask import PeriodicTask
from main.core.problem_specification.automatic_task_generator.template.AbstractTaskGeneratorAlgorithm import \
    AbstractTaskGeneratorAlgorithm


class UUniFastExtended(AbstractTaskGeneratorAlgorithm):
    """
    UUniFast task generation algorithm
    """

    def generate(self, options: Dict) -> List[PeriodicTask]:
        """
        Generate a list of periodic tasks
        :param options: parameter to the algorithm
                        number_of_tasks: int -> Number of tasks
                        utilization: float -> utilization
                        wcet_multiple: int -> all wcet will be multiple of this
                        processor_frequency: int -> max processor frequency in Hz
                        hyperperiod: int -> hyperperiod in second
        :return: List of tasks
        """
        # Obtain options
        number_of_tasks = options["number_of_tasks"]
        utilization = options["utilization"]
        hyperperiod = options["hyperperiod"]
        wcet_multiple = options["wcet_multiple"]
        processor_frequency = options["processor_frequency"]

        if (utilization * processor_frequency) % wcet_multiple != 0:
            print("Some tasks can't be multiple in automatic generation")
            return []

        cycles_to_plan = round((hyperperiod * utilization * processor_frequency) / wcet_multiple)

        # Divisors of hyperperiod
        possible_task_periods = [int(i) for i in self.divisor_generator(hyperperiod)]
        t_i = random.choices(possible_task_periods, k=number_of_tasks)

        # random number in interval[a, b]
        a = 6
        b = 20

        e_i = [a + (b - a) * uniform(0, 1) for _ in range(number_of_tasks)]

        remaining_u = utilization  # the sum of n uniform random variables
        tasks_cycles = number_of_tasks * [0]  # initialization
        tasks_cycles_left = cycles_to_plan

        for i in range(number_of_tasks - 1):
            # Obtain task utilization by UUnifast
            task_utilization = remaining_u - remaining_u * (uniform(0, 1) ** (1 / (number_of_tasks - 1 - i)))

            # Obtain task cycles
            task_cycles = round(t_i[i] * task_utilization * (processor_frequency / wcet_multiple))

            # The minimum number of execution cycles is 1
            task_cycles = 1 if task_cycles == 0 else task_cycles

            # Save the task cycle
            tasks_cycles[i] = task_cycles

            # Compute the task cycles_left
            tasks_cycles_left -= (task_cycles * round(hyperperiod / t_i[i]))

            # Remaining utilization
            remaining_u = tasks_cycles_left / cycles_to_plan

        if 0 >= tasks_cycles_left:
            # We haven't enough cycles for the last task
            max_pos = tasks_cycles.index(max(tasks_cycles))
            tasks_cycles[max_pos] -= 1
            tasks_cycles_left = round(hyperperiod / t_i[max_pos])

        # elif 0 < tasks_cycles_left <= processor_frequency / wcet_multiple:
        #     # We haven't enough cycles for the last task
        #     pass

        possible_periods_last_task = [period for period in possible_task_periods if
                                      tasks_cycles_left % round(hyperperiod / period) == 0]

        last_task_period = min(possible_periods_last_task)

        tasks_cycles[-1] = round(tasks_cycles_left / round(hyperperiod / last_task_period))
        t_i[-1] = last_task_period

        # Check if task creation is correct
        if sum([tasks_cycles[i] * (hyperperiod / t_i[i]) for i in range(number_of_tasks)]) != cycles_to_plan:
            print("Tasks creation have fail")
            return []

        return [PeriodicTask(tasks_cycles[i] * wcet_multiple, t_i[i], t_i[i], e_i[i]) for i in range(number_of_tasks)]

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
