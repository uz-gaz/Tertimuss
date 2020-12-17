from ....simulation_lib.math_utils import list_float_lcm
from ....simulation_lib.system_definition import TaskSet


def calculate_major_cycle(task_set: TaskSet):
    return list_float_lcm([i.relative_deadline for i in task_set.periodic_tasks])
