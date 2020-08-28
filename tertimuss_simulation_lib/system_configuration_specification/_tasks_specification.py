from functools import reduce
from typing import List

import numpy

from typing import Optional


class Task(object):

    def __init__(self, c: int, e: Optional[float]):
        """
        Task specification

        :param c: Task worst case execution time in cycles
        :param e: Energy consumption
        """
        self.c: int = c
        self.e: Optional[float] = e


class PeriodicTask(Task):

    def __init__(self, c: int, t: float, d: float, e: Optional[float]):
        """
        Periodic task specification

        :param c: Task worst case execution time in cycles
        :param t: Task period in seconds
        :param d: Task deadline in seconds
        :param e: Energy consumption
        """
        super().__init__(c, e)
        self.t: float = t
        self.d: float = d


class AperiodicTask(Task):

    def __init__(self, c: int, a: float, d: float, e: Optional[float]):
        """
        Aperiodic task specification

        :param c: Task worst case execution time in cycles
        :param a: Task arrive time, must be lower or equal than the hyperperiod
        :param d: Task deadline time, must be lower or equal than the hyperperiod
        :param e: Energy consumption
        """
        super().__init__(c, e)
        self.a: float = a
        self.d: float = d


class TasksSpecification(object):

    def __init__(self, periodic_tasks: List[PeriodicTask], aperiodic_tasks: List[AperiodicTask]):
        """
        System tasks

        :param periodic_tasks: List of periodic tasks in the system
        :param aperiodic_tasks: List of aperiodic tasks in the system
        """
        self.periodic_tasks: List[PeriodicTask] = periodic_tasks
        self.aperiodic_tasks: List[AperiodicTask] = aperiodic_tasks

        # As lcm can only be calculated with integer arguments, the float number is multiplied by a big integer to
        # minimize the error in integer conversion
        float_corrector = 2 ** 16

        self.h = reduce(numpy.lcm, list(
            map(lambda a: int(a.t * float_corrector), self.periodic_tasks))) / float_corrector  # Hyper period
