import scipy

from core.kernel_generator.kernel import SimulationKernel
from core.problem_specification_models.GlobalSpecification import GlobalSpecification
from core.schedulers.abstract_scheduler import AbstractScheduler, SchedulerResult
from core.schedulers.global_model_solver import solve_global_model
from core.schedulers.lineal_programing_problem_for_scheduling import solve_lineal_programing_problem_for_scheduling


class RTTcpnThermalAwareScheduler(AbstractScheduler):

    def __init__(self) -> None:
        super().__init__()

    def simulate(self, global_specification: GlobalSpecification,
                 simulation_kernel: SimulationKernel) -> SchedulerResult:

        j_b_i, j_fsc_i, quantum, m_t = solve_lineal_programing_problem_for_scheduling(
            global_specification.tasks_specification, global_specification.cpu_specification,
            global_specification.environment_specification,
            global_specification.simulation_specification,
            simulation_kernel.thermal_model)
        n = len(global_specification.tasks_specification.tasks)
        m = global_specification.cpu_specification.number_of_cores
        step = global_specification.simulation_specification.dt

        ti = [i.t for i in global_specification.tasks_specification.tasks]

        jobs = [int(i) for i in global_specification.tasks_specification.h / ti]

        diagonal = scipy.zeros((n, scipy.amax(jobs)))

        # Number of steps in the simulation
        simulation_time_steps = int(round(global_specification.tasks_specification.h / quantum))

        kd = 1
        sd_u = []
        for i in range(n):
            diagonal[i, 0: jobs[i]] = list(range(ti[i], global_specification.tasks_specification.h + 1, ti[i]))
            sd_u = scipy.union1d(sd_u, diagonal[i, 0: jobs[i]])

        sd_u = scipy.union1d(sd_u, [0])

        w_alloc = scipy.zeros(n * m)
        i_tau_disc = scipy.zeros((n * m, simulation_time_steps))
        e_i_fsc_j = scipy.zeros(n * m)
        x1 = scipy.zeros(n * m)
        x2 = scipy.zeros(n * m)
        s = scipy.zeros(n * m)
        i_re_j = scipy.zeros(n * m)
        i_pr_j = scipy.zeros((m, n))

        zeta = 0
        time = 0

        sd = sd_u[kd]

        m_exec_step = scipy.zeros(len(j_fsc_i))
        m_busy = scipy.zeros(len(j_fsc_i))
        m_exec_accumulated = scipy.zeros(len(j_fsc_i))
        time_z = scipy.ndarray((0, 1))
        time_step = scipy.asarray([])
        time_temp = scipy.ndarray((0, 1))
        temperature_cont = scipy.ndarray((len(simulation_kernel.global_model.s) - 2 * len(w_alloc), 0))
        temperature_disc = scipy.ndarray((len(simulation_kernel.global_model.s) - 2 * len(w_alloc), 0))
        m_exec_history = scipy.ndarray((n * m, 0))
        m_exec_tcpn_history = scipy.ndarray((n * m, 0))
        mo_disc = simulation_kernel.mo
        temperature_map = scipy.zeros((len(simulation_kernel.mo), 0))
        mo = simulation_kernel.mo

        for zeta_q in range(simulation_time_steps):
            while round(time) <= zeta + quantum:
                for j in range(m):
                    for i in range(n):
                        # Calculo del error, y la superficie para el sliding mode control
                        e_i_fsc_j[i + j * n] = j_fsc_i[i + j * n] * zeta - m_exec_step[i + j * n]

                        # Cambio de variables
                        x1[i + j * n] = e_i_fsc_j[i + j * n]
                        x2[i + j * n] = m_busy[i + j * n]  # m_bussy

                        # Superficie
                        s[i + j * n] = x1[i + j * n] - x2[i + j * n] + j_fsc_i[i + j * n]

                        # Control Para tareas temporal en cada procesador w_alloc control en I_tau
                        w_alloc[i + j * n] = (j_fsc_i[i + j * n] * scipy.sign(s[i + j * n]) + j_fsc_i[i + j * n]) / 2

                mo_next, m_exec_step, m_busy, temp, tout, temp_time, m_tcpn_cont = solve_global_model(
                    simulation_kernel.global_model,
                    mo.reshape(-1),
                    w_alloc,
                    global_specification.environment_specification.t_env,
                    [time, time + step])

                mo = mo_next
                temperature_cont = scipy.concatenate((temperature_cont, temp), axis=1)
                time_step = scipy.concatenate((time_step, scipy.asarray([time])))
                m_exec_tcpn_history = scipy.concatenate((m_exec_tcpn_history, m_exec_step), axis=1)
                time = time + step

            # DISCRETIZATION
            # Todas las tareas se expulsan de los procesadores
            i_tau_disc[:, zeta_q] = 0

            # Se inicializa el conjunto ET de transiciones de tareas para el modelo discreto
            et = scipy.zeros((m, n), dtype=int)

            fsc = scipy.zeros(m * n)

            # Se calcula el remaining jobs execution Re_tau(j,i)
            for j in range(m):
                for i in range(n):
                    fsc[i + j * n] = j_fsc_i[i + j * n] * sd
                    i_re_j[i + j * n] = m_exec_step[i + j * n] - m_exec_accumulated[i + j * n]

                    if round(i_re_j[i + j * n], 4) > 0:
                        et[j, i] = i + 1

            for j in range(m):
                # Si el conjunto no es vacio por cada j-esimo CPU, entonces se procede a
                # calcular la prioridad de cada tarea a ser asignada
                if scipy.count_nonzero(et[j]) > 0:
                    # Prioridad es igual al marcado del lugar continuo menos el marcado del lugar discreto
                    i_pr_j[j, :] = j_fsc_i[j * n: j * n + n] * sd - m_exec_accumulated[j * n:j * n + n]

                    # Se ordenan de manera descendente por orden de prioridad,
                    # IndMaxPr contiene los indices de las tareas ordenado de mayor a
                    # menor prioridad
                    ind_max_pr = scipy.flip(scipy.argsort(i_pr_j[j, :]))

                    # Si en el vector ET(j,k) existe un cero entonces significa que en
                    # la posicion k la tarea no tine a Re_tau(j,k)>0 (es decir la tarea ya ejecuto lo que debía)
                    # entonces hay que incrementar a la siguiente posicion k+1 para tomar a la tarea de
                    # mayor prioridad
                    k = 0
                    while et[j, ind_max_pr[k]] == 0:
                        k = k + 1

                    # Se toma la tarea de mayor prioridad en el conjunto ET
                    ind_max_pr = et[j, ind_max_pr[k]] - 1

                    # si se asigna la procesador j la tarea de mayor prioridad IndMaxPr(1), entonces si en el
                    # conjunto ET para los procesadores restantes debe pasar que ET(k,IndMaxPr(1))=0,
                    # para evitar que las tareas se ejecuten de manera paralela
                    for k in range(m):
                        if j != k:
                            et[k, ind_max_pr] = 0

                    i_tau_disc[ind_max_pr + j * n, zeta_q] = 1

                    m_exec_accumulated[ind_max_pr + j * n] += quantum

            m_exec_history = scipy.concatenate((m_exec_history, m_exec_accumulated.reshape(-1, 1)), axis=1)
            mo_next_disc, m_exec_disc, m_busy_disc, temp_disc, tout_disc, temp_time_disc, m_tcpn = solve_global_model(
                simulation_kernel.global_model, mo_disc.reshape(len(mo_disc)), i_tau_disc[:, zeta_q],
                global_specification.environment_specification.t_env, [zeta, zeta + quantum])

            mo_disc = mo_next_disc
            temperature_map = scipy.concatenate((temperature_map, m_tcpn), axis=1)

            temperature_disc = scipy.concatenate((temperature_disc, temp_time_disc), axis=1)
            time_temp = scipy.concatenate((time_temp, tout_disc))
            time_z = scipy.concatenate((time_z, scipy.asarray([zeta]).reshape((1, 1))))

            if scipy.array_equal(round(zeta, 3), sd):
                kd = kd + 1
                if kd + 1 <= len(sd_u):
                    sd = sd_u[kd]

            zeta = zeta + quantum

        return SchedulerResult(temperature_map, mo, time_z, i_tau_disc, m_exec_history, m_exec_tcpn_history,
                               time_step.reshape(
                                   (-1, 1)), time_temp, temperature_cont, temperature_disc, quantum)
