from functools import reduce
from typing import List, Optional, Dict, Tuple, Set

import numpy

from main.core.execution_simulator.system_simulator.SystemAperiodicTask import SystemAperiodicTask
from main.core.execution_simulator.system_simulator.SystemPeriodicTask import SystemPeriodicTask

from main.core.execution_simulator.system_simulator.SystemTask import SystemTask
from main.core.problem_specification.GlobalSpecification import GlobalSpecification
from main.core.problem_specification.cpu_specification.CoreGroupSpecification import CoreGroupSpecification
from main.core.problem_specification.cpu_specification.CpuSpecification import CpuSpecification
from main.core.problem_specification.tasks_specification.PeriodicTask import PeriodicTask
from main.core.problem_specification.tasks_specification.TasksSpecification import TasksSpecification
from main.core.schedulers_definition.implementations.AIECSMultipleMajorCycles import AIECSMultipleMajorCyclesScheduler
from main.core.schedulers_definition.implementations.EDF import EDFScheduler
from main.core.schedulers_definition.implementations.clusteredaiecs.bpp_based_algorithms import \
    BestFitDescendantBPPBasedPartitionAlgorithm
from main.core.schedulers_definition.implementations.clusteredaiecs.task import ImplicitDeadlineTask
from main.core.schedulers_definition.templates.AbstractScheduler import AbstractScheduler


class ClusteredAIECSScheduler(AbstractScheduler):
    def __init__(self):
        super().__init__()
        # List[Scheduler, tasks ids, number_of_cpus, first cpu index]
        self.__partitions_schedulers: List[Tuple[AbstractScheduler, Set[int], int, int]] = []

    def offline_stage(self, global_specification: GlobalSpecification, periodic_tasks: List[SystemPeriodicTask],
                      aperiodic_tasks: List[SystemAperiodicTask]) -> float:
        selected_frequency = max(global_specification.cpu_specification.cores_specification.available_frequencies)

        periodic_tasks_dict = {i.id: i for i in periodic_tasks}

        task_set: Dict[int, ImplicitDeadlineTask] = {i.id: ImplicitDeadlineTask(i.c, round(i.d * selected_frequency))
                                                     for i in periodic_tasks}

        h = round(reduce(numpy.lcm, [int(i.d) for i in task_set.values()]))

        used_cycles = int(sum([i.c * (h / i.d) for i in task_set.values()]))

        m = len(global_specification.cpu_specification.cores_specification.operating_frequencies)

        free_cycles = h * m - used_cycles

        if free_cycles != 0:
            task_set[-1] = ImplicitDeadlineTask(free_cycles, h)

        partition_algorithm = BestFitDescendantBPPBasedPartitionAlgorithm()

        partitions_obtained: List[Tuple[int, Set[int]]] = partition_algorithm.do_partition(task_set, m)

        # Partitions done
        for utilization, task_set_loop in partitions_obtained:
            major_cycle_local = round(reduce(numpy.lcm, [int(periodic_tasks_dict[i].d) for i in task_set_loop]))

            number_of_major_cycles = round(global_specification.tasks_specification.h / major_cycle_local)

            actual_scheduler = EDFScheduler() if (utilization == 1) else AIECSMultipleMajorCyclesScheduler(
                number_of_major_cycles)

            self.__partitions_schedulers.append(
                (actual_scheduler, task_set_loop, utilization, sum([i[2] for i in self.__partitions_schedulers])))

            # Call on offline stage
            local_task_specification: TasksSpecification = TasksSpecification(
                [PeriodicTask(c=periodic_tasks_dict[i].c, d=periodic_tasks_dict[i].d, t=periodic_tasks_dict[i].t,
                              e=None) for i
                 in task_set_loop])

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
            actual_scheduler.offline_stage(local_global_specification, [periodic_tasks_dict[i] for i in task_set_loop],
                                           [])
        return global_specification.simulation_specification.dt

    def schedule_policy(self, time: float, executable_tasks: List[SystemTask], active_tasks: List[int],
                        actual_cores_frequency: List[int], cores_max_temperature: Optional[numpy.ndarray]) -> \
            [List[int], Optional[float], Optional[List[int]]]:
        tasks_to_execute = []
        frequencies_to_set = []

        for (local_scheduler, task_set, local_number_of_cpus, first_cpu_index) in self.__partitions_schedulers:
            local_active_tasks = active_tasks[first_cpu_index: first_cpu_index + local_number_of_cpus]
            local_cores_frequency = actual_cores_frequency[first_cpu_index: first_cpu_index + local_number_of_cpus]

            local_tasks_to_execute, local_dt, local_frequencies = local_scheduler.schedule_policy(
                time, [i for i in executable_tasks if i.id in task_set], local_active_tasks, local_cores_frequency,
                None)

            # Update local active tasks
            tasks_to_execute = tasks_to_execute + local_tasks_to_execute
            frequencies_to_set = frequencies_to_set + (
                local_frequencies if local_frequencies is not None else local_cores_frequency)
        return tasks_to_execute, None, frequencies_to_set

    def aperiodic_arrive(self, time: float, aperiodic_tasks_arrived: List[SystemTask],
                         actual_cores_frequency: List[int], cores_max_temperature: Optional[numpy.ndarray]) -> bool:
        # Wont be implemented for now
        return False
