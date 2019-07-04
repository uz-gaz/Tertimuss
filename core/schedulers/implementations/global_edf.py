from typing import List, Optional

import scipy

from core.kernel_generator.global_model import GlobalModel
from core.problem_specification_models.GlobalSpecification import GlobalSpecification
from core.schedulers.templates.abstract_global_scheduler import AbstractGlobalScheduler, GlobalSchedulerPeriodicTask, \
    GlobalSchedulerAperiodicTask, GlobalSchedulerTask


class GlobalEDFScheduler(AbstractGlobalScheduler):
    """
    Implements global earliest deadline first scheduler
    """

    def __init__(self) -> None:
        super().__init__()
        self.__m = None

    def offline_stage(self, global_specification: GlobalSpecification,
                      periodic_tasks: List[GlobalSchedulerPeriodicTask],
                      aperiodic_tasks: List[GlobalSchedulerAperiodicTask]) -> float:
        """
        Method to implement with the offline stage scheduler tasks
        :param aperiodic_tasks: list of aperiodic tasks with their assigned ids
        :param periodic_tasks: list of periodic tasks with their assigned ids
        :param global_specification: Global specification
        :return: 1 - Scheduling quantum (default will be the step specified in problem creation)
        """
        self.__m = global_specification.cpu_specification.number_of_cores
        return super().offline_stage(global_specification, periodic_tasks, aperiodic_tasks)

    def aperiodic_arrive(self, time: float, executable_tasks: List[GlobalSchedulerTask], active_tasks: List[int],
                         actual_cores_frequency: List[float], cores_max_temperature: Optional[scipy.ndarray],
                         aperiodic_task_ids: List[int]) -> bool:
        # Nothing to do
        return False

    def schedule_policy(self, time: float, executable_tasks: List[GlobalSchedulerTask], active_tasks: List[int],
                        actual_cores_frequency: List[float], cores_max_temperature: Optional[scipy.ndarray]) -> \
            [List[int], Optional[float], Optional[List[float]]]:
        """
        Method to implement with the actual scheduler police
        :param actual_cores_frequency: Frequencies of cores
        :param time: actual simulation time passed
        :param executable_tasks: actual tasks that can be executed ( c > 0 and arrive_time <= time)
        :param active_tasks: actual id of tasks assigned to cores (task with id -1 is the idle task)
        :param cores_max_temperature: temperature of each core
        :return: 1 - tasks to assign to cores in next step (task with id -1 is the idle task)
                 2 - next quantum size (if None, will be taken the quantum specified in the offline_stage)
                 3 - cores relatives frequencies for the next quantum (if None, will be taken the frequencies specified
                  in the problem specification)
        """
        # alive_tasks = [x for x in tasks if x.next_arrival <= time]
        task_order = scipy.argsort(list(map(lambda x: x.next_deadline, executable_tasks)))
        return ([executable_tasks[i].id for i in task_order] + (self.__m - len(executable_tasks)) * [-1])[
               0:self.__m], None, None
