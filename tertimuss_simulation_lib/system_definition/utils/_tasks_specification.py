from tertimuss_simulation_lib._math_utils import float_lcm
from tertimuss_simulation_lib.system_definition import TaskSet


def calculate_major_cycle(task_set: TaskSet):
    return float_lcm([i.d for i in task_set.periodic_tasks])
