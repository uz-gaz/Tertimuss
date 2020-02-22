from typing import List

import numpy

from main.core.problem_specification.tasks_specification.AperiodicTask import AperiodicTask
from main.core.problem_specification.tasks_specification.PeriodicTask import PeriodicTask
from main.core.problem_specification.tasks_specification.Task import Task


class TasksSpecification(object):

    def __init__(self, tasks: List[Task]):
        """
        System tasks

        :param tasks: List of tasks
        """
        self.periodic_tasks: List[PeriodicTask] = [task for task in tasks if type(task) is PeriodicTask]
        self.aperiodic_tasks: List[AperiodicTask] = [task for task in tasks if type(task) is AperiodicTask]

        # As lcm can only be calculated with integer arguments, the float number is multiplied by a big integer to
        # minimize the error in integer conversion
        float_corrector = 2 ** 16

        self.h = numpy.lcm.reduce(
             list(map(lambda a: int(a.t * float_corrector), self.periodic_tasks))) / float_corrector  # Hyper period
