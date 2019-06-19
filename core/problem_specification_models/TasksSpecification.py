from typing import Optional, List

import scipy


class Task(object):
    """
    Task specification
    """

    def __init__(self, c: float, t: float, e: Optional[float]):
        """
        :param c: Task worst case execution time in seconds at base frequency
        :param t: Task period, equal to deadline in seconds
        :param e: Energy consumption
        """
        self.c = c
        self.t = t
        self.e = e


class TasksSpecification(object):
    """
    System tasks
    """

    def __init__(self, tasks: List[Task]):
        """
        :param tasks: List of tasks
        """
        self.tasks = tasks
        self.h = scipy.lcm.reduce(list(map(lambda a: int(a.t), tasks)))  # Hyper period, TODO: Fix actual aproximation (int)
