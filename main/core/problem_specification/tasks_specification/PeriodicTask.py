from typing import Optional

from main.core.problem_specification.tasks_specification.Task import Task


class PeriodicTask(Task):
    """
    Periodic task specification
    """

    def __init__(self, c: int, t: float, d: float, e: Optional[float]):
        """
        :param c: Task worst case execution time in cycles
        :param t: Task period in seconds
        :param d: Task deadline in seconds
        :param e: Energy consumption
        """
        super().__init__(c, e)
        self.t: float = t
        self.d: float = d
