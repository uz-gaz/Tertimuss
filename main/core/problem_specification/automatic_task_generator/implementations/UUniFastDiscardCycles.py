from typing import Dict, List

from main.core.problem_specification.automatic_task_generator.implementations.UUniFastCycles import UUniFastCycles
from main.core.problem_specification.tasks_specification.PeriodicTask import PeriodicTask


class UUniFastDiscardCycles(UUniFastCycles):
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
        have_to_be_discarded = True
        task_set = []

        while have_to_be_discarded:
            task_set = super().generate(options)
            processor_frequency = options["processor_frequency"]
            have_to_be_discarded = any([round(i.d * processor_frequency) < i.c for i in task_set])

        return task_set
