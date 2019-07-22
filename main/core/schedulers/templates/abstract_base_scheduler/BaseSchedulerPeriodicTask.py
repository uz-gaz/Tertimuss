from main.core.problem_specification.tasks_specification.PeriodicTask import PeriodicTask
from main.core.schedulers.templates.abstract_base_scheduler.BaseSchedulerTask import BaseSchedulerTask


class BaseSchedulerPeriodicTask(PeriodicTask, BaseSchedulerTask):
    def __init__(self, task_specification: PeriodicTask, task_id: int, base_frequency: int):
        PeriodicTask.__init__(self, task_specification.c, task_specification.t, task_specification.d,
                              task_specification.e)
        BaseSchedulerTask.__init__(self, task_specification.d, 0, task_specification.c, task_id, base_frequency)
