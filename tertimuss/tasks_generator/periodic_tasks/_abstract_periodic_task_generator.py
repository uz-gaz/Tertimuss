import abc
from dataclasses import dataclass
from typing import List


@dataclass
class PeriodicGeneratedTask:
    # Fixed separation interval between the activation of any two consecutive jobs
    deadline: float

    # The longest execution time needed by a processor to complete the task without interruption over all possible input
    # data in cycles
    worst_case_execution_time: int


class AbstractPeriodicTaskGenerator(metaclass=abc.ABCMeta):
    """
    Task generator algorithm interface
    """

    @staticmethod
    @abc.abstractmethod
    def generate(utilization: float, tasks_deadlines: List[float], frequency: int, **kwargs) \
            -> List[PeriodicGeneratedTask]:
        """
        Generate a list of periodic tasks

        :param utilization: utilization of the task set
        :param tasks_deadlines: deadline of the tasks in seconds
        :param frequency: frequency used to calculate the worst case execution time of each task
        :param kwargs: algorithm dependant arguments
        """
        pass
