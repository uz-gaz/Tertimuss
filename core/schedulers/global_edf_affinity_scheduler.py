import scipy

from core.kernel_generator.kernel import SimulationKernel
from core.problem_specification_models.GlobalSpecification import GlobalSpecification
from core.problem_specification_models.TasksSpecification import Task
from core.schedulers.abstract_scheduler import AbstractScheduler, SchedulerResult
from core.schedulers.global_model_solver import solve_global_model


class GlobalEDFAffinityScheduler(AbstractScheduler):
    class EDFTask(Task):
        def __init__(self, task_specification: Task, task_id: int):
            super().__init__(task_specification.c, task_specification.t, task_specification.e)
            self.next_deadline = task_specification.t
            self.next_arrival = 0
            self.pending_c = task_specification.c
            self.instances = 0
            self.id = task_id

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
        tasks = [self.EDFTask(global_specification.tasks_specification.tasks[i], i) for i in
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
        temperature_disc = scipy.ndarray((len(simulation_kernel.global_model.s) - 2 * n * m, 0))

        # Map with temperatures in each step
        temperature_map = scipy.zeros((len(simulation_kernel.mo), 0))

        # Time where each temperature step have been obtained
        time_temp = scipy.ndarray((0, 1))

        # Initial marking
        mo = simulation_kernel.mo

        # Accumulated execution time in each step
        m_exec_step = scipy.zeros(n * m)

        # Active tasks
        active_task_id = m * [-1]
        for zeta_q in range(simulation_time_steps):
            # Update time
            time = zeta_q * global_specification.simulation_specification.dt

            # Get active task in this step
            active_task_id = edf_with_affinity_police(time, tasks, m, active_task_id)

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
                scipy.asarray([time,
                               time + global_specification.simulation_specification.dt]))

            mo = mo_next
            temperature_map = scipy.concatenate((temperature_map, temperature_tcpn), axis=1)
            time_temp = scipy.concatenate((time_temp, tout_disc))

            temperature_disc = scipy.concatenate((temperature_disc, temp_time_disc), axis=1)

            m_exec[:, zeta_q] = m_exec_step
            m_exec_tcpn[:, zeta_q] = m_exec_disc.reshape(-1)

            time_step[zeta_q] = time

        time_step = scipy.asarray(time_step).reshape((-1, 1))
        return SchedulerResult(temperature_map, mo, time_step, i_tau_disc, m_exec, m_exec_tcpn, time_step, time_temp,
                               scipy.asarray([]), temperature_disc, global_specification.simulation_specification.dt)


def edf_with_affinity_police(time: float, tasks: list, m: int, active_tasks: list) -> list:
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
