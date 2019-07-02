from typing import List, Optional

import scipy

from core.schedulers.templates.abstract_global_scheduler import AbstractGlobalScheduler, GlobalSchedulerTask


class GlobalEDFAffinityFrequencyAwareScheduler(AbstractGlobalScheduler):
    """
    Implements a revision of the global earliest deadline first scheduler where affinity of tasks to processors have been
    got in mind and frequency too
    """

    def __init__(self) -> None:
        super().__init__()

    def schedule_policy(self, time: float, tasks: List[GlobalSchedulerTask], m: int, active_tasks: List[int],
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
        alive_tasks = [x for x in tasks if x.next_arrival <= time]
        task_order = scipy.argsort(list(map(lambda x: x.next_deadline, alive_tasks)))
        tasks_to_execute = ([alive_tasks[i].id for i in task_order] + (m - len(alive_tasks)) * [-1])[0:m]

        # Assign highest priority task to faster processor
        tasks_to_execute = [x for _, x in sorted(zip(cores_frequency, tasks_to_execute), reverse=True)]

        # Do affinity
        for i in range(m):
            actual = active_tasks[i]
            for j in range(m):
                if tasks_to_execute[j] == actual and cores_frequency[j] == cores_frequency[i]:
                    tasks_to_execute[j], tasks_to_execute[i] = tasks_to_execute[i], tasks_to_execute[j]
        return tasks_to_execute, None, None
