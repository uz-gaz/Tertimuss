from typing import List

from main.core.problem_specification.automatic_task_generator.template.AbstractTaskGeneratorAlgorithm import AbstractTaskGeneratorAlgorithm
from main.core.problem_specification.automatic_task_generator.implementations.UUniFast import UUniFast


class TaskGeneratorSelector(object):
    @staticmethod
    def select_task_generator(name: str) -> AbstractTaskGeneratorAlgorithm:
        """
        Select task generator by name
        :param name: Name of the automatic task generator
        :return:
        """
        task_generator_definition = {
            "UUniFast": UUniFast()
        }
        return task_generator_definition.get(name)

    @staticmethod
    def get_task_generators_names() -> List[str]:
        return ["UUniFast"]
