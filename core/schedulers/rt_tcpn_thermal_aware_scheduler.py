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

        jBi, jFSCi, quantum, mT = solve_lineal_programing_problem_for_scheduling(
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

        walloc = scipy.zeros(n * m)
        i_tau_disc = scipy.zeros((n * m, simulation_time_steps))
        e_iFSCj = scipy.zeros(n * m)
        x1 = scipy.zeros(n * m)
        x2 = scipy.zeros(n * m)
        s = scipy.zeros(n * m)
        iREj = scipy.zeros(n * m)
        iPRj = scipy.zeros((m, n))

        zeta = 0
        time = 0

        sd = sd_u[kd]

        m_exec = scipy.zeros(len(jFSCi))
        m_busy = scipy.zeros(len(jFSCi))
        Mexec = scipy.zeros(len(jFSCi))
        TIMEZ = scipy.ndarray((0, 1))
        TIMEstep = scipy.asarray([])
        TIME_Temp = scipy.ndarray((0, 1))
        TEMPERATURE_CONT = scipy.ndarray((len(simulation_kernel.global_model.s) - 2 * len(walloc), 0))
        TEMPERATURE_DISC = scipy.ndarray((len(simulation_kernel.global_model.s) - 2 * len(walloc), 0))
        MEXEC = scipy.ndarray((n * m, 0))
        MEXEC_TCPN = scipy.ndarray((n * m, 0))
        moDisc = simulation_kernel.mo
        M = scipy.zeros((len(simulation_kernel.mo), 0))
        mo = simulation_kernel.mo

        for zeta_q in range(simulation_time_steps):
            while round(time) <= zeta + quantum:
                for j in range(m):
                    for i in range(n):
                        # Calculo del error, y la superficie para el sliding mode control
                        e_iFSCj[i + j * n] = jFSCi[i + j * n] * zeta - m_exec[i + j * n]

                        # Cambio de variables
                        x1[i + j * n] = e_iFSCj[i + j * n]
                        x2[i + j * n] = m_busy[i + j * n]  # m_bussy

                        # Superficie
                        s[i + j * n] = x1[i + j * n] - x2[i + j * n] + jFSCi[i + j * n]

                        # Control Para tareas temporal en cada procesador w_alloc control en I_tau
                        walloc[i + j * n] = (jFSCi[i + j * n] * scipy.sign(s[i + j * n]) + jFSCi[i + j * n]) / 2

                mo_next, m_exec, m_busy, Temp, tout, TempTime, m_TCPN_cont = solve_global_model(
                    simulation_kernel.global_model,
                    mo.reshape(-1),
                    walloc,
                    global_specification.environment_specification.t_env,
                    [time, time + step])

                mo = mo_next
                TEMPERATURE_CONT = scipy.concatenate((TEMPERATURE_CONT, Temp), axis=1)
                TIMEstep = scipy.concatenate((TIMEstep, scipy.asarray([time])))
                MEXEC_TCPN = scipy.concatenate((MEXEC_TCPN, m_exec), axis=1)
                time = time + step

            # DISCRETIZATION
            # Todas las tareas se expulsan de los procesadores
            i_tau_disc[:, zeta_q] = 0

            # Se inicializa el conjunto ET de transiciones de tareas para el modelo discreto
            ET = scipy.zeros((m, n), dtype=int)

            FSC = scipy.zeros(m * n)

            # Se calcula el remaining jobs execution Re_tau(j,i)
            for j in range(m):
                for i in range(n):
                    FSC[i + j * n] = jFSCi[i + j * n] * sd
                    iREj[i + j * n] = m_exec[i + j * n] - Mexec[i + j * n]

                    if round(iREj[i + j * n], 4) > 0:
                        ET[j, i] = i + 1

            for j in range(m):
                # Si el conjunto no es vacio por cada j-esimo CPU, entonces se procede a
                # calcular la prioridad de cada tarea a ser asignada
                if scipy.count_nonzero(ET[j]) > 0:
                    # Prioridad es igual al marcado del lugar continuo menos el marcado del lugar discreto
                    iPRj[j, :] = jFSCi[j * n: j * n + n] * sd - Mexec[j * n:j * n + n]

                    # Se ordenan de manera descendente por orden de prioridad,
                    # IndMaxPr contiene los indices de las tareas ordenado de mayor a
                    # menor prioridad
                    IndMaxPr = scipy.flip(scipy.argsort(iPRj[j, :]))

                    # Si en el vector ET(j,k) existe un cero entonces significa que en
                    # la posicion k la tarea no tine a Re_tau(j,k)>0 (es decir la tarea ya ejecuto lo que debía)
                    # entonces hay que incrementar a la siguiente posicion k+1 para tomar a la tarea de
                    # mayor prioridad
                    k = 0
                    while ET[j, IndMaxPr[k]] == 0:
                        k = k + 1

                    # Se toma la tarea de mayor prioridad en el conjunto ET
                    IndMaxPr = ET[j, IndMaxPr[k]] - 1

                    # si se asigna la procesador j la tarea de mayor prioridad IndMaxPr(1), entonces si en el
                    # conjunto ET para los procesadores restantes debe pasar que ET(k,IndMaxPr(1))=0,
                    # para evitar que las tareas se ejecuten de manera paralela
                    for k in range(m):
                        if j != k:
                            ET[k, IndMaxPr] = 0

                    i_tau_disc[IndMaxPr + j * n, zeta_q] = 1

                    Mexec[IndMaxPr + j * n] += quantum

            MEXEC = scipy.concatenate((MEXEC, Mexec.reshape(-1, 1)), axis=1)
            mo_nextDisc, m_execDisc, m_busyDisc, TempDisc, toutDisc, TempTimeDisc, m_TCPN = solve_global_model(
                simulation_kernel.global_model, moDisc.reshape(len(moDisc)), i_tau_disc[:, zeta_q],
                global_specification.environment_specification.t_env, [zeta, zeta + quantum])

            moDisc = mo_nextDisc
            M = scipy.concatenate((M, m_TCPN), axis=1)

            TEMPERATURE_DISC = scipy.concatenate((TEMPERATURE_DISC, TempTimeDisc), axis=1)
            TIME_Temp = scipy.concatenate((TIME_Temp, toutDisc))
            TIMEZ = scipy.concatenate((TIMEZ, scipy.asarray([zeta]).reshape((1, 1))))

            if scipy.array_equal(round(zeta, 3), sd):
                kd = kd + 1
                if kd + 1 <= len(sd_u):
                    sd = sd_u[kd]

            zeta = zeta + quantum

        SCH_OLDTFS = i_tau_disc

        return SchedulerResult(M, mo, TIMEZ, SCH_OLDTFS, MEXEC, MEXEC_TCPN, TIMEstep.reshape(
            (-1, 1)), TIME_Temp, TEMPERATURE_CONT, TEMPERATURE_DISC, quantum)
