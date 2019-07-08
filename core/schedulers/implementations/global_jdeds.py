import math
from typing import List, Optional

import scipy

from core.problem_specification_models.GlobalSpecification import GlobalSpecification
from core.schedulers.templates.abstract_global_scheduler import AbstractGlobalScheduler, GlobalSchedulerPeriodicTask, \
    GlobalSchedulerAperiodicTask, GlobalSchedulerTask

import scipy.optimize
import scipy.linalg


class GlobalJDEDSScheduler(AbstractGlobalScheduler):
    """
    Implements a revision of the global earliest deadline first scheduler where affinity of tasks to processors have been
    got in mind and frequency too
    """

    def __init__(self) -> None:
        super().__init__()

        # Declare class variables
        self.__m = None
        self.__n = None
        self.__intervals_end = None
        self.__execution_by_intervals = None
        self.__execution_by_intervals_all_freq = None
        self.__interval_cc_left = None
        self.__actual_interval_end = None
        self.__actual_interval_index = None
        self.__dt = None
        self.__f_star = None

        # Decimals precision
        self.__decimals_precision = None

    @staticmethod
    def ilpp_dp(ci: List[int], ti: List[int], n: int, m: int) -> [scipy.ndarray, scipy.ndarray,
                                                                  scipy.ndarray]:
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

        # FIXME: Presolve = False may be only a temporal solution
        res = scipy.optimize.linprog(c=f, A_ub=a, b_ub=b, A_eq=a_eq,
                                     b_eq=b_eq, method='simplex', options={"presolve": False})
        if not res.success:
            # No solution found
            raise Exception("Error: No solution found when trying to solve the lineal programing problem")

        x = res.x

        # Partitioning

        i = 0
        s = scipy.zeros((n, number_of_interval - 1))  # FIXME: REVIEW
        for k in range(number_of_interval - 1):
            s[0:n, k] = x[i:i + n]
            i = i + n

        return s, sd, hyperperiod, isd

    def offline_stage(self, global_specification: GlobalSpecification,
                      periodic_tasks: List[GlobalSchedulerPeriodicTask],
                      aperiodic_tasks: List[GlobalSchedulerAperiodicTask]) -> float:
        """
        Method to implement with the offline stage scheduler tasks
        :param aperiodic_tasks: list of aperiodic tasks with their assigned ids
        :param periodic_tasks: list of periodic tasks with their assigned ids
        :param global_specification: Global specification
        :return: 1 - Scheduling quantum (default will be the step specified in problem creation)
        """
        self.__m = global_specification.cpu_specification.number_of_cores
        self.__n = len(global_specification.tasks_specification.periodic_tasks)

        self.__decimals_precision = global_specification.simulation_specification.float_round

        # Calculate F start
        f_max = global_specification.cpu_specification.clock_available_frequencies[-1]
        phi_min = global_specification.cpu_specification.clock_available_frequencies[0]
        phi_start = max(phi_min, sum([i.c / i.t for i in periodic_tasks]) / (self.__m * f_max))

        possible_f = [x for x in global_specification.cpu_specification.clock_available_frequencies if x >= phi_start]
        if len(possible_f) == 0:
            possible_f = [f_max]
            raise Exception("Warning: Schedule is not feasible")

        # F star in HZ
        possible_f_hz = [round(f * global_specification.cpu_specification.clock_base_frequency) for f in possible_f]

        # Number of cycles

        cci = [int(a.c * global_specification.cpu_specification.clock_base_frequency) for a in periodic_tasks]

        tci_list = [[int(a.t * i) for a in periodic_tasks] for i in possible_f_hz]

        # Add dummy task if needed
        hyperperiod_hz_list = [int(global_specification.tasks_specification.h * i) for i in possible_f_hz]

        a_i_list = [[int(tci_h[1] / i) for i in tci_h[0]] for tci_h in zip(tci_list, hyperperiod_hz_list)]

        total_used_cycles_list = [sum([i[0] * i[1] for i in zip(cci, a_i)]) for a_i in a_i_list]

        dummy_task_ci_list = []
        dummy_task_ti_list = []

        for i in range(len(possible_f_hz)):
            total_used_cycles = total_used_cycles_list[i]
            if total_used_cycles < self.__m * hyperperiod_hz_list[i]:
                dummy_task_ci_list.append(int(self.__m * hyperperiod_hz_list[i] - total_used_cycles))
                dummy_task_ti_list.append(hyperperiod_hz_list[i])
            else:
                dummy_task_ci_list.append([])
                dummy_task_ti_list.append([])

        sd = None
        x_list = []

        for i in range(len(possible_f_hz)):
            # Linear programing problem
            x, sd, _, _ = self.ilpp_dp(cci + dummy_task_ci_list[i], tci_list[i] + dummy_task_ti_list[i],
                                       len(tci_list[i] + dummy_task_ti_list[i]), self.__m)
            x_list.append(x)

        # isd = isd / (f_star * global_specification.cpu_specification.clock_base_frequency)
        sd_list = [sd / i for i in possible_f_hz]
        x_list = [x_list[i] / possible_f_hz[i] for i in range(len(possible_f_hz))]

        for i in range(len(possible_f_hz)):
            # Delete dummy task
            if len(dummy_task_ci_list[i]) == 0:
                x_list[i] = x_list[i][:-1, :]

        for i in range(len(possible_f_hz)):
            sd_list[i] = sd_list[1:]

        # All intervals
        self.__intervals_end = [round(i, self.__decimals_precision) for i in sd_list[0]]

        # All executions by intervals
        self.__execution_by_intervals = x_list[0]

        # [(cc left in the interval, task id)]
        self.__interval_cc_left = [(i[0], i[1].id) for i in
                                   zip((self.__execution_by_intervals[0][:, 0]).reshape(-1), periodic_tasks)]

        # Time when the interval end
        self.__actual_interval_end = self.__intervals_end[0]

        # Index of the actual interval
        self.__actual_interval_index = 0

        # Quantum
        self.__dt = super().offline_stage(global_specification, periodic_tasks, aperiodic_tasks)

        # Processor frequencies
        self.__f_star = possible_f[0]

        # Available f for aperiodic
        self.__f_star_available = possible_f
        self.x_possible = x_list

        return self.__dt

    def aperiodic_arrive(self, time: float, executable_tasks: List[GlobalSchedulerTask], active_tasks: List[int],
                         actual_cores_frequency: List[float], cores_max_temperature: Optional[scipy.ndarray],
                         aperiodic_task_ids: List[int]) -> bool:
        """
        Method to implement with the actual on aperiodic arrive scheduler police
        :param actual_cores_frequency: Frequencies of cores
        :param time: actual simulation time passed
        :param executable_tasks: actual tasks that can be executed ( c > 0 and arrive_time <= time)
        :param active_tasks: actual id of tasks assigned to cores (task with id -1 is the idle task)
        :param cores_max_temperature: temperature of each core
        :param aperiodic_task_ids: ids of the aperiodic tasks arrived
        :return: true if want to immediately call the scheduler (schedule_policy method), false otherwise
        """
        # Nothing to do
        return False

    def __sp_interrupt(self, active_tasks: List[int], time: float) -> bool:
        """
        Check if a schedule is necessary
        :param active_tasks: actual tasks in execution
        :param time:
        :return: true if need to schedule
        """
        # True if any task have ended in this step
        tasks_have_ended = any([round(i[0], self.__decimals_precision) <= 0 and i[1] in active_tasks
                                for i in self.__interval_cc_left])

        # True if any task laxity is 0
        executable_tasks_interval = [i for i in self.__interval_cc_left if round(i[0], self.__decimals_precision) > 0.0]
        tasks_laxity_zero = any([round(self.__actual_interval_end - time - i[0], self.__decimals_precision) <= 0
                                 for i in executable_tasks_interval])

        # True if new quantum has started (True if any task has arrived in this step)
        new_quantum_start = round(time, self.__decimals_precision) in (self.__intervals_end + [0.0])

        # True if new aperiodic has arrived
        # TODO:

        return tasks_have_ended or tasks_laxity_zero or new_quantum_start

    def __schedule_policy_imp(self, time: float, active_tasks: List[int]) -> List[int]:
        """
        Assign tasks to cores
        :param time: actual time
        :param active_tasks: actual tasks in execution
        :return: next tasks to execute
        """
        # Contains tasks that can be executed
        executable_tasks = [i for i in self.__interval_cc_left if round(i[0], self.__decimals_precision) > 0.0]

        # Contains all zero laxity tasks
        interval_time_left = self.__actual_interval_end - time
        tasks_laxity_zero = [i[1] for i in executable_tasks if
                             round(interval_time_left - i[0], self.__decimals_precision) <= 0]

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
        tasks_to_execute = tasks_laxity_zero + active_tasks_to_execute + executable_tasks + self.__m * [-1]

        return tasks_to_execute[:self.__m]

    def schedule_policy(self, time: float, executable_tasks: List[GlobalSchedulerTask], active_tasks: List[int],
                        actual_cores_frequency: List[float], cores_max_temperature: Optional[scipy.ndarray]) -> \
            [List[int], Optional[float], Optional[List[float]]]:
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
        new_quantum_start = round(time, self.__decimals_precision) == self.__actual_interval_end
        if new_quantum_start:
            self.__actual_interval_index += 1
            self.__actual_interval_end = self.__intervals_end[self.__actual_interval_index]
            self.__interval_cc_left = [(i[0], i[1][1]) for i in
                                       zip(self.__execution_by_intervals[:, self.__actual_interval_index],
                                           self.__interval_cc_left)]

        # Obtain new tasks to execute
        tasks_to_execute = active_tasks
        if self.__sp_interrupt(active_tasks, time):
            tasks_to_execute = self.__schedule_policy_imp(time, active_tasks)

        # Update cc in tasks being executed
        self.__interval_cc_left = [(i[0] - self.__dt, i[1]) if i[1] in tasks_to_execute else i for i in
                                   self.__interval_cc_left]

        # Do affinity
        for i in range(self.__m):
            actual = active_tasks[i]
            for j in range(self.__m):
                if tasks_to_execute[j] == actual and actual_cores_frequency[j] == actual_cores_frequency[i]:
                    tasks_to_execute[j], tasks_to_execute[i] = tasks_to_execute[i], tasks_to_execute[j]

        return tasks_to_execute, None, self.__m * [self.__f_star]
