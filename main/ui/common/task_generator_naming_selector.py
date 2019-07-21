from typing import Optional

from main.core.task_generator.template.AbstractTaskGeneratorAlgorithm import AbstractTaskGeneratorAlgorithm
from main.core.task_generator.implementations.UUniFast import UUniFast


def select_task_generator(name: str, number_of_tasks: int, utilization: float, period_interval: tuple,
                          processor_frequency: float) -> Optional[AbstractTaskGeneratorAlgorithm]:
    task_generator_definition = {
        "uunifast": UUniFast(number_of_tasks, utilization, period_interval, processor_frequency)
    }
    return task_generator_definition.get(name)
