import abc
from typing import Optional, List


class AbstractDeadlineGenerator(metaclass=abc.ABCMeta):
    @staticmethod
    @abc.abstractmethod
    def generate(number_of_tasks: int, min_deadline: float, max_deadline: float, major_cycle: Optional[float],
                 **kwargs) -> List[float]:
        """
        Generate deadlines for tasks

        :param number_of_tasks: Number of tasks
        :param min_deadline: The minimum deadline
        :param max_deadline: The maximum deadline
        :param major_cycle: The major cycle
        :param kwargs: Algorithm dependant arguments
        :return: List of deadlines
        """
        pass
