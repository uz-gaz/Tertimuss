import functools
import heapq
import math
from typing import List, Optional, Union, Tuple, Dict, Set

import numpy
from ortools.linear_solver import pywraplp

from tertimuss_simulation_lib.math_utils import list_float_lcm, list_int_gcd
from tertimuss_simulation_lib.schedulers_definition import CentralizedAbstractScheduler
from tertimuss_simulation_lib.system_definition import HomogeneousCpuSpecification, EnvironmentSpecification, TaskSet


class ALECSScheduler(CentralizedAbstractScheduler):
    """
    Implements the AIECS scheduler
    """

    def __init__(self, number_of_major_cycles: int = 1) -> None:
        super().__init__(True)

        # Declare class variables
        self.__scheduling_points: Dict[int, Dict[int, int]] = {}
        # self.__m = None
        # self.__n = None
        # self.__intervals_end = None
        # self.__execution_by_intervals = None
        # self.__interval_cc_left = None
        # self.__actual_interval_index = None
        # self.__dt = None
        # self.__aperiodic_arrive = None
        # self.__possible_f = None
        # self.__intervals_frequencies = None
        # self.__number_of_major_cycles = number_of_major_cycles
        # self.__index_to_id = None
        # self.__id_to_index = None

    @staticmethod
    def __list_lcm(values: List[int]) -> int:
        return functools.reduce(lambda a, b: abs(a * b) // math.gcd(a, b), values)

    @classmethod
    def aiecs_periods_lpp_glop(cls, ci: List[int], ti: List[int], number_of_cpus: int) \
            -> Optional[Tuple[List[int], List[List[int]]]]:
        """
        Solves the linear programing problem
        :param ci: execution cycles of each task
        :param ti: period in cycles of each task
        :param number_of_cpus: number of cpus
        :return: 1 -> tasks execution each interval
                 2 -> intervals
        """
        # Check number of tasks
        if len(ci) != len(ti):
            return None

        number_of_tasks = len(ci)

        # Hyper-period creation
        hyper_period = cls.__list_lcm(ti)

        # Check task set utilization
        utilization = sum([i * (hyper_period // j) for i, j in zip(ci, ti)])

        # Check utilization
        if utilization != number_of_cpus * hyper_period:
            return None

        # Create deadlines list
        deadline_list = sorted(set([j for i in ti for j in range(i, hyper_period + i, i)]))
        partitions_size = [i - j for i, j in zip(deadline_list, [0] + deadline_list[:-1])]

        # Number of partitions
        number_of_partitions = len(partitions_size)

        # Create solver
        solver = pywraplp.Solver.CreateSolver('linear_programming_examples', 'GLOP')

        # Create variables [task, period]
        variables_list = [
            [solver.NumVar(0, solver.infinity(), "x_" + str(i) + "_" + str(j)) for j in range(number_of_partitions)] for
            i
            in range(number_of_tasks)]

        # Utilization constraint
        for partition_index, partition_size in enumerate(partitions_size):
            utilization_constraint = solver.Constraint(partition_size * number_of_cpus, partition_size * number_of_cpus)
            for task_index in range(number_of_tasks):
                utilization_constraint.SetCoefficient(variables_list[task_index][partition_index], 1)

        # # Store the partitions that use each job [task][job][partition index]
        jobs_used_partitions = [
            [[partition_index for partition_index, deadline in enumerate(deadline_list) if
              job_start < deadline <= job_end]
             for job_start, job_end in zip(range(0, hyper_period, t), range(t, hyper_period + t, t))] for t in ti]

        # Execution constraint
        for task_index, (task_jobs, task_ci) in enumerate(zip(jobs_used_partitions, ci)):
            for job_partitions_indexes in task_jobs:
                execution_constraint = solver.Constraint(task_ci, task_ci)
                for partition_index in job_partitions_indexes:
                    execution_constraint.SetCoefficient(variables_list[task_index][partition_index], 1)

        # Laxity constraint
        for task_index, (task_jobs, task_ci) in enumerate(zip(jobs_used_partitions, ci)):
            for job_partitions_indexes in task_jobs:
                for partition_index_index, partition_index_k in enumerate(job_partitions_indexes[:-1]):
                    time_to_deadline = sum(
                        [partitions_size[i] for i in job_partitions_indexes[partition_index_index + 1:]])
                    laxity_constraint = solver.Constraint(max(0, task_ci - time_to_deadline), solver.infinity())
                    for partition_index_mu in job_partitions_indexes[:partition_index_index + 1]:
                        laxity_constraint.SetCoefficient(variables_list[task_index][partition_index_mu], 1)

        # Sequential constraint
        for partition_index, partition_size in enumerate(partitions_size):
            for task_index in range(number_of_tasks):
                sequential_constraint = solver.Constraint(-solver.infinity(), partition_size)
                sequential_constraint.SetCoefficient(variables_list[task_index][partition_index], 1)

        # Objective
        objective = solver.Objective()
        for partition_index, partition_size in enumerate(partitions_size):
            for task_index in range(number_of_tasks):
                objective.SetCoefficient(variables_list[task_index][partition_index], 1)
        objective.SetMaximization()

        # Solve the system
        status = solver.Solve()

        # Debug info
        if status == solver.OPTIMAL:
            return ([0] + deadline_list), [
                [round(variables_list[i][j].solution_value()) for j in range(number_of_partitions)] for
                i in range(number_of_tasks)]
        elif status == solver.FEASIBLE:
            print('A potentially suboptimal solution was found.')
            return ([0] + deadline_list), [
                [round(variables_list[i][j].solution_value()) for j in range(number_of_partitions)] for
                i in range(number_of_tasks)]
        else:
            print('The solver could not solve the problem.')
            return None

    def check_schedulability(self, cpu_specification: Union[HomogeneousCpuSpecification],
                             environment_specification: EnvironmentSpecification, task_set: TaskSet) \
            -> [bool, Optional[str]]:
        # TODO: Only implicit deadline, fully preemptive task-sets without phase in the periodic tasks are allowed,
        # and simulaton start in second 0

        m = cpu_specification.cores_specification.number_of_cores

        clock_available_frequencies = list(cpu_specification.cores_specification.available_frequencies)

        # Calculate F start
        major_cycle = list_float_lcm([i.relative_deadline for i in task_set.periodic_tasks])

        available_frequencies = [actual_frequency for actual_frequency in clock_available_frequencies
                                 if sum([i.worst_case_execution_time * round(major_cycle / i.relative_deadline)
                                         for i in task_set.periodic_tasks]) <= m * round(major_cycle * actual_frequency)
                                 and all([i.worst_case_execution_time * round(major_cycle / i.relative_deadline)
                                          <= round(major_cycle * actual_frequency) for i in task_set.periodic_tasks])]

        if len(available_frequencies) == 0:
            return True, "Error: Schedule is not feasible"
        else:
            return True, None

    @staticmethod
    def __offline_stage_check_interrupt(tasks_being_executed: List[int], interval_cc_left: List[int],
                                        cycles_in_this_interval: int, new_interval_start: bool) -> bool:
        """
        Check if a schedule is necessary
        :param tasks_being_executed: actual tasks in execution
        :param interval_cc_left: CC left of each task in this interval
        :param cycles_in_this_interval: Cycles left in this interval
        :param new_interval_start: True if new interval have start this cycle
        :return: True if need to schedule
        """
        # Condition 1: True if new interval have started
        # Condition 2: True if any task have ended in this step
        # Condition 3: True if any task laxity is 0
        return new_interval_start or \
               any(interval_cc_left[i] == 0 for i in tasks_being_executed) or \
               any(j == cycles_in_this_interval and i not in tasks_being_executed for i, j in
                   enumerate(interval_cc_left))

    @staticmethod
    def __schedule_policy_imp(tasks_being_executed: List[int], interval_cc_left: List[int],
                              cycles_in_this_interval: int) -> List[int]:
        """
        Assign tasks to cores
        :param tasks_being_executed: actual tasks in execution
        :param interval_cc_left: CC left of each task in this interval
        :param cycles_in_this_interval: Cycles left in this interval
        :param new_interval_start: True if new interval have start this cycle
        :return: next tasks to execute
        """
        m = len(tasks_being_executed)

        # Contains tasks that can be executed
        executable_tasks = [(i, j) for i, j in enumerate(interval_cc_left) if j > 0]

        # Contains all zero laxity tasks
        tasks_laxity_zero = [i for (i, j) in executable_tasks if j == cycles_in_this_interval]

        # Update executable tasks
        executable_tasks_middle_priority = [(i, j) for (i, j) in executable_tasks if j != cycles_in_this_interval]

        # Select active tasks
        active_tasks_to_execute = [i for (i, j) in executable_tasks_middle_priority if i in tasks_being_executed]

        # Update executable tasks
        executable_tasks_low_priority = [(i, j) for (i, j) in executable_tasks_middle_priority if
                                         i not in active_tasks_to_execute]

        if len(tasks_laxity_zero) + len(active_tasks_to_execute) < m:
            # Only in this case we will select tasks that wasn't being executed and dont have laxity zero
            elements_to_obtain = m - (len(tasks_laxity_zero) + len(active_tasks_to_execute))
            low_priority_tasks = heapq.nlargest(min(elements_to_obtain, len(executable_tasks_low_priority)),
                                                executable_tasks_low_priority,
                                                key=lambda i: i[1])
        else:
            low_priority_tasks = []

        # Tasks with laxity zero, active tasks, rest of the tasks, idle tasks
        tasks_to_execute = (tasks_laxity_zero + active_tasks_to_execute + [i for (i, j) in low_priority_tasks] + (
                m * [-1]))[:m]

        # Do affinity, this is a little improvement over the original algorithm
        for i in range(m):
            actual = tasks_being_executed[i]
            for j in range(m):
                if tasks_to_execute[j] == actual and j != i:
                    tasks_to_execute[j], tasks_to_execute[i] = tasks_to_execute[i], tasks_to_execute[j]

        return tasks_to_execute

    def offline_stage(self, cpu_specification: Union[HomogeneousCpuSpecification],
                      environment_specification: EnvironmentSpecification, task_set: TaskSet) -> int:
        m = cpu_specification.cores_specification.number_of_cores
        n = len(task_set.periodic_tasks)

        clock_available_frequencies = list(cpu_specification.cores_specification.available_frequencies)

        # Calculate F start
        major_cycle = list_float_lcm([i.relative_deadline for i in task_set.periodic_tasks])

        available_frequencies = [actual_frequency for actual_frequency in clock_available_frequencies
                                 if sum([i.worst_case_execution_time * round(major_cycle / i.relative_deadline)
                                         for i in task_set.periodic_tasks]) <= m * round(major_cycle * actual_frequency)
                                 and all([i.worst_case_execution_time * round(major_cycle / i.relative_deadline)
                                          <= round(major_cycle * actual_frequency) for i in task_set.periodic_tasks])]

        # F star in HZ
        f_star_hz = min(available_frequencies)

        # Number of cycles
        cci = [i.worst_case_execution_time for i in task_set.periodic_tasks]
        tci = [int(i.relative_deadline * f_star_hz) for i in task_set.periodic_tasks]

        # Add dummy task if needed
        major_cycle_in_cycles = int(major_cycle * f_star_hz)

        a_i = [round(major_cycle_in_cycles / i) for i in tci]

        # Check if it's needed a dummy task
        total_used_cycles = sum([i[0] * i[1] for i in zip(cci, a_i)])

        if total_used_cycles < m * major_cycle_in_cycles:
            cci.append(m * major_cycle_in_cycles - total_used_cycles)
            tci.append(major_cycle_in_cycles)

        # Linear programing problem
        interval_start_list, x = self.aiecs_periods_lpp_glop(cci, tci, m)
        x = numpy.array(x)

        # Delete dummy task
        x = x[:-1, :] if total_used_cycles < m * major_cycle_in_cycles else x

        # Index to id
        index_to_id = {i: j.identification for i, j in enumerate(task_set.periodic_tasks)}
        id_to_index = {j.identification: i for i, j in enumerate(task_set.periodic_tasks)}

        # Low the range of sd, x
        range_quantum = list_int_gcd([x[i, j] for i in range(x.shape[0]) for j in range(x.shape[1]) if x[i, j] != 0] +
                                     [i for i in interval_start_list[1:]])

        # Compute the schedule for a major cycle
        scheduling_points: Dict[int, Dict[int, int]] = {}

        actual_interval_cc: List[int] = []
        actual_interval_end: int = 0

        tasks_being_executed: List[int] = m * [-1]

        for i in range(0, major_cycle_in_cycles, range_quantum):
            # Obtain all assignations
            interval_have_ended_this_cycle = False
            if i == actual_interval_end:
                interval_index = interval_start_list.index(i)
                actual_interval_cc = x[:, interval_index].tolist()
                actual_interval_end = interval_start_list[interval_index + 1]
                interval_have_ended_this_cycle = True

            previous_tasks_being_executed = tasks_being_executed
            if self.__offline_stage_check_interrupt(tasks_being_executed, actual_interval_cc, actual_interval_end - i,
                                                    interval_have_ended_this_cycle):
                tasks_being_executed = self.__schedule_policy_imp(tasks_being_executed, actual_interval_cc,
                                                                  actual_interval_end - i)

            # Update CC
            for j in (r for r in tasks_being_executed if r != -1):
                actual_interval_cc[j] = actual_interval_cc[j] - range_quantum

            # Mark scheduling point
            # TODO: This can be a bit improved, because not not all interval ends the scheduler should
            # be called, neither when a task end his execution
            if interval_have_ended_this_cycle or previous_tasks_being_executed != tasks_being_executed:
                scheduling_points[i] = {i: index_to_id[j] for i, j in enumerate(tasks_being_executed) if j != -1}

        self.__scheduling_points = scheduling_points

        # Only used for debug purposes
        scheduling_points_debug_activated = False

        if scheduling_points_debug_activated:
            scheduling_points_debug = -2 * numpy.ones((m, major_cycle_in_cycles // range_quantum))

            index_sp = {i: max(j for j in scheduling_points.keys() if j <= i * range_quantum) for i in
                        range(major_cycle_in_cycles // range_quantum)}

            for i in range(major_cycle_in_cycles // range_quantum):
                for j in range(m):
                    scheduling_points_debug[j, i] = scheduling_points[index_sp[i]][j] if scheduling_points[
                        index_sp[i]].__contains__(j) else -1

        return f_star_hz

    # def aperiodic_arrive(self, time: float, aperiodic_tasks_arrived: List[SystemTask],
    #                      actual_cores_frequency: List[int], cores_max_temperature: Optional[numpy.ndarray]) -> bool:
    #     """
    #     Method to implement with the actual on aperiodic arrive scheduler police
    #     :param actual_cores_frequency: Frequencies of cores
    #     :param time: actual simulation time passed
    #     :param aperiodic_tasks_arrived: aperiodic tasks arrived in this step (arrive_time == time)
    #     :param cores_max_temperature: temperature of each core
    #     :return: true if want to immediately call the scheduler (schedule_policy method), false otherwise
    #     """
    #     # for actual_task in aperiodic_tasks_arrived:
    #     #     # x in cycles
    #     #     x = self.__execution_by_intervals
    #     #     cc = numpy.asarray([i[0] for i in self.__interval_cc_left])
    #     #
    #     #     # Remaining time for aperiodic in the actual interval for each frequency
    #     #     remaining_actual = [self.__m * (self.__intervals_end[self.__actual_interval_index] - time) - sum(cc / i) for
    #     #                         i in self.__possible_f]
    #     #
    #     #     # Remaining time for aperiodic in full intervals between aperiodic start and its deadline
    #     #     number_of_full_intervals = len(
    #     #         [i for i in self.__intervals_end[self.__actual_interval_index + 1:] if i <= actual_task.next_deadline])
    #     #
    #     #     remaining_full_intervals = [[
    #     #         self.__m * (self.__intervals_end[self.__actual_interval_index + i + 1] - self.__intervals_end[
    #     #             self.__actual_interval_index + i]) - sum(
    #     #             (x[:, self.__actual_interval_index + i + 1]).reshape(-1) / j) for i in
    #     #         range(number_of_full_intervals)] for j in
    #     #         self.__possible_f] if number_of_full_intervals > 0 else len(self.__possible_f) * [0]
    #     #
    #     #     # Remaining time for aperiodic in last interval
    #     #     remaining_last_interval_to_deadline = self.__m * (actual_task.next_deadline - self.__intervals_end[
    #     #         self.__actual_interval_index + number_of_full_intervals])
    #     #
    #     #     remaining_last_interval = [min(
    #     #         self.__intervals_end[self.__actual_interval_index + number_of_full_intervals + 1] -
    #     #         self.__intervals_end[
    #     #             self.__actual_interval_index + number_of_full_intervals] - sum(
    #     #             (x[:, self.__actual_interval_index + number_of_full_intervals + 1]).reshape(-1) / j),
    #     #         remaining_last_interval_to_deadline) for j in
    #     #         self.__possible_f] if remaining_last_interval_to_deadline > 0 else len(self.__possible_f) * [0]
    #     #
    #     #     # Remaining time in each frequency
    #     #     remaining = [(i[0] + sum(i[1]) + i[2], i[3]) for i in
    #     #                  zip(remaining_actual, remaining_full_intervals, remaining_last_interval,
    #     #                      range(len(self.__possible_f)))]
    #     #
    #     #     dt = self.__dt
    #     #
    #     #     possible_f_index = [i[1] for i in remaining if
    #     #                         i[0] >= (math.ceil(actual_task.pending_c / round(self.__possible_f[i[1]] * dt)) * dt)]
    #     #
    #     #     if len(possible_f_index) > 0:
    #     #         self.__aperiodic_arrive = True
    #     #         # Recreate x
    #     #         f_star = self.__possible_f[possible_f_index[0]]
    #     #
    #     #         times_to_execute = [remaining_actual[possible_f_index[0]]] + remaining_full_intervals[
    #     #             possible_f_index[0]] + ([remaining_last_interval[
    #     #                                          possible_f_index[
    #     #                                              0]]] if remaining_last_interval_to_deadline > 0 else [])
    #     #
    #     #         times_to_execute_c_aperiodic = math.ceil(actual_task.pending_c / round(f_star * dt)) * dt
    #     #
    #     #         times_to_execute_cc = [round(i * f_star) for i in times_to_execute]
    #     #
    #     #         # Number of intervals that we will need for the execution
    #     #         intervals_needed = 0
    #     #         remaining_auxiliary = times_to_execute_c_aperiodic * f_star
    #     #
    #     #         while remaining_auxiliary > 0:
    #     #             remaining_auxiliary = remaining_auxiliary - times_to_execute_cc[intervals_needed]
    #     #             intervals_needed = intervals_needed + 1
    #     #
    #     #         times_to_execute_cc[intervals_needed - 1] = times_to_execute_cc[
    #     #                                                         intervals_needed - 1] + remaining_auxiliary
    #     #
    #     #         new_x_row = numpy.zeros((1, len(self.__intervals_end)))
    #     #         new_x_row[0,
    #     #         self.__actual_interval_index: self.__actual_interval_index + intervals_needed] = times_to_execute_cc[
    #     #                                                                                          :intervals_needed]
    #     #
    #     #         self.__execution_by_intervals = numpy.concatenate([self.__execution_by_intervals, new_x_row], axis=0)
    #     #
    #     #         self.__interval_cc_left = self.__interval_cc_left + [
    #     #             (round(self.__execution_by_intervals[-1, self.__actual_interval_index]), actual_task.id)]
    #     #
    #     #         self.__intervals_frequencies[self.__actual_interval_index:
    #     #                                      self.__actual_interval_index + intervals_needed] = intervals_needed * [
    #     #             f_star]
    #     #     else:
    #     #         print("Warning: The aperiodic task can not be executed")
    #
    #     # Not implemented for now
    #     return False

    def schedule_policy(self, global_time: float, active_jobs_id: Set[int],
                        jobs_being_executed_id: Dict[int, int], cores_frequency: int,
                        cores_max_temperature: Optional[Dict[int, float]]) \
            -> Tuple[Dict[int, int], Optional[int], Optional[int]]:
        """
        Method to implement with the actual scheduler police
        :param actual_cores_frequency: Frequencies of cores
        :param time: actual simulation time passed
        :param executable_tasks: actual tasks that can be executed ( c > 0 and arrive_time <= time)
        :param active_tasks: actual id of tasks assigned to cores (task with id -1 is the idle task)
        :param cores_max_temperature: temperature of each core
        :return: 1 - tasks to assign to cores in next step (task with id -1 is the idle task)
                 2 - next quantum size (if None, will be taken the quantum specified in the offline_stage)
                 3 - cores relatives frequencies for the next quantum (if None, will be taken the frequencies specified
                  in the problem specification)
        """
        # Check if new interval have arrived and update everything
        new_interval_start = (round(time / self.__dt) >= round(
            self.__intervals_end[self.__actual_interval_index] / self.__dt))

        if new_interval_start:
            self.__actual_interval_index += 1
            self.__interval_cc_left = [
                (round(i[0]), i[1][1]) for i in zip(self.__execution_by_intervals[:, self.__actual_interval_index],
                                                    self.__interval_cc_left)]

        active_tasks_index = [self.__id_to_index[i] if i != -1 else -1 for i in active_tasks]
        executable_tasks_index = [self.__id_to_index[i.id] for i in executable_tasks]

        # Obtain new tasks to execute
        tasks_to_execute = active_tasks_index
        if self.__sp_interrupt(active_tasks_index, time):
            tasks_to_execute = self.__schedule_policy_imp(time, active_tasks_index,
                                                          [i for i in executable_tasks_index])

        # Update cc in tasks being executed
        self.__interval_cc_left = [
            (round(i[0] - (self.__intervals_frequencies[self.__actual_interval_index] *
                           self.__dt)), i[1]) if i[1] in tasks_to_execute else i
            for i in self.__interval_cc_left]

        # If any task has negative cc left, transform to 0
        self.__interval_cc_left = [i if i[0] > 0 else (0, i[1]) for i in self.__interval_cc_left]

        return [self.__index_to_id[i] if i != -1 else -1 for i in tasks_to_execute], None, self.__m * [
            self.__intervals_frequencies[self.__actual_interval_index]]
