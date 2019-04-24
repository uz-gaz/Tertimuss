from typing import List

import scipy

from core.schedulers.abstract_global_scheduler import AbstractGlobalScheduler, GlobalSchedulerTask


class GlobalEDFScheduler(AbstractGlobalScheduler):

    def __init__(self) -> None:
        super().__init__()

    def schedule_policy(self, time: float, tasks: List[GlobalSchedulerTask], m: int, active_tasks: List[int],
                        cores_temperature: scipy.ndarray) -> List[int]:
        alive_tasks = [x for x in tasks if x.next_arrival <= time]
        task_order = scipy.argsort(list(map(lambda x: x.next_deadline, alive_tasks)))
        return ([alive_tasks[i].id for i in task_order] + (m - len(alive_tasks)) * [-1])[0:m]
