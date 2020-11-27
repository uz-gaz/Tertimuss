from tertimuss_simulation_lib.math_utils import list_float_lcm
from tertimuss_simulation_lib.system_definition import TaskSet, Task, Job


def calculate_major_cycle(task_set: TaskSet):
    return list_float_lcm([i.relative_deadline for i in task_set.periodic_tasks])
