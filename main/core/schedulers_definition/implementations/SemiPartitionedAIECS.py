import math
from typing import List, Optional

import numpy

from main.core.execution_simulator.system_simulator.SystemAperiodicTask import SystemAperiodicTask
from main.core.execution_simulator.system_simulator.SystemPeriodicTask import SystemPeriodicTask

from main.core.execution_simulator.system_simulator.SystemTask import SystemTask
from main.core.problem_specification.GlobalSpecification import GlobalSpecification
from main.core.schedulers_definition.implementations.AIECS import AIECSScheduler
from main.core.schedulers_definition.implementations.G_EDF import GlobalEDFScheduler
from main.core.schedulers_definition.implementations.RUN import RUNTask, RUNScheduler, RUNPack


class SemiPartitionedAIECSScheduler(RUNScheduler):
    def __init__(self):
        self.__partitions_schedulers = []

    def __obtain_tasks_from_tree_parent(self, pack_of_tasks: RUNPack):
        content = []
        for i in pack_of_tasks.content:
            if type(i) is RUNTask:
                content = content + [i.task_id]
            elif type(i) is RUNPack:
                content = content + self.__obtain_tasks_from_tree_parent(i)
        return content

    def offline_stage(self, global_specification: GlobalSpecification, periodic_tasks: List[SystemPeriodicTask],
                      aperiodic_tasks: List[SystemAperiodicTask]) -> float:
        # TODO: We should reduce the frequency to the lowest possible as in JDEDS
        # available_frequencies = global_specification.cpu_specification.cores_specification.available_frequencies
        # available_frequencies.sort(reverse=True)
        # selected_frequency = available_frequencies[0]
        selected_frequency = max(global_specification.cpu_specification.cores_specification.available_frequencies)

        task_set = [RUNTask(i.id, i.c, int(i.d * selected_frequency)) for i in periodic_tasks]
        h = numpy.lcm.reduce([int(i.d) for i in task_set])

        used_cycles = int(sum([i.c * (h / i.d) for i in task_set]))

        m = len(global_specification.cpu_specification.cores_specification.operating_frequencies)

        free_cycles = h * m - used_cycles

        if free_cycles != 0:
            task_set = task_set + [RUNTask(-1, free_cycles, h)]

        parents_of_tree = self._create_tree(task_set)

        # Partitions done
        partitions = [self.__obtain_tasks_from_tree_parent(i) for i in parents_of_tree]

        # 1 - View the utilization of each partition
        partitioned_task_set = [[next(x for x in periodic_tasks if x.id == i) for i in partition_tasks if (i != -1)]
                                for partition_tasks in partitions]

        task_sets_and_utilization = [(i, math.ceil(sum([j.c / j.d for j in i]))) for i in partitioned_task_set]

        for task_set, utilization in task_sets_and_utilization:
            actual_scheduler = GlobalEDFScheduler() if (utilization == 1) else AIECSScheduler()
            self.__partitions_schedulers.append(actual_scheduler)
            # TODO:continue
            actual_scheduler.offline_stage()

        pass
        pass
        pass
        pass
        i = 0
        i = 1
        # 2 - For each partition create an instance of AIECS scheduler and assign some CPUs

    def schedule_policy(self, time: float, executable_tasks: List[SystemTask], active_tasks: List[int],
                        actual_cores_frequency: List[int], cores_max_temperature: Optional[numpy.ndarray]) -> \
            [List[int], Optional[float], Optional[List[int]]]:
        # TODO: Call each scheduler instance
        pass

    def aperiodic_arrive(self, time: float, aperiodic_tasks_arrived: List[SystemTask],
                         actual_cores_frequency: List[int], cores_max_temperature: Optional[numpy.ndarray]) -> bool:
        # Wont be implemented now
        return False
