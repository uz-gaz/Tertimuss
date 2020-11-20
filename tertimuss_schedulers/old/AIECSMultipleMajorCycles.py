import functools
import math
from typing import List, Optional, Tuple

import numpy
from ortools.linear_solver import pywraplp

from main.core.problem_specification.GlobalSpecification import GlobalSpecification
from main.core.schedulers_definition.templates.AbstractScheduler import AbstractScheduler
from main.core.execution_simulator.system_simulator.SystemAperiodicTask import SystemAperiodicTask
from main.core.execution_simulator.system_simulator.SystemPeriodicTask import SystemPeriodicTask
from main.core.execution_simulator.system_simulator.SystemTask import SystemTask


class AIECSMultipleMajorCyclesScheduler(AbstractScheduler):
    """
    Implements the AIECS scheduler
    """

    def __init__(self, number_of_major_cycles: int) -> None:
        super().__init__()

        # Declare class variables
        self.__m = None
        self.__n = None
        self.__intervals_end = None
        self.__execution_by_intervals = None
        self.__interval_cc_left = None
        self.__actual_interval_index = None
        self.__dt = None
        self.__aperiodic_arrive = None
        self.__possible_f = None
        self.__intervals_frequencies = None
        self.__number_of_major_cycles = number_of_major_cycles
        self.__index_to_id = None
        self.__id_to_index = None

    @staticmethod
    def __list_lcm(values: List[int]) -> int:
        return functools.reduce(lambda a, b: abs(a * b) // math.gcd(a, b), values)

    @classmethod
    def aiecs_periods_lpp_glop(cls, ci: List[int], ti: List[int], number_of_cpus: int) -> Optional[
        Tuple[List[int], List[List[int]]]]:
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

    def offline_stage(self, global_specification: GlobalSpecification,
                      periodic_tasks: List[SystemPeriodicTask],
                      aperiodic_tasks: List[SystemAperiodicTask]) -> float:
        """
        Method to implement with the offline stage scheduler tasks
        :param aperiodic_tasks: list of aperiodic tasks with their assigned ids
        :param periodic_tasks: list of periodic tasks with their assigned ids
        :param global_specification: Global specification
        :return: 1 - Scheduling quantum (default will be the step specified in problem creation)
        """
        self.__m = len(global_specification.cpu_specification.cores_specification.operating_frequencies)
        self.__n = len(global_specification.tasks_specification.periodic_tasks)

        clock_available_frequencies_hz = [i for i in
                                          global_specification.cpu_specification.cores_specification.available_frequencies]

        dt = global_specification.simulation_specification.dt

        # Calculate F start
        # The minimum number cycles you can execute is (frequency * dt). Therefore the real number of cycles you will
        # execute for each task will be ceil(task cc / (frequency * dt)) * (frequency * dt)
        available_frequencies_hz = []

        for actual_frequency in clock_available_frequencies_hz:
            tasks_real_cycles = [
                ((math.ceil(i.c / round(actual_frequency * dt)) * actual_frequency * dt), i.temperature * actual_frequency) for i
                in periodic_tasks]

            # Avoid float errors
            h_cycles = int(global_specification.tasks_specification.convection_factor * actual_frequency)
            utilization_constraint = sum([i[0] * (h_cycles / i[1]) for i in tasks_real_cycles]) <= self.__m * h_cycles

            # utilization_constraint = sum([i[0] / i[1] for i in tasks_real_cycles]) <= self.__m

            task_period_constraint = all([(i[0] / i[1]) <= 1 for i in tasks_real_cycles])

            if utilization_constraint and task_period_constraint:
                available_frequencies_hz.append(actual_frequency)

        if len(available_frequencies_hz) == 0:
            raise Exception("Error: Schedule is not feasible")

        # F star in HZ
        f_star_hz = available_frequencies_hz[0]

        # Number of cycles
        cci = [i.c for i in periodic_tasks]
        tci = [int(i.temperature * f_star_hz) for i in periodic_tasks]

        # Add dummy task if needed
        hyperperiod_hz = int(global_specification.tasks_specification.convection_factor * f_star_hz)

        a_i = [int(hyperperiod_hz / i) for i in tci]

        # Get the number of quantums for which each task will be executed
        cci_in_quantums = [math.ceil(i / round(f_star_hz * dt)) for i in cci]
        tci_in_quantums = [math.ceil(i / round(f_star_hz * dt)) for i in tci]

        # Check if it's needed a dummy task
        total_used_quantums = sum([i[0] * i[1] for i in zip(cci_in_quantums, a_i)])
        hyperperiod_in_quantums = int(hyperperiod_hz / round(f_star_hz * dt))

        if total_used_quantums < self.__m * hyperperiod_in_quantums:
            cci_in_quantums.append(int(round(self.__m * hyperperiod_in_quantums - total_used_quantums)))
            tci_in_quantums.append(hyperperiod_in_quantums)

        # Linear programing problem
        sd, x = self.aiecs_periods_lpp_glop(cci_in_quantums, tci_in_quantums, self.__m)
        sd = numpy.array(sd)
        x = numpy.array(x)

        # Transform from quantums to cycles
        x = x * round(f_star_hz * dt)

        # Transform from quantums to time
        sd = sd * dt

        # Delete dummy task
        if total_used_quantums < self.__m * hyperperiod_in_quantums:
            x = x[:-1, :]

        # Delete deadline 0
        sd = sd[1:]

        # Delete the extra cycles added to x
        for task in range(self.__n):
            if cci[task] % int(round(dt * f_star_hz)) != 0:
                for i in range(a_i[task]):
                    # Obtain last interval where each job is executed
                    intervals_of_execution = [j for j in range(sd.shape[0]) if
                                              i * tci[task] < round(sd[j] * f_star_hz) <= (i + 1) * tci[task] and
                                              sd.shape[0] != 0]
                    last_interval_of_execution = intervals_of_execution[-1]

                    # Delete the extra cycles
                    number_of_extra_cycles = (dt * f_star_hz) - (cci[task] % int(round(dt * f_star_hz)))
                    x[task, last_interval_of_execution] = x[task, last_interval_of_execution] - number_of_extra_cycles

        # Index to id
        self.__index_to_id = {i: j.id for i, j in enumerate(periodic_tasks)}
        self.__id_to_index = {j.id: i for i, j in enumerate(periodic_tasks)}

        # All intervals
        self.__intervals_end = numpy.hstack(
            [sd + (i * global_specification.tasks_specification.convection_factor) for i in range(self.__number_of_major_cycles)])

        # All executions by intervals
        self.__execution_by_intervals = numpy.hstack(self.__number_of_major_cycles * [x])

        # [(cc left in the interval, task id)]
        self.__interval_cc_left = [(round(i[0]), self.__id_to_index[i[1].id]) for i in
                                   zip((x[:, 0]).reshape(-1), periodic_tasks)]

        # Index of the actual interval
        self.__actual_interval_index = 0

        # Quantum
        self.__dt = super().offline_stage(global_specification, periodic_tasks, aperiodic_tasks)

        # Processors frequencies in each step
        self.__intervals_frequencies = (len(self.__intervals_end) * self.__number_of_major_cycles) * [f_star_hz]

        # Possible frequencies
        self.__possible_f = available_frequencies_hz

        # True if new aperiodic has arrive
        self.__aperiodic_arrive = False

        return self.__dt

    def aperiodic_arrive(self, time: float, aperiodic_tasks_arrived: List[SystemTask],
                         actual_cores_frequency: List[int], cores_max_temperature: Optional[numpy.ndarray]) -> bool:
        """
        Method to implement with the actual on aperiodic arrive scheduler police
        :param actual_cores_frequency: Frequencies of cores
        :param time: actual simulation time passed
        :param aperiodic_tasks_arrived: aperiodic tasks arrived in this step (arrive_time == time)
        :param cores_max_temperature: temperature of each core
        :return: true if want to immediately call the scheduler (schedule_policy method), false otherwise
        """
        # for actual_task in aperiodic_tasks_arrived:
        #     # x in cycles
        #     x = self.__execution_by_intervals
        #     cc = numpy.asarray([i[0] for i in self.__interval_cc_left])
        #
        #     # Remaining time for aperiodic in the actual interval for each frequency
        #     remaining_actual = [self.__m * (self.__intervals_end[self.__actual_interval_index] - time) - sum(cc / i) for
        #                         i in self.__possible_f]
        #
        #     # Remaining time for aperiodic in full intervals between aperiodic start and its deadline
        #     number_of_full_intervals = len(
        #         [i for i in self.__intervals_end[self.__actual_interval_index + 1:] if i <= actual_task.next_deadline])
        #
        #     remaining_full_intervals = [[
        #         self.__m * (self.__intervals_end[self.__actual_interval_index + i + 1] - self.__intervals_end[
        #             self.__actual_interval_index + i]) - sum(
        #             (x[:, self.__actual_interval_index + i + 1]).reshape(-1) / j) for i in
        #         range(number_of_full_intervals)] for j in
        #         self.__possible_f] if number_of_full_intervals > 0 else len(self.__possible_f) * [0]
        #
        #     # Remaining time for aperiodic in last interval
        #     remaining_last_interval_to_deadline = self.__m * (actual_task.next_deadline - self.__intervals_end[
        #         self.__actual_interval_index + number_of_full_intervals])
        #
        #     remaining_last_interval = [min(
        #         self.__intervals_end[self.__actual_interval_index + number_of_full_intervals + 1] -
        #         self.__intervals_end[
        #             self.__actual_interval_index + number_of_full_intervals] - sum(
        #             (x[:, self.__actual_interval_index + number_of_full_intervals + 1]).reshape(-1) / j),
        #         remaining_last_interval_to_deadline) for j in
        #         self.__possible_f] if remaining_last_interval_to_deadline > 0 else len(self.__possible_f) * [0]
        #
        #     # Remaining time in each frequency
        #     remaining = [(i[0] + sum(i[1]) + i[2], i[3]) for i in
        #                  zip(remaining_actual, remaining_full_intervals, remaining_last_interval,
        #                      range(len(self.__possible_f)))]
        #
        #     dt = self.__dt
        #
        #     possible_f_index = [i[1] for i in remaining if
        #                         i[0] >= (math.ceil(actual_task.pending_c / round(self.__possible_f[i[1]] * dt)) * dt)]
        #
        #     if len(possible_f_index) > 0:
        #         self.__aperiodic_arrive = True
        #         # Recreate x
        #         f_star = self.__possible_f[possible_f_index[0]]
        #
        #         times_to_execute = [remaining_actual[possible_f_index[0]]] + remaining_full_intervals[
        #             possible_f_index[0]] + ([remaining_last_interval[
        #                                          possible_f_index[
        #                                              0]]] if remaining_last_interval_to_deadline > 0 else [])
        #
        #         times_to_execute_c_aperiodic = math.ceil(actual_task.pending_c / round(f_star * dt)) * dt
        #
        #         times_to_execute_cc = [round(i * f_star) for i in times_to_execute]
        #
        #         # Number of intervals that we will need for the execution
        #         intervals_needed = 0
        #         remaining_auxiliary = times_to_execute_c_aperiodic * f_star
        #
        #         while remaining_auxiliary > 0:
        #             remaining_auxiliary = remaining_auxiliary - times_to_execute_cc[intervals_needed]
        #             intervals_needed = intervals_needed + 1
        #
        #         times_to_execute_cc[intervals_needed - 1] = times_to_execute_cc[
        #                                                         intervals_needed - 1] + remaining_auxiliary
        #
        #         new_x_row = numpy.zeros((1, len(self.__intervals_end)))
        #         new_x_row[0,
        #         self.__actual_interval_index: self.__actual_interval_index + intervals_needed] = times_to_execute_cc[
        #                                                                                          :intervals_needed]
        #
        #         self.__execution_by_intervals = numpy.concatenate([self.__execution_by_intervals, new_x_row], axis=0)
        #
        #         self.__interval_cc_left = self.__interval_cc_left + [
        #             (round(self.__execution_by_intervals[-1, self.__actual_interval_index]), actual_task.id)]
        #
        #         self.__intervals_frequencies[self.__actual_interval_index:
        #                                      self.__actual_interval_index + intervals_needed] = intervals_needed * [
        #             f_star]
        #     else:
        #         print("Warning: The aperiodic task can not be executed")

        # Not implemented for now
        return False

    def __sp_interrupt(self, active_tasks: List[int], time: float) -> bool:
        """
        Check if a schedule is necessary
        :param active_tasks: actual tasks in execution
        :param time:
        :return: true if need to schedule
        """
        # True if any task have ended in this step
        tasks_have_ended = any([i[0] <= 0 and i[1] in active_tasks
                                for i in self.__interval_cc_left])

        # True if any task laxity is 0
        executable_tasks_interval = [i for i in self.__interval_cc_left if i[0] > 0]

        actual_interval_end = self.__intervals_end[self.__actual_interval_index]

        tasks_laxity_zero = any(
            [round((actual_interval_end - time - (
                    i[0] / self.__intervals_frequencies[self.__actual_interval_index])) / self.__dt) <= 0
             and i[1] not in active_tasks for i in executable_tasks_interval])

        # True if new quantum has started (True if any task has arrived in this step)
        new_interval_start = any([round(i / self.__dt) == round(time / self.__dt) for i in self.__intervals_end]) \
                             or time == 0

        # True if new aperiodic has arrived
        aperiodic_arrive = self.__aperiodic_arrive
        self.__aperiodic_arrive = False

        return tasks_have_ended or tasks_laxity_zero or new_interval_start or aperiodic_arrive

    def __schedule_policy_imp(self, time: float, active_tasks: List[int], executable_tasks_proc: List[int]) \
            -> List[int]:
        """
        Assign tasks to cores
        :param time: actual time
        :param active_tasks: actual tasks in execution
        :return: next tasks to execute
        """
        # Contains tasks that can be executed
        executable_tasks = [i for i in self.__interval_cc_left if i[0] > 0]

        actual_interval_end = self.__intervals_end[self.__actual_interval_index]

        # Contains all zero laxity tasks
        tasks_laxity_zero = [i[1] for i in executable_tasks if
                             round((actual_interval_end - time - (i[0] / self.__intervals_frequencies[
                                 self.__actual_interval_index])) / self.__dt) <= 0]

        # Update executable tasks
        executable_tasks = [i for i in executable_tasks if i[1] not in tasks_laxity_zero]

        # Select active tasks
        active_tasks_to_execute = [i[1] for i in executable_tasks if i[1] in active_tasks]

        # Update executable tasks
        executable_tasks = [i for i in executable_tasks if i[1] not in active_tasks_to_execute]

        # Sort the rest of the array
        executable_tasks.sort(reverse=True, key=lambda i: i[0])
        executable_tasks = [i[1] for i in executable_tasks]

        # Tasks with laxity zero, active tasks, rest of the tasks, idle tasks
        tasks_to_execute = tasks_laxity_zero + active_tasks_to_execute + executable_tasks
        tasks_to_execute = [i for i in tasks_to_execute if i in executable_tasks_proc]
        tasks_to_execute = tasks_to_execute + self.__m * [-1]
        return tasks_to_execute[:self.__m]

    def schedule_policy(self, time: float, executable_tasks: List[SystemTask], active_tasks: List[int],
                        actual_cores_frequency: List[int], cores_max_temperature: Optional[numpy.ndarray]) -> \
            [List[int], Optional[float], Optional[List[int]]]:
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

        # Do affinity, this is a little improvement over the original algorithm
        for i in range(self.__m):
            actual = active_tasks_index[i]
            for j in range(self.__m):
                if tasks_to_execute[j] == actual and j != i:
                    tasks_to_execute[j], tasks_to_execute[i] = tasks_to_execute[i], tasks_to_execute[j]

        return [self.__index_to_id[i] if i != -1 else -1 for i in tasks_to_execute], None, self.__m * [
            self.__intervals_frequencies[self.__actual_interval_index]]
