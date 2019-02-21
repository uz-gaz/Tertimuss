import numpy as np


class TasksSpecification(object):

    def __init__(self, tasks: list):
        self.tasks = tasks  # tasks
        self.h = np.lcm.reduce(list(map(lambda a: a.t, tasks)))  # Hyper period


class Task(object):

    def __init__(self, c: float, t: int, e: float):
        self.c = c  # Task WCET
        self.t = t  # Task period
        self.e = e  # Energy consumption
        # TODO: Add Task deadline
