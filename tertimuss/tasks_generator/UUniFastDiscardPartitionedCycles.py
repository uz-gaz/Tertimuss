from typing import Dict, List

from main.core.problem_specification.automatic_task_generator.implementations.UUniFastDiscardCycles import \
    UUniFastDiscardCycles
from main.core.problem_specification.tasks_specification.PeriodicTask import PeriodicTask


class UUniFastDiscardPartitionedCycles(UUniFastDiscardCycles):
    def generate(self, options: Dict) -> List[PeriodicTask]:
        """
        Generate a list of periodic tasks
        :param options: parameter to the algorithm
                        min_period_interval: int -> min possible value of periods in cycles
                        max_period_interval: int -> max possible value of periods in cycles
                        processor_frequency: int -> max processor frequency in Hz
                        major_cycle: int -> major cycle in second
                        partition_description: List[Tuple[int, float]] -> List of (number of tasks in the partition,
                         and utilization of partition)
        :return: List of tasks
        """
        task_set = []
        partitions_description = options["partition_description"]

        for number_of_tasks, utilization in partitions_description:
            partition_options = {
                "number_of_tasks": number_of_tasks,
                "utilization": utilization,
                "min_period_interval": options["min_period_interval"],
                "max_period_interval": options["max_period_interval"],
                "processor_frequency": options["processor_frequency"]
            }
            task_set = task_set + super().generate(partition_options)

        return task_set
