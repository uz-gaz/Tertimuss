from typing import List, Optional

import scipy

from core.schedulers.abstract_global_scheduler import AbstractGlobalScheduler, GlobalSchedulerTask


class GlobalEDFAffinityScheduler(AbstractGlobalScheduler):
    """
    Implements a revision of the global earliest deadline first scheduler where affinity of tasks to processors have been
    got in mind
    """

    def __init__(self) -> None:
        super().__init__()

    def schedule_policy(self, time: float, tasks: List[GlobalSchedulerTask], m: int, active_tasks: List[int],
                        cores_temperature: Optional[scipy.ndarray]) -> List[int]:
        """
        Method to implement with the actual scheduler police
        :param time: actual simulation time passed
        :param tasks: tasks
        :param m: number of cores
        :param active_tasks: actual id of tasks assigned to cores (task with id -1 is the idle task)
        :param cores_temperature: temperature of each core
        :return: tasks to assign to cores in next step (task with id -1 is the idle task)
        """
        alive_tasks = [x for x in tasks if x.next_arrival <= time]
        task_order = scipy.argsort(list(map(lambda x: x.next_deadline, alive_tasks)))
        tasks_to_execute = ([alive_tasks[i].id for i in task_order] + (m - len(alive_tasks)) * [-1])[0:m]

        # Do affinity
        for i in range(m):
            actual = active_tasks[i]
            for j in range(m):
                if tasks_to_execute[j] == actual:
                    tasks_to_execute[j], tasks_to_execute[i] = tasks_to_execute[i], tasks_to_execute[j]
        return tasks_to_execute
