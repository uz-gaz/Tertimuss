import math
from typing import List, Optional

import scipy

from core.kernel_generator.global_model import GlobalModel
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
        self.__m = None

    def ilpp_dp(self, ci: List[float], ti: List[float], n: int, m: int) -> [scipy.ndarray, scipy.ndarray,
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

        # Calculate F start
        f_max = global_specification.cpu_specification.clock_available_frequencies[-1]
        phi_min = global_specification.cpu_specification.clock_available_frequencies[0]
        phi_start = max(phi_min,
                        sum(map(lambda task: task.c / task.t, periodic_tasks)) / (
                                self.__m * f_max))

        f_star = next(
            (x for x in global_specification.cpu_specification.clock_available_frequencies if x >= phi_start), f_max)

        cc = list(map(lambda a: a.c / f_star, periodic_tasks))  # FIXME: Check this

        cpu_utilization = sum(map(lambda a: a[0] / a[1].t, zip(cc, periodic_tasks)))

        # Exit program if can schedule
        if cpu_utilization >= self.__m:
            raise Exception("Error: Schedule is not feasible")

        dummy_task = False
        cc_dummy = 0
        ti_dummy = global_specification.tasks_specification.h

        # Add dummy task
        if cpu_utilization < self.__m:
            h = global_specification.tasks_specification.h
            cc_dummy = (self.__m - sum(
                map(lambda a: a.c / a.t, global_specification.tasks_specification.tasks))) * f_star * h

        # Number of cycles
        cci = list(map(lambda a: a.c * global_specification.cpu_specification.clock_base_frequency,
                       periodic_tasks)) + ([cc_dummy * global_specification.cpu_specification.clock_base_frequency]
                                           if dummy_task else [])

        tci = list(map(lambda a: a.t * f_star * global_specification.cpu_specification.clock_base_frequency,
                       periodic_tasks)) + ([ti_dummy * global_specification.cpu_specification.clock_base_frequency]
                                           if dummy_task else [])

        # Linear programing problem
        x, sd, _, _ = self.ilpp_dp(cci, tci, self.__n, self.__m)

        # isd = isd / (f_star * global_specification.cpu_specification.clock_base_frequency)
        sd = sd / (f_star * global_specification.cpu_specification.clock_base_frequency)
        x = x / (f_star * global_specification.cpu_specification.clock_base_frequency)

        # All intervals
        self.__intervals_end = sd[1:]

        # All executions by intervals
        self.__execution_by_intervals = x

        # [(cc left in the interval, task id)]
        self.__interval_cc_left = [(i[0], i[1].id) for i in zip([x[0], periodic_tasks])]

        # Time when the interval end
        self.__interval_end = sd[1]

        return super().offline_stage(global_specification, periodic_tasks, aperiodic_tasks)

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
        # TODO: Implement
        alive_tasks = [x for x in executable_tasks if x.next_arrival <= time]
        task_order = scipy.argsort(list(map(lambda x: x.next_deadline, alive_tasks)))
        tasks_to_execute = ([alive_tasks[i].id for i in task_order] + (self.__m - len(alive_tasks)) * [-1])[0:self.__m]

        # Assign highest priority task to faster processor
        tasks_to_execute = [x for _, x in sorted(zip(actual_cores_frequency, tasks_to_execute), reverse=True)]

        # Do affinity
        for i in range(self.__m):
            actual = active_tasks[i]
            for j in range(self.__m):
                if tasks_to_execute[j] == actual and actual_cores_frequency[j] == actual_cores_frequency[i]:
                    tasks_to_execute[j], tasks_to_execute[i] = tasks_to_execute[i], tasks_to_execute[j]
        return tasks_to_execute, None, None
