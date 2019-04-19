import scipy

from core.kernel_generator.kernel import SimulationKernel
from core.problem_specification_models.GlobalSpecification import GlobalSpecification
from core.problem_specification_models.TasksSpecification import Task
from core.schedulers.abstract_scheduler import AbstractScheduler, SchedulerResult
from core.schedulers.global_model_solver import solve_global_model


class GlobalEDFScheduler(AbstractScheduler):
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

        # Active task in each core
        # active_task_id = m * [idle_task_id]

        simulation_time_steps = int(round(
            global_specification.tasks_specification.h / global_specification.simulation_specification.dt))

        # Allocation of each task in each simulation step
        i_tau_disc = scipy.zeros((n * m, simulation_time_steps))

        # Accumulated execution time in each step
        m_exec = scipy.zeros(n * m)

        TIMEZ = scipy.ndarray((0, 1))
        TIMEstep = scipy.asarray([])
        TIME_Temp = scipy.ndarray((0, 1))
        TEMPERATURE_DISC = scipy.ndarray((len(simulation_kernel.global_model.s) - 2 * n * m, 0))
        MEXEC = scipy.ndarray((n * m, 0))
        MEXEC_TCPN = scipy.ndarray((n * m, 0))
        M = scipy.zeros((len(simulation_kernel.mo), 0))

        mo = simulation_kernel.mo

        for zeta_q in range(simulation_time_steps):
            time = zeta_q * global_specification.simulation_specification.dt

            # Get active task in this step
            active_task_id = edf_police(time, tasks, m)

            for j in range(m):
                if active_task_id[j] != idle_task_id:
                    if round(tasks[active_task_id[j]].pending_c, 5) > 0:
                        # Not end yet
                        tasks[active_task_id[j]].pending_c -= global_specification.simulation_specification.dt
                        i_tau_disc[active_task_id[j] + j * n, zeta_q] = 1
                        m_exec[active_task_id[j] + j * n] += global_specification.simulation_specification.dt

                    else:
                        # Ended
                        tasks[active_task_id[j]].instances += 1

                        tasks[active_task_id[j]].pending_c = tasks[active_task_id[j]].c

                        tasks[active_task_id[j]].next_arrival += tasks[active_task_id[j]].t
                        tasks[active_task_id[j]].next_deadline += tasks[active_task_id[j]].t

            # TODO: Revisar de aqui para abajo
            mo_next, m_exec_disc, _, _, toutDisc, TempTimeDisc, m_TCPN = solve_global_model(
                simulation_kernel.global_model,
                mo.reshape(-1),
                i_tau_disc[:, zeta_q].reshape(-1),
                global_specification.environment_specification.t_env,
                scipy.asarray([time,
                               time + global_specification.simulation_specification.dt]))

            mo = mo_next
            M = scipy.concatenate((M, m_TCPN), axis=1)
            TIMEstep = scipy.concatenate((TIMEstep, scipy.asarray([time])))
            TEMPERATURE_DISC = scipy.concatenate((TEMPERATURE_DISC, TempTimeDisc), axis=1)
            TIME_Temp = scipy.concatenate((TIME_Temp, toutDisc))

            MEXEC = scipy.concatenate((MEXEC, m_exec.reshape(-1, 1)), axis=1)
            MEXEC_TCPN = scipy.concatenate((MEXEC_TCPN, m_exec_disc), axis=1)

            TIMEZ = scipy.concatenate((TIMEZ, scipy.asarray([time]).reshape((1, 1))))

        return SchedulerResult(M, mo, TIMEZ, i_tau_disc, MEXEC, MEXEC_TCPN, TIMEstep.reshape(
            (-1, 1)), TIME_Temp, scipy.asarray([]), TEMPERATURE_DISC)


def edf_police(time: float, tasks: list, m: int) -> list:
    alive_tasks = [x for x in tasks if x.next_arrival <= time]
    task_order = scipy.argsort(list(map(lambda x: x.next_deadline, alive_tasks)))
    return ([alive_tasks[i].id for i in task_order] + (m - len(alive_tasks)) * [-1])[0:m]
