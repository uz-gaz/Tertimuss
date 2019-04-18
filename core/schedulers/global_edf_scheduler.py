import scipy

from core.kernel_generator.kernel import SimulationKernel
from core.problem_specification_models.GlobalSpecification import GlobalSpecification
from core.schedulers.abstract_scheduler import AbstractScheduler, SchedulerResult
from core.schedulers.global_model_solver import solve_global_model


class GlobalEDFScheduler(AbstractScheduler):

    def __init__(self) -> None:
        super().__init__()

    def simulate(self, global_specification: GlobalSpecification,
                 simulation_kernel: SimulationKernel) -> SchedulerResult:

        idle_task_id = 1023
        m = global_specification.cpu_specification.number_of_cores
        n = len(global_specification.tasks_specification.tasks)
        cpu_utilization = 1 / (m * sum(map(lambda a: a.c / a.t, global_specification.tasks_specification.tasks)))
        if cpu_utilization >= m:
            print("Schedule is not feasible")
            # TODO: Return error or throw exception
            return None

        cc = list(map(lambda a: a.c, global_specification.tasks_specification.tasks))
        abs_arrival = n * [0]
        tasks_instances = n * [0]
        tasks_alive = n * [0]
        abs_deadline = list(map(lambda a: a.t, global_specification.tasks_specification.tasks))

        active_task_id = idle_task_id * scipy.ones((m, 1))

        simulation_time_steps = int(round(
            global_specification.tasks_specification.h / global_specification.simulation_specification.dt))

        i_tau_disc = scipy.zeros((n * m, simulation_time_steps))

        m_exec = scipy.zeros((n * m, 1))

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

            for j in range(m):
                res, tasks_alive = sp_interrupt(time, n, abs_arrival, tasks_alive)
                if res:
                    active_task_id = edf_police(n, m, abs_deadline, tasks_alive)

                if active_task_id[j] != idle_task_id:
                    if round(cc[active_task_id[j]],
                             5) != 0:  # FIXME: Probably errors with float precision because always go into
                        cc[active_task_id[j]] -= global_specification.simulation_specification.dt
                        i_tau_disc[active_task_id[j] + j * n, zeta_q] = 1

                        m_exec[active_task_id[j] + j * n] += global_specification.simulation_specification.dt
                    else:
                        cc[active_task_id[j]] = 0

                    if cc[active_task_id[j]] <= 0:
                        i_tau_disc[active_task_id[j] + j * n, zeta_q] = 0
                        tasks_instances[active_task_id[j]] += 1
                        tasks_alive[active_task_id[j]] = 0

                        cc[active_task_id[j]] = global_specification.tasks_specification.tasks[
                            active_task_id[j]].c

                        abs_arrival[active_task_id[j]] += tasks_instances[active_task_id[j]] * \
                                                          global_specification.tasks_specification.tasks[
                                                              active_task_id[j]].t

                        abs_deadline[active_task_id[j]] = global_specification.tasks_specification.tasks[
                                                              active_task_id[j]].t + abs_arrival[
                                                              active_task_id[j]]
                        active_task_id = edf_police(n, m, abs_deadline, tasks_alive)
                else:
                    i_tau_disc[j, zeta_q] = 1

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


def sp_interrupt(time: float, n: int, abs_arrival: list, tasks_alive: list) -> [bool, list]:
    a = 0
    n1 = 0
    for i in range(n):
        if round(time, 5) == round(abs_arrival[i], 5):
            tasks_alive[i] = 1
            a = a + 1
        elif tasks_alive[i] == 0:
            n1 += 1

    return n1 == n or a != 0, tasks_alive


def edf_police(n: int, m: int, abs_deadline: list, tasks_alive: list) -> list:
    id_task = m * [1023]

    id_task_order = scipy.argsort(abs_deadline)

    for j in range(m):
        min_value = 32767
        for i in range(n):
            if min_value > abs_deadline[id_task_order[j]] and tasks_alive[id_task_order[j]] == 1:
                min_value = abs_deadline[id_task_order[j]]
                id_task[j] = id_task_order[j]
    return id_task
