import math
from typing import List, Optional

import scipy

from main.core.problem_specification.GlobalSpecification import GlobalSpecification
from main.core.schedulers.templates.abstract_base_scheduler.AbstractBaseScheduler import AbstractBaseScheduler
from main.core.schedulers.templates.abstract_base_scheduler.BaseSchedulerAperiodicTask import BaseSchedulerAperiodicTask
from main.core.schedulers.templates.abstract_base_scheduler.BaseSchedulerPeriodicTask import BaseSchedulerPeriodicTask
from main.core.schedulers.templates.abstract_base_scheduler.BaseSchedulerTask import BaseSchedulerTask

import scipy.optimize
import scipy.linalg


class GlobalJDEDSScheduler(AbstractBaseScheduler):
    """
    Implements the JDEDS scheduler
    """

    def __init__(self) -> None:
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
        self.__periodic_tasks = None
        self.__intervals_frequencies = None

    @staticmethod
    def ilpp_dp(ci: List[int], ti: List[int], n: int, m: int) -> [scipy.ndarray, scipy.ndarray]:
        """
        Solves the linear programing problem
        :param ci: execution cycles of each task
        :param ti: period in cycles of each task
        :param n: number of tasks
        :param m: number of cpus
        :return: 1 -> tasks execution each interval
                 2 -> intervals
        """
        hyperperiod = scipy.lcm.reduce(ti)

        jobs = list(map(lambda task: int(hyperperiod / task), ti))

        t_star = list(map(lambda task: task[1] - task[0], zip(ci, ti)))

        d = scipy.zeros((n, max(jobs)))

        for i in range(n):
            d[i, :jobs[i]] = (scipy.arange(ti[i], hyperperiod, ti[i]).tolist() + [hyperperiod])

        sd = d[0, 0:jobs[0]]

        for i in range(1, n):
            sd = scipy.union1d(sd, d[i, 0:jobs[i]])

        sd = scipy.union1d(sd, [0])

        number_of_interval = len(sd)

        # Intervals length
        isd = scipy.asarray([sd[j + 1] - sd[j] for j in range(number_of_interval - 1)])

        # Number of variables
        v = n * (number_of_interval - 1)

        # Restrictions
        # - Cpu utilization
        aeq_1 = scipy.linalg.block_diag(*((number_of_interval - 1) * [scipy.ones(n)]))
        beq_1 = scipy.asarray([j * m for j in isd]).reshape((-1, 1))

        aeq_2 = scipy.zeros((v, v))
        a_1 = scipy.zeros((v, v))
        beq_2 = scipy.zeros((v, 1))
        b_1 = scipy.zeros((v, 1))

        # - Temporal
        f1 = 0
        f2 = 0
        for j in range(number_of_interval - 1):
            for i in range(n):
                i_k = 0

                q = math.floor(sd[j + 1] / ti[i])
                r = sd[j + 1] % ti[i]

                for k in range(j + 1):
                    if r == 0:
                        aeq_2[f1, k * n + i] = 1
                    else:
                        a_1[f2, k * n + i] = -1
                    i_k = i_k + isd[k]

                if r == 0:
                    beq_2[f1, 0] = q * ci[i]
                    f1 = f1 + 1
                else:
                    b_1[f2, 0] = -1 * (q * ci[i] - q * ti[i] + max(0, i_k - t_star[i]))
                    f2 = f2 + 1

        def select_non_zero_rows(array_to_filter):
            return scipy.concatenate(list(map(lambda filtered_row: filtered_row.reshape(1, -1), (
                filter(lambda actual_row: scipy.count_nonzero(actual_row) != 0, array_to_filter)))), axis=0)

        aeq_2 = select_non_zero_rows(aeq_2)
        a_1 = select_non_zero_rows(a_1)
        beq_2 = beq_2[0:len(aeq_2), :]
        b_1 = b_1[0:len(a_1), :]

        # Maximum utilization
        a_2 = scipy.identity(v)
        b_2 = scipy.zeros((v, 1))
        f1 = 0
        for j in range(number_of_interval - 1):
            b_2[f1:f1 + n, 0] = isd[j]
            f1 = f1 + n

        a_eq = scipy.concatenate([aeq_1, aeq_2])
        b_eq = scipy.concatenate([beq_1, beq_2])

        a = scipy.concatenate([a_1, a_2])
        b = scipy.concatenate([b_1, b_2])

        f = scipy.full((v, 1), -1)

        # WARNING: "Presolve = False" is a workaround to deal with an issue on the scipy.optimize.linprog library
        res = scipy.optimize.linprog(c=f, A_ub=a, b_ub=b, A_eq=a_eq,
                                     b_eq=b_eq, method='simplex', options={"presolve": False})
        if not res.success:
            # No solution found
            raise Exception("Error: No solution found when trying to solve the lineal programing problem")

        x = res.x

        # Partitioning
        i = 0
        s = scipy.zeros((n, number_of_interval - 1))
        for k in range(number_of_interval - 1):
            s[0:n, k] = x[i:i + n]
            i = i + n

        return s, sd

    def offline_stage(self, global_specification: GlobalSpecification,
                      periodic_tasks: List[BaseSchedulerPeriodicTask],
                      aperiodic_tasks: List[BaseSchedulerAperiodicTask]) -> float:
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
                ((math.ceil(i.c / round(actual_frequency * dt)) * actual_frequency * dt), i.t * actual_frequency) for i
                in periodic_tasks]

            utilization_constraint = sum([i[0] / i[1] for i in tasks_real_cycles]) <= self.__m

            task_period_constraint = all([(i[0] / i[1]) <= 1 for i in tasks_real_cycles])

            if utilization_constraint and task_period_constraint:
                available_frequencies_hz.append(actual_frequency)

        if len(available_frequencies_hz) == 0:
            raise Exception("Error: Schedule is not feasible")

        # F star in HZ
        f_star_hz = available_frequencies_hz[0]

        # Number of cycles
        cci = [i.c for i in periodic_tasks]
        tci = [int(i.t * f_star_hz) for i in periodic_tasks]

        # Add dummy task if needed
        hyperperiod_hz = int(global_specification.tasks_specification.h * f_star_hz)

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
        x, sd = self.ilpp_dp(cci_in_quantums, tci_in_quantums, len(cci_in_quantums), self.__m)

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

        # All intervals
        self.__intervals_end = sd

        # All executions by intervals
        self.__execution_by_intervals = x

        # [(cc left in the interval, task id)]
        self.__interval_cc_left = [(int(i[0]), i[1].id) for i in zip((x[:, 0]).reshape(-1), periodic_tasks)]

        # Index of the actual interval
        self.__actual_interval_index = 0

        # Quantum
        self.__dt = super().offline_stage(global_specification, periodic_tasks, aperiodic_tasks)

        # Processors frequencies in each step
        self.__intervals_frequencies = len(self.__intervals_end) * [f_star_hz]

        # Possible frequencies
        self.__possible_f = available_frequencies_hz

        # True if new aperiodic has arrive
        self.__aperiodic_arrive = False

        # Periodic tasks
        self.__periodic_tasks = periodic_tasks

        return self.__dt

    def aperiodic_arrive(self, time: float, aperiodic_tasks_arrived: List[BaseSchedulerTask],
                         actual_cores_frequency: List[int], cores_max_temperature: Optional[scipy.ndarray]) -> bool:
        """
        Method to implement with the actual on aperiodic arrive scheduler police
        :param actual_cores_frequency: Frequencies of cores
        :param time: actual simulation time passed
        :param aperiodic_tasks_arrived: aperiodic tasks arrived in this step (arrive_time == time)
        :param cores_max_temperature: temperature of each core
        :return: true if want to immediately call the scheduler (schedule_policy method), false otherwise
        """
        for actual_task in aperiodic_tasks_arrived:
            # x in cycles
            x = self.__execution_by_intervals
            cc = scipy.asarray([i[0] for i in self.__interval_cc_left])

            # Remaining time for aperiodic in the actual interval for each frequency
            remaining_actual = [self.__m * (self.__intervals_end[self.__actual_interval_index] - time) - sum(cc / i) for
                                i in self.__possible_f]

            # Remaining time for aperiodic in full intervals between aperiodic start and its deadline
            number_of_full_intervals = len(
                [i for i in self.__intervals_end[self.__actual_interval_index + 1:] if i <= actual_task.next_deadline])

            remaining_full_intervals = [[
                self.__m * (self.__intervals_end[self.__actual_interval_index + i + 1] - self.__intervals_end[
                    self.__actual_interval_index + i]) - sum(
                    (x[:, self.__actual_interval_index + i + 1]).reshape(-1) / j) for i in
                range(number_of_full_intervals)] for j in
                self.__possible_f] if number_of_full_intervals > 0 else len(self.__possible_f) * [0]

            # Remaining time for aperiodic in last interval
            remaining_last_interval_to_deadline = self.__m * (actual_task.next_deadline - self.__intervals_end[
                self.__actual_interval_index + number_of_full_intervals])

            remaining_last_interval = [min(
                self.__intervals_end[self.__actual_interval_index + number_of_full_intervals + 1] -
                self.__intervals_end[
                    self.__actual_interval_index + number_of_full_intervals] - sum(
                    (x[:, self.__actual_interval_index + number_of_full_intervals + 1]).reshape(-1) / j),
                remaining_last_interval_to_deadline) for j in
                self.__possible_f] if remaining_last_interval_to_deadline > 0 else len(self.__possible_f) * [0]

            # Remaining time in each frequency
            remaining = [(i[0] + sum(i[1]) + i[2], i[3]) for i in
                         zip(remaining_actual, remaining_full_intervals, remaining_last_interval,
                             range(len(self.__possible_f)))]

            dt = self.__dt

            possible_f_index = [i[1] for i in remaining if
                                i[0] >= (math.ceil(actual_task.pending_c / round(self.__possible_f[i[1]] * dt)) * dt)]

            if len(possible_f_index) > 0:
                self.__aperiodic_arrive = True
                # Recreate x
                f_star = self.__possible_f[possible_f_index[0]]

                times_to_execute = [remaining_actual[possible_f_index[0]]] + remaining_full_intervals[
                    possible_f_index[0]] + ([remaining_last_interval[
                                                 possible_f_index[
                                                     0]]] if remaining_last_interval_to_deadline > 0 else [])

                times_to_execute_c_aperiodic = math.ceil(actual_task.pending_c / round(f_star * dt)) * dt

                times_to_execute_cc = [round(i * f_star) for i in times_to_execute]

                # Number of intervals that we will need for the execution
                intervals_needed = 0
                remaining_auxiliary = times_to_execute_c_aperiodic * f_star

                while remaining_auxiliary > 0:
                    remaining_auxiliary = remaining_auxiliary - times_to_execute_cc[intervals_needed]
                    intervals_needed = intervals_needed + 1

                times_to_execute_cc[intervals_needed - 1] = times_to_execute_cc[
                                                                intervals_needed - 1] + remaining_auxiliary

                new_x_row = scipy.zeros((1, len(self.__intervals_end)))
                new_x_row[0,
                self.__actual_interval_index: self.__actual_interval_index + intervals_needed] = times_to_execute_cc[
                                                                                                 :intervals_needed]

                self.__execution_by_intervals = scipy.concatenate([self.__execution_by_intervals, new_x_row], axis=0)

                self.__interval_cc_left = self.__interval_cc_left + [
                    (self.__execution_by_intervals[-1, self.__actual_interval_index], actual_task.id)]

                self.__intervals_frequencies[self.__actual_interval_index:
                                             self.__actual_interval_index + intervals_needed] = intervals_needed * [
                    f_star]
            else:
                print("Warning: The aperiodic task can not be executed")

        return self.__aperiodic_arrive

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
            [int((actual_interval_end - time - (
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
                             int((actual_interval_end - time - (i[0] / self.__intervals_frequencies[
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

    def schedule_policy(self, time: float, executable_tasks: List[BaseSchedulerTask], active_tasks: List[int],
                        actual_cores_frequency: List[int], cores_max_temperature: Optional[scipy.ndarray]) -> \
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
                (i[0], i[1][1]) for i in zip(self.__execution_by_intervals[:, self.__actual_interval_index],
                                             self.__interval_cc_left)]

        # Obtain new tasks to execute
        tasks_to_execute = active_tasks
        if self.__sp_interrupt(active_tasks, time):
            tasks_to_execute = self.__schedule_policy_imp(time, active_tasks, [i.id for i in executable_tasks])

        # Update cc in tasks being executed
        self.__interval_cc_left = [
            (i[0] - (self.__intervals_frequencies[self.__actual_interval_index] *
                     self.__dt), i[1]) if i[1] in tasks_to_execute else i
            for i in self.__interval_cc_left]

        # If any task has negative cc left, transform to 0
        self.__interval_cc_left = [i if i[0] > 0 else (0, i[1]) for i in self.__interval_cc_left]

        # Do affinity, this is a little improvement over the original algorithm
        for i in range(self.__m):
            actual = active_tasks[i]
            for j in range(self.__m):
                if tasks_to_execute[j] == actual and j != i:
                    tasks_to_execute[j], tasks_to_execute[i] = tasks_to_execute[i], tasks_to_execute[j]

        return tasks_to_execute, None, self.__m * [self.__intervals_frequencies[self.__actual_interval_index]]
