from typing import List

from .._abstract_periodic_task_generator import PeriodicGeneratedTask, PeriodicTaskGenerator
from ._uunifast import PTGUUniFast


class PTGUUniFastDiscard(PeriodicTaskGenerator):
    """
    UUniFast Discard task generation algorithm
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
        have_to_be_discarded = True
        task_set = []

        while have_to_be_discarded:
            task_set = PTGUUniFast.generate(utilization, tasks_deadlines.copy(), processor_frequency)
            have_to_be_discarded = any([round(
                i.deadline * processor_frequency) < i.worst_case_execution_time or i.worst_case_execution_time <= 0 for
                                        i in task_set])
        return task_set
