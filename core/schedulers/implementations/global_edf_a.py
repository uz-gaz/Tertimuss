from typing import List, Optional

import scipy

from core.kernel_generator.global_model import GlobalModel
from core.problem_specification_models.GlobalSpecification import GlobalSpecification

from core.schedulers.templates.abstract_global_scheduler import AbstractGlobalScheduler, GlobalSchedulerPeriodicTask, \
    GlobalSchedulerTask, GlobalSchedulerAperiodicTask


class GlobalEDFAffinityScheduler(AbstractGlobalScheduler):
    """
    Implements a revision of the global earliest deadline first scheduler where affinity of tasks to processors have been
    got in mind
    """

    def __init__(self) -> None:
        super().__init__()
        self.__m = None

    def offline_stage(self, global_specification: GlobalSpecification, global_model: GlobalModel,
                      periodic_tasks: List[GlobalSchedulerPeriodicTask],
                      aperiodic_tasks: List[GlobalSchedulerAperiodicTask]) -> float:
        self.__m = global_specification.cpu_specification.number_of_cores
        return super().offline_stage(global_specification, global_model, periodic_tasks, aperiodic_tasks)

    def aperiodic_arrive(self, time: float, executable_tasks: List[GlobalSchedulerTask], active_tasks: List[int],
                         actual_cores_frequency: List[float], cores_max_temperature: Optional[scipy.ndarray],
                         aperiodic_task_ids: List[int]) -> bool:
        # Nothing to do
        return False

    def schedule_policy(self, time: float, tasks: List[GlobalSchedulerPeriodicTask], active_tasks: List[int],
                        cores_frequency: Optional[List[float]], cores_temperature: Optional[scipy.ndarray]) -> \
            [List[int], Optional[float], Optional[List[float]]]:
        """
        Method to implement with the actual scheduler police
        :param cores_frequency: Frequencies of cores
        :param time: actual simulation time passed
        :param tasks: tasks
        :param m: number of cores
        :param active_tasks: actual id of tasks assigned to cores (task with id -1 is the idle task)
        :param cores_temperature: temperature of each core
        :return: 1 - tasks to assign to cores in next step (task with id -1 is the idle task)
                 2 - next quantum size (if None, will be taken the quantum specified in the offline_stage)
                 3 - cores relatives frequencies for the next quantum (if None, will be taken the frequencies specified
                  in the offline_stage)
        """
        # alive_tasks = [x for x in tasks if x.next_arrival <= time]
        task_order = scipy.argsort(list(map(lambda x: x.next_deadline, tasks)))
        tasks_to_execute = ([tasks[i].id for i in task_order] + (self.__m - len(tasks)) * [-1])[0:self.__m]

        # Do affinity
        for i in range(self.__m):
            actual = active_tasks[i]
            for j in range(self.__m):
                if tasks_to_execute[j] == actual:
                    tasks_to_execute[j], tasks_to_execute[i] = tasks_to_execute[i], tasks_to_execute[j]
        return tasks_to_execute, None, None
