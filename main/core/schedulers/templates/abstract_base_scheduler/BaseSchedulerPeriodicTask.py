from main.core.problem_specification.tasks_specification.PeriodicTask import PeriodicTask
from main.core.schedulers.templates.abstract_base_scheduler.BaseSchedulerTask import BaseSchedulerTask


class BaseSchedulerPeriodicTask(PeriodicTask, BaseSchedulerTask):
    def __init__(self, task_specification: PeriodicTask, task_id: int):
        """
        This class is a fusion between the current job that is being executed of a periodic task and the task itself
        :param task_specification: periodic task
        :param task_id: task id
        """
        PeriodicTask.__init__(self, task_specification.c, task_specification.t, task_specification.d,
                              task_specification.e)
        BaseSchedulerTask.__init__(self, task_specification.d, 0, task_specification.c, task_id)
