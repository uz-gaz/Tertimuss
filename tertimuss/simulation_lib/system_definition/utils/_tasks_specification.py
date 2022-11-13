from ...math_utils import list_float_lcm, list_float_gcd
from .._tasks_specification import TaskSet


def calculate_major_cycle(task_set: TaskSet):
    return list_float_lcm([i.period for i in task_set.periodic_tasks])

def calculate_minor_cycle(task_set: TaskSet):
    return list_float_gcd([i.period for i in task_set.periodic_tasks])
