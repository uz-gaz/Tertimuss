from typing import List, Optional

import scipy

from main.core.execution_simulator.system_simulator.SystemAperiodicTask import SystemAperiodicTask
from main.core.execution_simulator.system_simulator.SystemPeriodicTask import SystemPeriodicTask

from main.core.execution_simulator.system_simulator.SystemTask import SystemTask
from main.core.problem_specification.GlobalSpecification import GlobalSpecification
from main.core.schedulers_definition.templates.AbstractScheduler import AbstractScheduler


class RUNServer(object):
    def __init__(self, c: int, d: int):
        self.c = c
        self.d = d
        self.laxity = d - c
        self.pending_c = self.c
        self.pending_laxity = self.laxity
        self.next_arrive = self.d
        self.server_id = id(self)

        # This value will be used to give more priority to the last executed task
        self.last_time_executed_dual = 0
        self.last_time_executed_edf = 0


class RUNPack(RUNServer):
    """
    This class represent the union of a DUAL and an EDF server
    """

    def __init__(self, content: List[RUNServer]):
        self.content = content
        d = int(scipy.gcd.reduce([i.d for i in content]))
        c = int(sum([i.laxity * (d / i.d) for i in content]))
        super().__init__(c, d)


class RUNTask(RUNServer):
    def __init__(self, task_id: int, c: int, d: int):
        self.task_id = task_id
        self.last_cpu_execution = -1
        super().__init__(c, d)


class PacksBin(object):
    def __init__(self, c: int, d: int, packs: List[RUNServer]):
        self.c = c
        self.d = d
        self.packs = packs


class RUNScheduler(AbstractScheduler):
    def __init__(self):
        self.__parents_of_tree = None
        self.__dt = None
        self.__operating_frequency = None
        self.__last_tasks_assignation = None
        self.__m = None

    @classmethod
    def _create_packs_from_virtual_tasks(cls, packs: List[RUNServer]) -> List[RUNPack]:
        started_bins: List[PacksBin] = []

        packs.sort(key=lambda x: x.laxity / x.d, reverse=True)  # Sort packs in descendant order of utilization

        for pack in packs:
            started_bins.sort(key=lambda x: x.c / x.d,
                              reverse=False)  # Sort started bins in ascendant order of utilization

            assigned = False
            index_started_bins = 0
            while not assigned and index_started_bins < len(started_bins):
                actual_bin = started_bins[index_started_bins]
                deadline = scipy.gcd(pack.d, actual_bin.d)
                actual_bin_c = int(actual_bin.c / (actual_bin.d / deadline))
                actual_pack_dual = int(pack.laxity / (pack.d / deadline))

                if actual_pack_dual <= (deadline - actual_bin_c):
                    assigned = True
                    started_bins[index_started_bins].c = actual_bin_c + actual_pack_dual
                    started_bins[index_started_bins].d = deadline
                    started_bins[index_started_bins].packs.append(pack)
                index_started_bins = index_started_bins + 1

            if not assigned:
                started_bins.append(PacksBin(pack.laxity, pack.d, [pack]))
        return [RUNPack(actual_bin.packs) for actual_bin in started_bins]

    @classmethod
    def _create_recursive_tree(cls, packs: List[RUNPack]) -> List[RUNPack]:
        tree_parents: List[RUNPack] = []
        tree_children: List[RUNPack] = []

        for pack in packs:
            if pack.laxity == 0:
                tree_parents.append(pack)
            else:
                tree_children.append(pack)

        if len(tree_children) > 0:
            tree_parents = tree_parents + cls._create_recursive_tree(
                cls._create_packs_from_virtual_tasks(tree_children))

        return tree_parents

    @classmethod
    def _update_virtual_task_info(cls, children: List[RUNServer], actual_time: int):
        for i in children:
            if i.next_arrive <= actual_time:
                # We need update the task info
                i.pending_c = i.c
                i.next_arrive = i.next_arrive + i.d
                i.pending_laxity = i.laxity

            if isinstance(i, RUNPack):
                cls._update_virtual_task_info(i.content, actual_time)

    @classmethod
    def _create_tree(cls, tasks: List[RUNTask]) -> List[RUNPack]:
        packs = cls._create_packs_from_virtual_tasks(tasks)
        parents = cls._create_recursive_tree(packs)
        return parents

    @classmethod
    def _count_tree_levels(cls, parent: RUNPack) -> int:
        """
        Return the number of levels including the root
        :param parent:
        :return:
        """
        count = 1
        actual_parent = parent
        while not isinstance(actual_parent, RUNTask):
            actual_parent = actual_parent.content[0]
            count += 1
        return count

    @classmethod
    def _edf_server_selection(cls, previous_dual_selection: List[RUNPack]) -> List[RUNServer]:
        selection = []

        for server in previous_dual_selection:
            children_with_time_to_execute = [i for i in server.content if i.pending_laxity > 0]
            if len(children_with_time_to_execute) != 0:
                # Order the tasks by the EDF criteria
                children_with_time_to_execute.sort(key=lambda x: x.next_arrive,
                                                   reverse=False)  # Sort packs in ascendant order of arrive
                selected_next_arrive = children_with_time_to_execute[0].next_arrive

                # If there are several tasks with the same priority, the last executed is selected to decrease
                # context changes
                children_with_highest_priority = [i for i in children_with_time_to_execute if
                                                  i.next_arrive == selected_next_arrive]
                children_with_highest_priority.sort(key=lambda x: x.last_time_executed_edf,
                                                    reverse=True)  # Sort packs in descendant order of last execution

                # Append to selection the highest priority task
                selection.append(children_with_highest_priority[0])

        return selection

    @classmethod
    def _select_servers_from_level(cls, level: int, parent: RUNPack) -> List[RUNServer]:
        if level == 0:
            return [parent]
        else:
            to_return = []
            for i in parent.content:
                if isinstance(i, RUNPack):
                    recursive_return = cls._select_servers_from_level(level - 1, i)
                    to_return = to_return + recursive_return
                else:
                    to_return = to_return + [i]

            return to_return

    @classmethod
    def _dual_server_selection(cls, level: int, parent: RUNPack, previous_edf_selection: List[RUNServer]) -> List[
        RUNServer]:
        servers_from_level = cls._select_servers_from_level(level, parent)

        previous_edf_selection_ids = [i.server_id for i in previous_edf_selection]

        servers_not_selected_in_edf = [i for i in servers_from_level if i.server_id not in previous_edf_selection_ids]

        servers_with_pending_c = [i for i in servers_not_selected_in_edf if i.pending_c >= 0]

        return servers_with_pending_c

    @classmethod
    def _select_tasks_to_execute_one_parent(cls, parent: RUNPack, actual_time: int, dt: int) -> List[RUNTask]:
        tree_levels = cls._count_tree_levels(parent)
        dual_selection = [parent]
        for level in range(1, tree_levels):
            # Select servers by EDF
            edf_selection = cls._edf_server_selection(dual_selection)

            # Decrease pending dual_c (laxity) of those servers selected by edf
            for server in edf_selection:
                server.pending_laxity -= dt
                server.last_time_executed_edf = actual_time + dt

            # Select servers from the set of dual servers previously selected
            dual_selection = cls._dual_server_selection(level, parent, edf_selection)

            # Decrease pending c of those servers selected
            for server in dual_selection:
                server.pending_c -= dt
                server.last_time_executed_dual = actual_time + dt

        # In the leafs of the tree, we must have Tasks
        return [i for i in dual_selection if isinstance(i, RUNTask)]

    @classmethod
    def _select_tasks_to_execute(cls, parents: List[RUNPack], actual_time: int, dt: int) -> List[RUNTask]:
        cls._update_virtual_task_info(parents, actual_time)
        tasks_to_execute = []
        for parent in parents:
            actual_tasks = cls._select_tasks_to_execute_one_parent(parent, actual_time, dt)
            tasks_to_execute += actual_tasks
        return tasks_to_execute

    @classmethod
    def _assign_tasks_to_cpu(cls, task_set: List[RUNTask], last_tasks_cpu_assignation: List[int], m: int) -> List[int]:
        tasks_assignation = m * [-1]

        not_assigned_yet_phase_1 = []
        # Phase 1
        for i in task_set:
            if i.task_id in last_tasks_cpu_assignation and i.task_id != -1:
                cpu_assigned = last_tasks_cpu_assignation.index(i.task_id)
                tasks_assignation[cpu_assigned] = i.task_id
                # i.last_cpu_execution = cpu_assigned
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

    def offline_stage(self, global_specification: GlobalSpecification, periodic_tasks: List[SystemPeriodicTask],
                      aperiodic_tasks: List[SystemAperiodicTask]) -> float:
        # TODO: We should reduce the frequency to the lowest possible as in JDEDS
        available_frequencies = global_specification.cpu_specification.cores_specification.available_frequencies
        available_frequencies.sort(reverse=True)
        selected_frequency = available_frequencies[-1]

        task_set = [RUNTask(i.id, i.c, round(i.d * selected_frequency)) for i in periodic_tasks]
        h = int(scipy.lcm.reduce([i.d for i in task_set]))

        used_cycles = int(sum([i.c * (h / i.d) for i in task_set]))

        m = len(global_specification.cpu_specification.cores_specification.operating_frequencies)

        free_cycles = h * m - used_cycles

        if free_cycles > 0:
            task_set = task_set + [RUNTask(-1, free_cycles, h)]

        self.__parents_of_tree = self._create_tree(task_set)
        self.__dt = global_specification.simulation_specification.dt
        self.__operating_frequency = m * [selected_frequency]
        self.__last_tasks_assignation = m * [-1]
        self.__m = m

        return global_specification.simulation_specification.dt

    def schedule_policy(self, time: float, executable_tasks: List[SystemTask], active_tasks: List[int],
                        actual_cores_frequency: List[int], cores_max_temperature: Optional[scipy.ndarray]) -> \
            [List[int], Optional[float], Optional[List[int]]]:

        time_cycles = int(time * self.__operating_frequency[0])
        dt_cycles = int(self.__dt * self.__operating_frequency[0])
        iteration_result = self._select_tasks_to_execute(self.__parents_of_tree, time_cycles, dt_cycles)
        iteration_result = self._assign_tasks_to_cpu(iteration_result, self.__last_tasks_assignation, self.__m)
        self.__last_tasks_assignation = iteration_result
        return iteration_result, self.__dt, self.__operating_frequency

    def aperiodic_arrive(self, time: float, aperiodic_tasks_arrived: List[SystemTask],
                         actual_cores_frequency: List[int], cores_max_temperature: Optional[scipy.ndarray]) -> bool:
        return False
