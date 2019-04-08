import scipy

from core.kernel_generator.kernel import SimulationKernel
from core.problem_specification_models.GlobalSpecification import GlobalSpecification
from core.schedulers.abstract_scheduler import AbstractScheduler
from core.schedulers.lineal_programing_problem_for_scheduling import solve_lineal_programing_problem_for_scheduling


class GlobalEDFScheduler(AbstractScheduler):

    def __init__(self) -> None:
        super().__init__()

    def simulate(self, global_specification: GlobalSpecification, simulation_kernel: SimulationKernel):
        idle_task_id = 1023
        all = 1
        current = 0
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
        tasks_alives = n * [0]
        abs_deadline = list(map(lambda a: a.t, global_specification.tasks_specification.tasks))

        active_task_id = idle_task_id * scipy.ones((m, 1))

        i_tau_disc = scipy.zeros((n * m, int(
            global_specification.tasks_specification.h / global_specification.simulation_specification.step)))

        time = 0

        m_exec = scipy.zeros((n * m, 1))

        TIMEZ = scipy.ndarray((0, 1))
        TIMEstep = scipy.asarray([])
        TIME_Temp = scipy.ndarray((0, 1))
        TEMPERATURE_DISC = scipy.ndarray((len(simulation_kernel.global_model.s) - 2 * len(walloc), 0))
        MEXEC = scipy.ndarray((len(jFSCi), 0))
        MEXEC_TCPN = scipy.ndarray((len(walloc), 0))
        M = scipy.zeros((len(simulation_kernel.mo), 0))

        zeta_q = 1

        while time <= global_specification.tasks_specification.h:
            for j in range(m):
                if sp_interrupt(time, n, m):
                    active_task_id = EDF_police(n, m)

                if active_task_id[j, 0] != idle_task_id:
                    if cc[active_task_id[j, 0]] != 0:  # FIXME: Probably errors with float precision
                        cc[active_task_id[j, 0]] -= global_specification.simulation_specification.step
                        i_tau_disc[active_task_id[j, 0] + j * n, zeta_q] = 1

                        m_exec[active_task_id[j, 0] + j * n] += global_specification.simulation_specification.step

                    if cc[active_task_id[j, 0]] <= 0:
                        i_tau_disc[active_task_id[j, 0] + j * n, zeta_q] = 0
                        tasks_instances[active_task_id[j, 0]] += 1
                        tasks_alives[active_task_id[j, 0]] = 0
                        # TODO: copy_execution_time(active_task_id(j,1),CURRENT);
                        # TODO: update_abs_arrival(active_task_id(j,1), task(active_task_id(j,1)).instance,CURRENT);
                        # TODO: update_abs_deadline(active_task_id(j,1),CURRENT);
                        active_task_id = EDF_police(n, m)
                else:
                    i_tau_disc[j, zeta_q] = 1
            # TODO: [mo_next, m_exec, ~, ~, toutDisc, TempTimeDisc, m_TCPN]=SolGlobalModel(TCPNmodel,mo, I_tauDisc(:,ZetaQ), m_amb, [time time+step]);

            """
                mo=mo_next;
                M=[M  m_TCPN];
                TIMEstep=[TIMEstep;time];
                TEMPERATURE_DISC=[TEMPERATURE_DISC TempTimeDisc];
                TIME_Temp=[TIME_Temp; toutDisc];
                MEXEC=[MEXEC Mexec];
                MEXEC_TCPN=[MEXEC_TCPN m_exec];
                TIMEZ=[TIMEZ;time];
                time=time+step;
                
                ZetaQ=ZetaQ+1;
            """


def sp_interrupt(time: float, n: int, m: int) -> bool:
    # TODO
    return True


def EDF_police(n: int, m: int) -> int:
    # TODO
    pass
