from main.core.task_generator.template.AbstractTaskGeneratorAlgorithm import AbstractTaskGeneratorAlgorithm
from main.core.task_generator.implementations.UUniFast import UUniFast


class TaskGeneratorSelector(object):
    @staticmethod
    def select_task_generator(name: str) -> AbstractTaskGeneratorAlgorithm:
        task_generator_definition = {
            "UUniFast": UUniFast()
        }
        return task_generator_definition.get(name)
