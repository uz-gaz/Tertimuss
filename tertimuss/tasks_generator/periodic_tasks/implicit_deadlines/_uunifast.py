from random import uniform
from typing import List

from tertimuss.simulation_lib.math_utils import list_float_lcm
from .._abstract_periodic_task_generator import PeriodicGeneratedTask, AbstractPeriodicTaskGenerator


class UUniFast(AbstractPeriodicTaskGenerator):
    """
    UUniFast task generation algorithm
    """

    @staticmethod
    def generate(utilization: float, tasks_deadlines: List[float], processor_frequency: int, **kwargs) \
            -> List[PeriodicGeneratedTask]:
        """
        Generate a list of periodic tasks

        :param utilization: utilization of the task set
        :param tasks_deadlines: deadline of the tasks in seconds
        :param processor_frequency: frequency used to calculate the worst case execution time of each task
        :param kwargs: algorithm dependant arguments
        """
        # Major cycle
        major_cycle = round(list_float_lcm(tasks_deadlines))
        total_cycles = round(major_cycle * utilization * processor_frequency)
        number_of_tasks = len(tasks_deadlines)

        # Utilization
        sum_u = utilization  # the sum of n uniform random variables

        cc_i: List[int] = []

        tasks_deadlines = sorted(tasks_deadlines)

        for i in range(number_of_tasks - 1):
            next_sum_u = sum_u * (uniform(0, 1) ** (1 / (number_of_tasks - 1 - i)))
            task_cycles_actual = round(processor_frequency * (sum_u - next_sum_u) * tasks_deadlines[i])
            cc_i.append(task_cycles_actual)
            sum_u = next_sum_u
            total_cycles = total_cycles - (task_cycles_actual * (major_cycle // tasks_deadlines[i]))

        if total_cycles % int(round(major_cycle / tasks_deadlines[-1])) == 0:
            cc_i.append(total_cycles // int(round(major_cycle / tasks_deadlines[-1])))
        else:
            cc_i.append(total_cycles)
            tasks_deadlines[-1] = major_cycle

        return [PeriodicGeneratedTask(worst_case_execution_time=cc, deadline=t) for (cc, t) in
                zip(cc_i, tasks_deadlines)]
