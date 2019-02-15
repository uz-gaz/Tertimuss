from task_generator.TaskGeneratorAlgorithm import TaskGeneratorAlgorithm


class UUniFast(TaskGeneratorAlgorithm):

    def __init__(self, number_of_tasks: int, utilization: float):
        self.number_of_tasks = number_of_tasks
        self.utilization = utilization

    def generate(self) -> list:
        return [self.number_of_tasks]
