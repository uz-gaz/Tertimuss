from main.core.problem_specification.tasks_specification.AperiodicTask import AperiodicTask
from main.core.execution_simulator.system_simulator.SystemTask import SystemTask


class SystemAperiodicTask(AperiodicTask, SystemTask):
    def __init__(self, task_specification: AperiodicTask, task_id: int):
        """
        This class is a fusion between the current job that is being executed of an aperiodic task and the task itself
        :param task_specification: aperiodic task
        :param task_id: task id
        """
        AperiodicTask.__init__(self, task_specification.c, task_specification.a, task_specification.d,
                               task_specification.e)
        SystemTask.__init__(self, task_specification.d, task_specification.a, task_specification.c, task_id)
