import abc

import scipy

from core.kernel_generator.kernel import SimulationKernel
from core.problem_specification_models.GlobalSpecification import GlobalSpecification
from core.problem_specification_models.TasksSpecification import Task
from core.schedulers.abstract_scheduler import AbstractScheduler, SchedulerResult
from core.schedulers.global_model_solver import solve_global_model
from typing import List


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
                 simulation_kernel: SimulationKernel) -> SchedulerResult:

        idle_task_id = -1
        m = global_specification.cpu_specification.number_of_cores
        n = len(global_specification.tasks_specification.tasks)
        cpu_utilization = sum(map(lambda a: a.c / a.t, global_specification.tasks_specification.tasks))
        if cpu_utilization >= m:
            print("Schedule is not feasible")
            # TODO: Return error or throw exception
            return None

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
        temperature_disc = scipy.ndarray((m, 0))

        # Map with temperatures in each step
        temperature_map = scipy.zeros((len(simulation_kernel.mo), 0))

        # Time where each temperature step have been obtained
        time_temp = scipy.ndarray((0, 1))

        # Initial marking
        mo = simulation_kernel.mo

        # Accumulated execution time in each step
        m_exec_step = scipy.zeros(n * m)

        # Actual cores temperature in each step
        cores_temperature = scipy.asarray(m * [global_specification.environment_specification.t_env])

        # Active tasks
        active_task_id = m * [-1]
        for zeta_q in range(simulation_time_steps):
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
            mo_next, m_exec_disc, _, _, tout_disc, temp_time_disc, temperature_tcpn = solve_global_model(
                simulation_kernel.global_model,
                mo.reshape(-1),
                i_tau_disc[:, zeta_q].reshape(-1),
                global_specification.environment_specification.t_env,
                [time, time + global_specification.simulation_specification.dt])

            mo = mo_next
            temperature_map = scipy.concatenate((temperature_map, temperature_tcpn), axis=1)
            time_temp = scipy.concatenate((time_temp, tout_disc))

            temperature_disc = scipy.concatenate((temperature_disc, temp_time_disc), axis=1)

            m_exec[:, zeta_q] = m_exec_step
            m_exec_tcpn[:, zeta_q] = m_exec_disc.reshape(-1)

            time_step[zeta_q] = time

            cores_temperature = scipy.transpose(temp_time_disc)[-1] if temp_time_disc.shape[
                                                                           1] > 0 else cores_temperature

        time_step = scipy.asarray(time_step).reshape((-1, 1))
        return SchedulerResult(temperature_map, mo, time_step, i_tau_disc, m_exec, m_exec_tcpn, time_step, time_temp,
                               scipy.asarray([]), temperature_disc, global_specification.simulation_specification.dt)

    @abc.abstractmethod
    def schedule_policy(self, time: float, tasks: List[GlobalSchedulerTask], m: int, active_tasks: List[int],
                        cores_temperature: scipy.ndarray) -> List[int]:
        """
        Method to implement with the actual scheduler police
        :param time: actual simulation time passed
        :param tasks: tasks
        :param m: number of cores
        :param active_tasks: actual id of tasks assigned to cores (task with id -1 is the idle task)
        :param cores_temperature: temperature of each core
        :return: tasks to assign to cores in next step (task with id -1 is the idle task)
        """
        pass
