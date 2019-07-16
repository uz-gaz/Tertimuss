from typing import Optional, List

import scipy


class Task(object):
    """
    Task specification
    """

    def __init__(self, c: float, e: Optional[float]):
        """
        :param c: Task worst case execution time in seconds at base frequency
        :param e: Energy consumption
        """
        self.c: float = c
        self.e: Optional[float] = e


class PeriodicTask(Task):
    """
    Periodic task specification
    """

    def __init__(self, c: float, t: float, d: float, e: Optional[float]):
        """
        :param c: Task worst case execution time in seconds at base frequency
        :param t: Task period in seconds
        :param d: Task deadline in seconds
        :param e: Energy consumption
        """
        super().__init__(c, e)
        self.t: float = t
        self.d: float = d


class AperiodicTask(Task):
    """
    Aperiodic task specification
    """

    def __init__(self, c: float, a: float, d: float, e: Optional[float]):
        """
        :param c: Task worst case execution time in seconds at base frequency
        :param a: Task arrive time, must be lower or equal than the hyperperiod
        :param d: Task deadline time, must be lower or equal than the hyperperiod
        :param e: Energy consumption
        """
        super().__init__(c, e)
        self.a: float = a
        self.d: float = d


class TasksSpecification(object):
    """
    System tasks
    """

    def __init__(self, tasks: List[Task]):
        """
        :param tasks: List of tasks
        """
        self.periodic_tasks: List[PeriodicTask] = [task for task in tasks if type(task) is PeriodicTask]
        self.aperiodic_tasks: List[AperiodicTask] = [task for task in tasks if type(task) is AperiodicTask]

        # As lcm can only be calculated with integer arguments, the float number is multiplied by a big integer to
        # minimize the error in integer conversion
        float_corrector = 2 ** 16

        self.h = scipy.lcm.reduce(
             list(map(lambda a: int(a.t * float_corrector), self.periodic_tasks))) / float_corrector  # Hyper period
