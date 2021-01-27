from typing import List

from .._abstract_periodic_task_generator import PeriodicGeneratedTask, AbstractPeriodicTaskGenerator
from ._uunifast import UUniFast


class UUniFastDiscard(AbstractPeriodicTaskGenerator):
    """
    UUniFast Discard task generation algorithm
    """

    @staticmethod
    def generate(utilization: float, tasks_deadlines: List[float], processor_frequency: int, **kwargs) \
            -> List[PeriodicGeneratedTask]:
        have_to_be_discarded = True
        task_set = []

        while have_to_be_discarded:
            task_set = UUniFast.generate(utilization, tasks_deadlines.copy(), processor_frequency)
            have_to_be_discarded = any([round(
                i.deadline * processor_frequency) < i.worst_case_execution_time or i.worst_case_execution_time <= 0 for
                                        i in task_set])
        return task_set
