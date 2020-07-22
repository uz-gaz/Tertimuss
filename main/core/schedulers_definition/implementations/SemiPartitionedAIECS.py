import math
from functools import reduce
from typing import List, Optional

import numpy

from main.core.execution_simulator.system_simulator.SystemAperiodicTask import SystemAperiodicTask
from main.core.execution_simulator.system_simulator.SystemPeriodicTask import SystemPeriodicTask

from main.core.execution_simulator.system_simulator.SystemTask import SystemTask
from main.core.problem_specification.GlobalSpecification import GlobalSpecification
from main.core.problem_specification.cpu_specification.CoreGroupSpecification import CoreGroupSpecification
from main.core.problem_specification.cpu_specification.CpuSpecification import CpuSpecification
from main.core.problem_specification.tasks_specification.PeriodicTask import PeriodicTask
from main.core.problem_specification.tasks_specification.TasksSpecification import TasksSpecification
from main.core.schedulers_definition.implementations.AIECS import AIECSScheduler
from main.core.schedulers_definition.implementations.G_EDF import GlobalEDFScheduler
from main.core.schedulers_definition.implementations.RUN import RUNTask, RUNScheduler, RUNPack


class SemiPartitionedAIECSScheduler(RUNScheduler):
    def __init__(self):
        super().__init__()
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
        selected_frequency = max(global_specification.cpu_specification.cores_specification.available_frequencies)

        task_set = [RUNTask(i.id, i.c, int(i.d * selected_frequency)) for i in periodic_tasks]
        h = reduce(numpy.lcm, [int(i.d) for i in task_set])

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

        task_sets_and_utilization = [(i, math.ceil(sum([j.c / (j.d * selected_frequency) for j in i]))) for i in
                                     partitioned_task_set]

        for task_set_loop, utilization in task_sets_and_utilization:
            # TODO: In the case of AIECS it assumes id from 0 to number of tasks -1, so if we provide the original id it fill fail
            actual_scheduler = GlobalEDFScheduler() if (utilization == 1) else AIECSScheduler()
            self.__partitions_schedulers.append(
                [actual_scheduler, [i.id for i in task_set_loop], utilization * [-1],
                 utilization * [selected_frequency]])

            # Call on offline stage
            local_task_specification: TasksSpecification = TasksSpecification(
                [PeriodicTask(i.c, i.t, i.d, i.e) for i in task_set_loop])
            local_cores_specification: CoreGroupSpecification = CoreGroupSpecification(
                global_specification.cpu_specification.cores_specification.physical_properties,
                global_specification.cpu_specification.cores_specification.energy_consumption_properties,
                global_specification.cpu_specification.cores_specification.available_frequencies,
                utilization * [selected_frequency])

            # The CPU specification can be improved assigning the real location of the cores
            local_cpu_specification: CpuSpecification = CpuSpecification(
                global_specification.cpu_specification.board_specification,
                local_cores_specification)
            local_global_specification: GlobalSpecification = GlobalSpecification(
                local_task_specification,
                local_cpu_specification,
                global_specification.environment_specification,
                global_specification.simulation_specification,
                global_specification.tcpn_model_specification)
            actual_scheduler.offline_stage(local_global_specification, task_set_loop, [])
        return global_specification.simulation_specification.dt

    def schedule_policy(self, time: float, executable_tasks: List[SystemTask], active_tasks: List[int],
                        actual_cores_frequency: List[int], cores_max_temperature: Optional[numpy.ndarray]) -> \
            [List[int], Optional[float], Optional[List[int]]]:
        tasks_to_execute = []
        frequencies_to_set = []
        for scheduler_info in self.__partitions_schedulers:
            local_scheduler, task_set, local_active_tasks, local_cores_frequency = scheduler_info

            local_tasks_to_execute, local_dt, local_frequencies = local_scheduler.schedule_policy(
                time, [i for i in executable_tasks if i.id in task_set], local_active_tasks, local_cores_frequency,
                None)

            # Update local active tasks
            scheduler_info[2] = local_tasks_to_execute
            scheduler_info[3] = local_frequencies if (local_frequencies is not None) else local_cores_frequency
            tasks_to_execute = tasks_to_execute + local_tasks_to_execute
            frequencies_to_set = frequencies_to_set + scheduler_info[3]
        return tasks_to_execute, None, frequencies_to_set

    def aperiodic_arrive(self, time: float, aperiodic_tasks_arrived: List[SystemTask],
                         actual_cores_frequency: List[int], cores_max_temperature: Optional[numpy.ndarray]) -> bool:
        # Wont be implemented for now
        return False
