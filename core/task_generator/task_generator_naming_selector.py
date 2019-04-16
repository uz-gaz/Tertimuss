from typing import Optional

from core.task_generator.TaskGeneratorAlgorithm import TaskGeneratorAlgorithm
from core.task_generator.UUniFast import UUniFast


def select_task_generator(name: str, number_of_tasks: int, utilization: float) -> Optional[TaskGeneratorAlgorithm]:
    # TODO
    task_generator_definition = {
        "uunifast": UUniFast(number_of_tasks, utilization)
    }
    return task_generator_definition.get(name)
