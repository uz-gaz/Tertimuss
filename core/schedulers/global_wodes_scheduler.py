import abc
import math

import scipy

from core.kernel_generator.global_model import GlobalModel
from core.problem_specification_models.GlobalSpecification import GlobalSpecification
from core.problem_specification_models.TasksSpecification import Task
from core.schedulers.abstract_scheduler import AbstractScheduler, SchedulerResult
from typing import List, Optional
from core.schedulers.utils.GlobalModelSolver import GlobalModelSolver
from output_generation.abstract_progress_bar import AbstractProgressBar


class GlobalSchedulerTask(Task):
    def __init__(self, task_specification: Task, task_id: int):
        super().__init__(task_specification.c, task_specification.t, task_specification.e)
        self.next_deadline = task_specification.t
        self.next_arrival = 0
        self.pending_c = task_specification.c
        self.instances = 0
        self.id = task_id


class GlobalWodesScheduler(AbstractScheduler):
    """
    Abstract implementation of global scheduler (Custom Scheduler in original work).
    Method schedule_police must be implemented
    """

    def __init__(self) -> None:
        super().__init__()

    def simulate(self, global_specification: GlobalSpecification, global_model: GlobalModel,
                 progress_bar: Optional[AbstractProgressBar]) -> SchedulerResult:
        """

        :param global_model:
        :param progress_bar:
        :type global_specification: object
        """
        # True if simulation must save temperature
        is_thermal_simulation = global_model.enable_thermal_mode

        idle_task_id = -1
        m = global_specification.cpu_specification.number_of_cores
        n = len(global_specification.tasks_specification.tasks)

        # Calculate F start
        f_max = global_specification.cpu_specification.clock_available_frequencies[-1]
        phi_min = global_specification.cpu_specification.clock_available_frequencies[0]
        phi_start = max(phi_min,
                        sum(map(lambda task: task.c / task.t, global_specification.tasks_specification.tasks)) / (
                                m * f_max))

        f_start = next(
            (x for x in global_specification.cpu_specification.clock_available_frequencies if x >= phi_start), f_max)

        cc = list(map(lambda a: a.c / f_start, global_specification.tasks_specification.tasks))

        cpu_utilization = sum(map(lambda a: a[0] / a[1].t, zip(cc, global_specification.tasks_specification.tasks)))

        # Exit program if can schedule
        if cpu_utilization >= m:
            raise Exception("Error: Schedule is not feasible")

        # Tasks set
        tasks = [GlobalSchedulerTask(global_specification.tasks_specification.tasks[i], i) for i in
                 range(len(global_specification.tasks_specification.tasks))]

        # Add dummy task
        if cpu_utilization < m:
            h = global_specification.tasks_specification.h
            cc_dummy = (m - sum(map(lambda a: a.c / a.t,
                                    global_specification.tasks_specification.tasks))) * f_start * h
            tasks.append(GlobalSchedulerTask(Task(cc_dummy, h, 0), len(tasks)))

        # Number of steps in the simulation
        simulation_time_steps = int(round(
            global_specification.tasks_specification.h / global_specification.simulation_specification.dt))

        # Allocation of each task in each simulation step
        i_tau_disc = scipy.zeros((n * m, simulation_time_steps))

        # Time of each quantum
        time_step = simulation_time_steps * [0]

        # Accumulated execution time
        m_exec = scipy.ndarray((n * m, simulation_time_steps))

        # Accumulated execution time tcpn
        m_exec_tcpn = scipy.ndarray((n * m, simulation_time_steps))

        # Temperature of cores in each step
        temperature_disc = []

        # Map with temperatures in each step
        temperature_map = []

        # Time where each temperature step have been obtained
        time_temp = []

        # Accumulated execution time in each step
        m_exec_step = scipy.zeros(n * m)

        # Actual cores temperature in each step
        cores_temperature = scipy.asarray(
            m * [global_specification.environment_specification.t_env]) if is_thermal_simulation else None

        # Global model solver
        global_model_solver = GlobalModelSolver(global_model, global_specification)
        del global_model

        # Active tasks
        active_task_id = m * [-1]
        for zeta_q in range(simulation_time_steps):
            # Update progress
            if progress_bar is not None:
                progress_bar.update_progress(zeta_q / simulation_time_steps * 100)

            # Update time
            time = zeta_q * global_specification.simulation_specification.dt

            # Get active task in this step
            active_task_id = self.schedule_policy(time, tasks, m, active_task_id,
                                                  global_specification.cpu_specification.clock_relative_frequencies,
                                                  cores_temperature)

            for j in range(m):
                if active_task_id[j] != idle_task_id:
                    if round(tasks[active_task_id[j]].pending_c, 5) > 0:
                        # Not end yet
                        tasks[active_task_id[j]].pending_c -= global_specification.simulation_specification.dt * \
                                                              global_specification.cpu_specification.clock_relative_frequencies[
                                                                  j]
                        i_tau_disc[active_task_id[j] + j * n, zeta_q] = 1
                        m_exec_step[active_task_id[j] + j * n] += global_specification.simulation_specification.dt

                    else:
                        # Ended
                        tasks[active_task_id[j]].instances += 1

                        tasks[active_task_id[j]].pending_c = tasks[active_task_id[j]].c

                        tasks[active_task_id[j]].next_arrival += tasks[active_task_id[j]].t
                        tasks[active_task_id[j]].next_deadline += tasks[active_task_id[j]].t

            m_exec_disc, board_temperature, cores_temperature, results_times = global_model_solver.run_step(
                i_tau_disc[:, zeta_q].reshape(-1), time)
            m_exec_tcpn[:, zeta_q] = m_exec_disc

            m_exec[:, zeta_q] = m_exec_step

            time_step[zeta_q] = time

            temperature_disc.append(cores_temperature)

            temperature_map.append(board_temperature)

            time_temp.append(results_times)

        time_step = scipy.asarray(time_step).reshape((-1, 1))

        if len(temperature_map) > 0:
            temperature_map = scipy.concatenate(temperature_map, axis=1)

        if len(time_temp) > 0:
            time_temp = scipy.concatenate(time_temp)

        if len(temperature_disc) > 0:
            temperature_disc = scipy.concatenate(temperature_disc, axis=1)

        return SchedulerResult(temperature_map, temperature_disc, time_step, time_temp, m_exec, m_exec_tcpn,
                               i_tau_disc, global_specification.simulation_specification.dt)

    def ilpp_dp(self, scheduler_tasks: List[GlobalSchedulerTask], f_start: float, hyperperiod: float, n: int,
                m: int) -> [scipy.ndarray, scipy.ndarray, scipy.ndarray]:
        utilization = sum(map(lambda a: a.c / (a.t * f_start), scheduler_tasks))

        jobs = list(map(lambda a: hyperperiod / a.t, scheduler_tasks))
        t_star = list(map(lambda a: (a.t - a.c) * f_start, scheduler_tasks))

        d = scipy.zeros((n, max(jobs)))

        for i in range(n):
            d[i, :jobs[i]] = scipy.arange(scheduler_tasks[i].t * f_start, hyperperiod * f_start,
                                          scheduler_tasks[i].t * f_start)
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
        aeq_1 = scipy.zeros((number_of_interval - 1, v))
        beq_1 = scipy.zeros((number_of_interval - 1, 1))
        c = 0
        for j in range(1, number_of_interval - 1):
            for i in range(n):
                aeq_1[j, i + c] = 1
            c = c + n
            beq_1[j] = m * isd[j]

        aeq_2 = scipy.zeros((v, v))
        a_1 = scipy.zeros((v, v))
        beq_2 = scipy.zeros((v, 1))
        b_1 = scipy.zeros((v, 1))

        # Temporal
        f1 = 1
        f2 = 1
        for j in range(number_of_interval - 1):
            for i in range(n):
                i_k = 0
                for k in range(j):
                    q = math.floor(sd[j + 1] / (scheduler_tasks[i].t * f_start))
                    r = sd[j + 1] % (scheduler_tasks[i].t * f_start)
                    if r == 0:
                        aeq_2[f1, (k - 1) * n + i] = 1
                    else:
                        a_1[f2, (k - 1) * n + i] = -1
                    i_k = i_k + isd[k]

                if r == 0:
                    beq_2[f1, 1] = q * scheduler_tasks[i].c * f_start
                    f1 = f1 + 1
                else:
                    b_1[f2, 1] = -1 * (q * scheduler_tasks[i].c * f_start - q * scheduler_tasks[i].t * f_start +
                                       max(0, i_k - t_star[i]))
                    f2 = f2 + 1

        # TODO: Seguir desde aqui


@abc.abstractmethod
def schedule_policy(self, time: float, tasks: List[GlobalSchedulerTask], m: int, active_tasks: List[int],
                    cores_frequency: Optional[List[float]], cores_temperature: Optional[scipy.ndarray]) -> \
        List[int]:
    """
    Method to implement with the actual scheduler police
    :param cores_frequency: Frequencies of cores
    :param time: actual simulation time passed
    :param tasks: tasks
    :param m: number of cores
    :param active_tasks: actual id of tasks assigned to cores (task with id -1 is the idle task)
    :param cores_temperature: temperature of each core
    :return: tasks to assign to cores in next step (task with id -1 is the idle task)
    """
    pass
