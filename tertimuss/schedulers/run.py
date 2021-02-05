"""
=========================================
Reduction to Uniprocessor Scheduler (RUN)
=========================================

This module provides the following class:
- :class:`RUNScheduler`
"""

from typing import Set, Dict, Optional, Tuple, List

import numpy

from tertimuss.simulation_lib.math_utils import list_int_gcd, list_int_lcm
from tertimuss.simulation_lib.schedulers_definition import CentralizedAbstractScheduler
from tertimuss.simulation_lib.system_definition import ProcessorDefinition, EnvironmentSpecification, TaskSet, \
    PreemptiveExecution
from tertimuss.simulation_lib.system_definition.utils import calculate_major_cycle


class _RUNServer(object):
    def __init__(self, c: int, d: int):
        # c: WCET in cycles
        # d: deadline in cycles
        self.c: int = c
        self.d: int = d
        self.laxity: int = d - c
        self.pending_c: int = self.c
        self.pending_laxity: int = self.laxity
        self.next_arrive: int = self.d
        self.server_id = id(self)

        # This value will be used to give more priority to the last executed task
        self.last_time_executed_dual: int = 0
        self.last_time_executed_edf: int = 0


class _RUNPack(_RUNServer):
    """
    This class represent the union of a DUAL and an EDF server
    """

    def __init__(self, content: List[_RUNServer]):
        self.content = content
        d = list_int_gcd([i.d for i in content])
        c = sum([((i.laxity if isinstance(i, _RUNPack) else i.c) * d) // i.d for i in content])
        super().__init__(c, d)


class _RUNTask(_RUNServer):
    def __init__(self, task_id: int, c: int, d: int):
        self.task_id = task_id
        self.last_cpu_execution = -1
        super().__init__(c, d)


class _PacksBin(object):
    def __init__(self, pack: _RUNServer):
        self.c = pack.laxity if isinstance(pack, _RUNPack) else pack.c
        self.d = pack.d
        self.packs = [pack]

    def can_add_server(self, pack: _RUNServer) -> bool:
        deadline = list_int_gcd([pack.d, self.d])
        bin_c = int(self.c / (self.d / deadline))
        ant_pack_c = pack.laxity if isinstance(pack, _RUNPack) else pack.c
        pack_c = int(ant_pack_c / (pack.d / deadline))
        return bin_c + pack_c <= deadline

    def add_server(self, pack: _RUNServer):
        deadline = list_int_gcd([pack.d, self.d])
        bin_c = int(self.c / (self.d / deadline))
        ant_pack_c = pack.laxity if isinstance(pack, _RUNPack) else pack.c
        pack_c = int(ant_pack_c / (pack.d / deadline))
        self.c = bin_c + pack_c
        self.d = deadline
        self.packs.append(pack)

    def transform_to_pack(self) -> _RUNPack:
        return _RUNPack(self.packs)


def _create_packs_from_virtual_tasks(packs: List[_RUNServer]) -> List[_RUNPack]:
    started_bins: List[_PacksBin] = []

    # Sort packs in descendant order of utilization
    sorted_packs = sorted(packs, key=lambda x: (x.laxity if isinstance(x, _RUNPack) else x.c) / x.d, reverse=True)

    for pack in sorted_packs:
        emptiest_bin_index: Optional[int] = None

        if len(started_bins) > 0:
            emptiest_bin_index = numpy.argmin([x.c / x.d for x in started_bins])  # Numpy.argmin returns an integer

        if emptiest_bin_index is not None and started_bins[emptiest_bin_index].can_add_server(pack):
            started_bins[emptiest_bin_index].add_server(pack)
        else:
            started_bins.append(_PacksBin(pack))

    return [actual_bin.transform_to_pack() for actual_bin in started_bins]


def _create_recursive_tree(packs: List[_RUNServer]) -> List[_RUNPack]:
    tree_parents: List[_RUNPack] = []
    tree_children: List[_RUNServer] = []

    for pack in packs:
        if pack.laxity == 0 and isinstance(pack, _RUNPack):
            tree_parents.append(pack)
        else:
            tree_children.append(pack)

    if len(tree_children) > 0:
        tree_parents = tree_parents + _create_recursive_tree(
            _create_packs_from_virtual_tasks(tree_children))
        return tree_parents
    else:
        return tree_parents


def _update_virtual_task_info(children: List[_RUNServer], actual_time_cycles: int):
    for i in children:
        if i.next_arrive <= actual_time_cycles:
            # We need update the task info
            i.pending_c = i.c
            i.next_arrive = i.next_arrive + i.d
            i.pending_laxity = i.laxity

        if isinstance(i, _RUNPack):
            _update_virtual_task_info(i.content, actual_time_cycles)


def _create_tree(tasks: List[_RUNTask]) -> List[_RUNPack]:
    parents = _create_recursive_tree(tasks)
    return parents


def _count_tree_levels(parent: _RUNPack) -> int:
    """
    Return the number of levels including the root
    :param parent:
    :return:
    """
    count = 1
    actual_parent = parent
    while not isinstance(actual_parent, _RUNTask):
        actual_parent = actual_parent.content[0]
        count += 1
    return count


def _edf_server_tasks_selection(previous_dual_selection: List[_RUNPack], selecting_servers: bool) -> List[_RUNServer]:
    selection = []

    for server in previous_dual_selection:
        children_with_time_to_execute = [i for i in server.content if (i.pending_laxity > 0 and selecting_servers) or (
                i.pending_c > 0 and not selecting_servers)]
        if len(children_with_time_to_execute) != 0:
            # Order the tasks by the EDF criteria
            # Sort packs in ascendant order of arrive
            children_with_time_to_execute.sort(key=lambda x: x.next_arrive, reverse=False)
            selected_next_arrive = children_with_time_to_execute[0].next_arrive

            # If there are several tasks with the same priority, the last executed is selected to decrease context
            # changes
            children_with_highest_priority = [i for i in children_with_time_to_execute if
                                              i.next_arrive == selected_next_arrive]
            # Sort packs in descendant order of last execution
            children_with_highest_priority.sort(key=lambda x: x.last_time_executed_edf, reverse=True)

            # Append to selection the highest priority task
            selection.append(children_with_highest_priority[0])

    return selection


def _select_servers_from_level(level: int, parent: _RUNPack) -> List[_RUNServer]:
    if level == 0:
        return [parent]
    else:
        to_return = []
        for i in parent.content:
            if isinstance(i, _RUNPack):
                recursive_return = _select_servers_from_level(level - 1, i)
                to_return = to_return + recursive_return
            else:
                to_return = to_return + [i]

        return to_return


def _dual_server_selection(level: int, parent: _RUNPack, previous_edf_selection: List[_RUNServer]) -> List[_RUNServer]:
    servers_from_level = _select_servers_from_level(level, parent)

    previous_edf_selection_ids = [i.server_id for i in previous_edf_selection]

    servers_not_selected_in_edf = [i for i in servers_from_level if i.server_id not in previous_edf_selection_ids]

    servers_with_pending_c = [i for i in servers_not_selected_in_edf if i.pending_c > 0]

    return servers_with_pending_c


def _select_tasks_to_execute_one_parent(parent: _RUNPack, actual_cycle: int) -> List[_RUNTask]:
    tree_levels = _count_tree_levels(parent)
    dual_selection = [parent]
    for level in range(1, tree_levels - 1):
        # Select servers by EDF
        edf_selection = _edf_server_tasks_selection(dual_selection, True)

        # Decrease pending dual_c (laxity) of those servers selected by edf
        for server in edf_selection:
            server.pending_laxity -= 1
            server.last_time_executed_edf = actual_cycle + 1

        # Select servers from the set of dual servers previously selected
        dual_selection = _dual_server_selection(level, parent, edf_selection)

        # Decrease pending c of those servers selected
        for server in dual_selection:
            server.pending_c -= 1
            server.last_time_executed_dual = actual_cycle + 1

    # Select tasks by EDF
    edf_selection_tasks = _edf_server_tasks_selection(dual_selection, False)

    # Decrease pending dual_c (laxity) of those servers selected by edf
    for server in edf_selection_tasks:
        server.pending_c -= 1
        server.last_time_executed_edf = actual_cycle + 1

    # In the leafs of the tree, we must have Tasks
    return [i for i in edf_selection_tasks if isinstance(i, _RUNTask)]


def _select_tasks_to_execute(parents: List[_RUNPack], actual_cycle: int) -> List[_RUNTask]:
    _update_virtual_task_info(parents, actual_cycle)
    tasks_to_execute = []
    for parent in parents:
        actual_tasks = _select_tasks_to_execute_one_parent(parent, actual_cycle)
        tasks_to_execute += actual_tasks
    return tasks_to_execute


def _assign_tasks_to_cpu(task_set: List[_RUNTask], active_tasks: List[int], m: int) -> List[int]:
    tasks_assignation = m * [-1]

    not_assigned_yet_phase_1 = []

    # Phase 1
    for i in task_set:
        if i.task_id in active_tasks and i.task_id != -1:
            cpu_assigned = active_tasks.index(i.task_id)
            tasks_assignation[cpu_assigned] = i.task_id
        else:
            not_assigned_yet_phase_1 = not_assigned_yet_phase_1 + [i]

    # Phase 2
    not_assigned_yet_phase_2 = []
    for i in not_assigned_yet_phase_1:
        if i.last_cpu_execution != -1 and tasks_assignation[i.last_cpu_execution] == -1:
            tasks_assignation[i.last_cpu_execution] = i.task_id
        else:
            not_assigned_yet_phase_2 = not_assigned_yet_phase_2 + [i]

    # If we have more tasks than CPUs, delete the excess of tasks
    not_assigned_yet_phase_2 = [i for i in not_assigned_yet_phase_2 if
                                i.task_id != -1]  # First delete the dummy task

    number_of_tasks_to_execute = len([i for i in task_set if i.task_id != -1])

    if number_of_tasks_to_execute > m:
        not_assigned_yet_phase_2 = not_assigned_yet_phase_2[(number_of_tasks_to_execute - m):]

    # Phase 3
    for i in not_assigned_yet_phase_2:
        next_empty_cpu = tasks_assignation.index(-1)
        tasks_assignation[next_empty_cpu] = i.task_id
        i.last_cpu_execution = next_empty_cpu

    return tasks_assignation


def _obtain_utilization_of_run_pack_subtree(run_pack: _RUNPack) -> float:
    return sum(
        [_obtain_utilization_of_run_pack_subtree(i) if isinstance(i, _RUNPack) else i.c / i.d for i in
         run_pack.content])


class RUNScheduler(CentralizedAbstractScheduler):
    """
    Implements the Reduction to Uniprocessor Scheduler (RUN)

    References:
        RUN: Optimal Multiprocessor Real-Time Scheduling via Reduction to Uniprocessor -
        Proceedings of the 32nd IEEE Real-Time Systems Symposium 2011
        DOI: 10.1109/RTSS.2011.17
    """

    def __init__(self, activate_debug: bool, store_clusters_obtained: bool):
        """
        Create the RUN scheduler instance

        :param activate_debug: True if want to communicate the scheduler to be in debug mode
        :param store_clusters_obtained: True if want to access later to the clusters obtained by the scheduler
        """
        super().__init__(activate_debug)
        self.__scheduling_points: Dict[int, Dict[int, int]] = {}
        self.__major_cycle: float = 0
        self.__task_to_job: Dict[int, int] = {}

        # Store the number of CPUs in each cluster
        self.__clusters_obtained: Optional[List[int]] = [] if store_clusters_obtained else None

    def get_clusters_obtained(self) -> Optional[List[int]]:
        """
        Return the configuration of the clusters obtained
        :return: number of cpus in each cluster
        """
        return self.__clusters_obtained

    def check_schedulability(self, processor_definition: ProcessorDefinition,
                             environment_specification: EnvironmentSpecification, task_set: TaskSet) -> [bool,
                                                                                                         Optional[str]]:
        """
        Return true if the scheduler can be able to schedule the system. In negative case, it can return a reason.
        In example, a scheduler that only can work with periodic tasks with phase=0, can return
         [false, "Only can schedule tasks with phase=0"]

        :param environment_specification: Specification of the environment
        :param processor_definition: Specification of the cpu
        :param task_set: Tasks in the system
        :return CPU frequency
        """
        only_0_phase = all(i.phase is None or i.phase == 0 for i in task_set.periodic_tasks)

        only_periodic_tasks = len(task_set.sporadic_tasks) + len(task_set.aperiodic_tasks) == 0

        only_implicit_deadline = all(i.relative_deadline == i.period for i in task_set.periodic_tasks)

        only_fully_preemptive = all(i.preemptive_execution == PreemptiveExecution.FULLY_PREEMPTIVE
                                    for i in task_set.periodic_tasks)

        if not (only_0_phase and only_periodic_tasks and only_implicit_deadline and only_fully_preemptive):
            return False, "Error: Only implicit deadline, fully preemptive, 0 phase periodic tasks are allowed"

        return True, None

    def offline_stage(self, processor_definition: ProcessorDefinition,
                      environment_specification: EnvironmentSpecification, task_set: TaskSet) -> int:
        """
        Method to implement with the offline stage scheduler tasks

        :param environment_specification: Specification of the environment
        :param processor_definition: Specification of the cpu
        :param task_set: Tasks in the system
        :return CPU frequency
        """
        # Select always the maximum frequency
        selected_frequency = max(Set.intersection(
            *[i.core_type.available_frequencies for i in processor_definition.cores_definition.values()]))

        task_set_run = [_RUNTask(i.identification, i.worst_case_execution_time,
                                 int(i.period * selected_frequency)) for i in task_set.periodic_tasks]

        major_cycle = calculate_major_cycle(task_set)

        major_cycle_in_cycles = list_int_lcm([int(i.period * selected_frequency)
                                              for i in task_set.periodic_tasks])

        used_cycles = sum([i.c * (major_cycle_in_cycles // i.d) for i in task_set_run])

        m = len(processor_definition.cores_definition)

        free_cycles = major_cycle_in_cycles * m - used_cycles

        if free_cycles != 0:
            task_set_run.append(_RUNTask(-1, free_cycles, major_cycle_in_cycles))

        run_tree = _create_tree(task_set_run)

        if self.__clusters_obtained is not None:
            self.__clusters_obtained = [round(_obtain_utilization_of_run_pack_subtree(i)) for i in run_tree]

        # Tasks periods in cycles
        tasks_periods_cycles: Dict[int, int] = {i.identification: int(i.period * selected_frequency) for i in
                                                task_set.periodic_tasks}

        # Compute the schedule for a major cycle
        scheduling_points: Dict[int, Dict[int, int]] = {}

        previous_tasks_being_executed: List[int] = m * [-1]

        for actual_cycle in range(0, major_cycle_in_cycles):
            selected_tasks = _select_tasks_to_execute(run_tree, actual_cycle)
            tasks_being_executed = _assign_tasks_to_cpu(selected_tasks, previous_tasks_being_executed, m)

            # Mark for scheduling point
            if previous_tasks_being_executed != tasks_being_executed or any(
                    actual_cycle % tasks_periods_cycles[i] == 0 for i in tasks_being_executed if i != -1):
                scheduling_points[actual_cycle] = {i: j for i, j in enumerate(tasks_being_executed) if j != -1}

            previous_tasks_being_executed = tasks_being_executed

        self.__scheduling_points = scheduling_points
        self.__major_cycle = major_cycle

        return selected_frequency

    def schedule_policy(self, global_time: float, active_jobs_id: Set[int], jobs_being_executed_id: Dict[int, int],
                        cores_frequency: int, cores_max_temperature: Optional[Dict[int, float]]) \
            -> Tuple[Dict[int, int], Optional[int], Optional[int]]:
        """
        Method to implement with the actual scheduler police

        :param global_time: Time in seconds since the simulation starts
        :param jobs_being_executed_id: Ids of the jobs that are currently executed on the system. The dictionary has as
         key the CPU id (it goes from 0 to number of CPUs - 1), and as value the job id.
        :param active_jobs_id: Identifications of the jobs that are currently active
         (look in :ref:..system_definition.DeadlineCriteria for more info) and can be executed.
        :param cores_frequency: Frequencies of cores on the scheduler invocation in Hz.
        :param cores_max_temperature: Max temperature of each core. The dictionary has as
         key the CPU id, and as value the temperature in Kelvin degrees.
        :return: Tuple of [
         Jobs CPU assignation. The dictionary has as key the CPU id, and as value the job id,
         Cycles to execute until the next invocation of the scheduler. If None, it won't be executed until a system
         event trigger its invocation,
         CPU frequency. If None, it will maintain the last used frequency (cores_frequency)
        ]
        """
        actual_execution_cycle = round(global_time * cores_frequency) % round(self.__major_cycle * cores_frequency)

        next_scheduling_point = next(i for i in sorted(self.__scheduling_points.keys()) +
                                     [round(self.__major_cycle * cores_frequency)] if i > actual_execution_cycle)

        return ({k: self.__task_to_job[v] for k, v in self.__scheduling_points[actual_execution_cycle].items()},
                next_scheduling_point - actual_execution_cycle, None)

    def on_jobs_activation(self, global_time: float, activation_time: float,
                           jobs_id_tasks_ids: List[Tuple[int, int]]) -> bool:
        """
        Method to implement with the actual on job activation scheduler police.
        This method is the recommended place to detect the arrival of an aperiodic or sporadic task.

        :param jobs_id_tasks_ids: List[Identification of the job that have been activated,
         Identification of the task which job have been activated]
        :param global_time: Actual time in seconds since the simulation starts
        :param activation_time: Time where the activation was produced (It can be different from the global_time in the
         case that it doesn't adjust to a cycle end)
        :return: true if want to immediately call the scheduler (schedule_policy method), false otherwise
        """
        for job_id, task_id in jobs_id_tasks_ids:
            self.__task_to_job[task_id] = job_id

        return super().on_jobs_activation(global_time, activation_time, jobs_id_tasks_ids)
