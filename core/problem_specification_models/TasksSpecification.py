from typing import Optional, List

import scipy


class Task(object):
    """
    Task specification
    """

    def __init__(self, c: int, t: int, e: Optional[float]):
        """
        :param c: Task worst case execution time in CPU cycles
        :param t: Task period, equal to deadline in CPU cycles with CPU frequency equal to base frequency
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
        self.h = scipy.lcm.reduce(list(map(lambda a: a.t, tasks)))  # Hyper period
