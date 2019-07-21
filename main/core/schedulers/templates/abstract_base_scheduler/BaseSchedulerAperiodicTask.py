from main.core.problem_specification.tasks_specification.AperiodicTask import AperiodicTask
from main.core.schedulers.templates.abstract_base_scheduler.BaseSchedulerTask import BaseSchedulerTask


class BaseSchedulerAperiodicTask(AperiodicTask, BaseSchedulerTask):
    def __init__(self, task_specification: AperiodicTask, task_id: int):
        AperiodicTask.__init__(self, task_specification.c, task_specification.a, task_specification.d,
                               task_specification.e)
        BaseSchedulerTask.__init__(self, task_specification.d, task_specification.a, task_specification.c, task_id)