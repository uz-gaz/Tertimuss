from typing import List

from main.core.task_generator.template.AbstractTaskGeneratorAlgorithm import AbstractTaskGeneratorAlgorithm
from main.core.task_generator.implementations.UUniFast import UUniFast


class TaskGeneratorSelector(object):
    @staticmethod
    def select_task_generator(name: str) -> AbstractTaskGeneratorAlgorithm:
        task_generator_definition = {
            "UUniFast": UUniFast()
        }
        return task_generator_definition.get(name)

    @staticmethod
    def get_task_generators_names() -> List[str]:
        return ["UUniFast"]
