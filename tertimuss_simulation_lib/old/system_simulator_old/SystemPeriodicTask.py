from main.core.problem_specification.tasks_specification.PeriodicTask import PeriodicTask
from main.core.execution_simulator.system_simulator.SystemTask import SystemTask


class SystemPeriodicTask(PeriodicTask, SystemTask):
    def __init__(self, task_specification: PeriodicTask, task_id: int):
        """
        This class is a fusion between the current job that is being executed of a periodic task and the task itself
        :param task_specification: periodic task
        :param task_id: task id
        """
        PeriodicTask.__init__(self, task_specification.c, task_specification.temperature, task_specification.d,
                              task_specification.e)
        SystemTask.__init__(self, task_specification.d, 0, task_specification.c, task_id)
