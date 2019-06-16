import scipy

from core.kernel_generator.global_model import GlobalModel
from core.problem_specification_models.GlobalSpecification import GlobalSpecification
from core.problem_specification_models.TasksSpecification import Task
from core.schedulers.abstract_scheduler import AbstractScheduler, SchedulerResult
from core.schedulers.utils.global_model_solver import solve_global_model
from typing import List, Optional

from output_generation.abstract_progress_bar import AbstractProgressBar


class GlobalSchedulerTask(Task):
    def __init__(self, task_specification: Task, task_id: int):
        super().__init__(task_specification.c, task_specification.t, task_specification.e)
        self.next_deadline = task_specification.t
        self.next_arrival = 0
        self.pending_c = task_specification.c
        self.instances = 0
        self.id = task_id


class AbstractGlobalScheduler(AbstractScheduler):
    """
    Abstract implementation of global scheduler (Custom Scheduler in original work).
    Method schedule_police must be implemented
    """

    def __init__(self) -> None:
        super().__init__()

    def simulate(self, global_specification: GlobalSpecification,
                 global_model: GlobalModel, progress_bar: Optional[AbstractProgressBar]) -> SchedulerResult:

        # True if simulation must save temperature
        is_thermal_simulation = False

        idle_task_id = -1
        m = global_specification.cpu_specification.number_of_cores
        n = len(global_specification.tasks_specification.tasks)
        cpu_utilization = sum(map(lambda a: a.c / a.t, global_specification.tasks_specification.tasks))

        # Exit program if can schedule
        if cpu_utilization >= m:
            raise Exception("Error: Schedule is not feasible")

        # Tasks set
        tasks = [GlobalSchedulerTask(global_specification.tasks_specification.tasks[i], i) for i in
                 range(len(global_specification.tasks_specification.tasks))]

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

        # Initial marking
        # mo = global_model

        # Accumulated execution time in each step
        m_exec_step = scipy.zeros(n * m)

        # Actual cores temperature in each step
        cores_temperature = scipy.asarray(
            m * [global_specification.environment_specification.t_env]) if is_thermal_simulation else None

        # TODO: REMOVE, only for debug
        mo_debug_history = scipy.zeros((len(global_model.m), simulation_time_steps))

        # Active tasks
        active_task_id = m * [-1]
        for zeta_q in range(simulation_time_steps):
            print(zeta_q, simulation_time_steps)
            # TODO: REMOVE, only for debug
            mo_debug_history[:, zeta_q] = global_model.m[:, 0]

            # Update time
            time = zeta_q * global_specification.simulation_specification.dt

            # Get active task in this step
            active_task_id = self.schedule_policy(time, tasks, m, active_task_id, cores_temperature)

            for j in range(m):
                if active_task_id[j] != idle_task_id:
                    if round(tasks[active_task_id[j]].pending_c, 5) > 0:
                        # Not end yet
                        tasks[active_task_id[j]].pending_c -= global_specification.simulation_specification.dt
                        i_tau_disc[active_task_id[j] + j * n, zeta_q] = 1
                        m_exec_step[active_task_id[j] + j * n] += global_specification.simulation_specification.dt

                    else:
                        # Ended
                        tasks[active_task_id[j]].instances += 1

                        tasks[active_task_id[j]].pending_c = tasks[active_task_id[j]].c

                        tasks[active_task_id[j]].next_arrival += tasks[active_task_id[j]].t
                        tasks[active_task_id[j]].next_deadline += tasks[active_task_id[j]].t

            if is_thermal_simulation:
                mo_next, m_exec_disc, _, _, tout_disc, temp_time_disc, temperature_tcpn = solve_global_model(
                    global_model,
                    global_model.m.reshape(-1),
                    i_tau_disc[:, zeta_q].reshape(-1),
                    global_specification.environment_specification.t_env,
                    global_specification.simulation_specification.dt)

                global_model.m = mo_next

                temperature_map.append(temperature_tcpn)

                time_temp.append(tout_disc)

                temperature_disc.append(temp_time_disc)

                cores_temperature = scipy.transpose(temp_time_disc)[-1] if temp_time_disc.shape[
                                                                               1] > 0 else cores_temperature

                m_exec_tcpn[:, zeta_q] = m_exec_disc.reshape(-1)

            else:
                mo_next, m_exec_disc, _, _, _, _, _ = solve_global_model(
                    global_model,
                    global_model.m.reshape(-1),
                    i_tau_disc[:, zeta_q].reshape(-1),
                    45,
                    global_specification.simulation_specification.dt)

                m_exec_tcpn[:, zeta_q] = m_exec_disc.reshape(-1)
                global_model.m = mo_next

            m_exec[:, zeta_q] = m_exec_step

            time_step[zeta_q] = time

        time_step = scipy.asarray(time_step).reshape((-1, 1))

        if len(temperature_map) > 0:
            temperature_map = scipy.concatenate(temperature_map, axis=1)

        if len(time_temp) > 0:
            time_temp = scipy.concatenate(time_temp)

        if len(temperature_disc) > 0:
            temperature_disc = scipy.concatenate(temperature_disc, axis=1)

        return SchedulerResult(temperature_map, global_model.m, time_step, i_tau_disc, m_exec, m_exec_tcpn, time_step,
                               time_temp,
                               scipy.asarray([]), temperature_disc, global_specification.simulation_specification.dt)

    def schedule_policy(self, time: float, tasks: List[GlobalSchedulerTask], m: int, active_tasks: List[int],
                        cores_temperature: Optional[scipy.ndarray]) -> List[int]:
        """
        Method to implement with the actual scheduler police
        :param time: actual simulation time passed
        :param tasks: tasks
        :param m: number of cores
        :param active_tasks: actual id of tasks assigned to cores (task with id -1 is the idle task)
        :param cores_temperature: temperature of each core
        :return: tasks to assign to cores in next step (task with id -1 is the idle task)
        """

        alive_tasks = [x for x in tasks if x.next_arrival <= time]
        task_order = scipy.argsort(list(map(lambda x: x.next_deadline, alive_tasks)))
        tasks_to_execute = ([alive_tasks[i].id for i in task_order] + (m - len(alive_tasks)) * [-1])[0:m]

        # Do affinity
        for i in range(m):
            actual = active_tasks[i]
            for j in range(m):
                if tasks_to_execute[j] == actual:
                    tasks_to_execute[j], tasks_to_execute[i] = tasks_to_execute[i], tasks_to_execute[j]
        return tasks_to_execute
