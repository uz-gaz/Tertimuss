import numpy as np

from core.kernel_generator.global_model import GlobalModel
from core.kernel_generator.processor_model import ProcessorModel
from core.kernel_generator.tasks_model import TasksModel
from core.kernel_generator.thermal_model import ThermalModel
from core.problem_specification_models.CpuSpecification import CpuSpecification
from core.problem_specification_models.EnvironmentSpecification import EnvironmentSpecification
from core.problem_specification_models.SimulationSpecification import SimulationSpecification
from core.problem_specification_models.TasksSpecification import TasksSpecification
from core.schedulers.abstract_scheduler import AbstractScheduler
from core.schedulers.global_model_solver import solve_global_model
from core.schedulers.lineal_programing_problem_for_scheduling import solve_lineal_programing_problem_for_scheduling


class RTTcpnThermalAwareScheduler(AbstractScheduler):

    def __init__(self) -> None:
        super().__init__()

    def simulate(self, tasks_specification: TasksSpecification, cpu_specification: CpuSpecification,
                 environment_specification: EnvironmentSpecification, simulation_specification: SimulationSpecification,
                 global_model: GlobalModel, processor_model: ProcessorModel, tasks_model: TasksModel,
                 thermal_model: ThermalModel):
        jBi, jFSCi, quantum, mT = solve_lineal_programing_problem_for_scheduling(tasks_specification, cpu_specification,
                                                                                 environment_specification,
                                                                                 simulation_specification,
                                                                                 thermal_model)
        n = len(tasks_specification.tasks)
        m = cpu_specification.number_of_cores
        step = simulation_specification.dt

        ti = [i.t for i in tasks_specification.tasks]

        jobs = [int(i) for i in tasks_specification.h / ti]

        diagonal = np.zeros((n, np.max(jobs)))

        kd = 1
        sd_u = []
        for i in range(0, n):
            diagonal[i, 0: jobs[i]] = list(range(ti[i], tasks_specification.h + 1, ti[i]))
            sd_u = np.union1d(sd_u, diagonal[i, 0: jobs[i]])

        sd_u = np.union1d(sd_u, [0])

        walloc = np.zeros(len(jFSCi))

        i_tau_disc = np.zeros((len(jFSCi), int(tasks_specification.h / quantum)))
        e_iFSCj = np.zeros(len(walloc))
        x1 = np.zeros(len(e_iFSCj))  # ==np.zeros(walloc)
        x2 = np.zeros(len(e_iFSCj))
        s = np.zeros(len(e_iFSCj))
        iREj = np.zeros(len(walloc))
        iPRj = np.zeros((m, n))

        zeta = 0
        time = 0
        zeta_q = 0

        sd = sd_u[kd]

        m_exec = np.zeros(len(jFSCi))
        m_busy = np.zeros(len(jFSCi))
        Mexec = np.zeros(len(jFSCi))
        TIMEZ = []
        TIMEstep = []
        TIME_Temp = []
        TEMPERATURE_CONT = [] # np.asarray([])
        TEMPERATURE_DISC = []
        MEXEC = []
        MEXEC_TCPN = []
        moDisc = global_model.mo
        M = []
        mo = global_model.mo

        while round(zeta) <= tasks_specification.h:
            while round(time) <= zeta + quantum:
                for j in range(0, m):
                    for i in range(0, n):
                        # Calculo del error, y la superficie para el sliding mode control
                        e_iFSCj[i + j * n] = jFSCi[i + j * n] * zeta - m_exec[i + j * n]

                        # Cambio de variables
                        x1[i + j * n] = e_iFSCj[i + j * n]
                        x2[i + j * n] = m_busy[i + j * n]  # m_bussy

                        # Superficie
                        s[i + j * n] = x1[i + j * n] - x2[i + j * n] + jFSCi[i + j * n]

                        # Control Para tareas temporal en cada procesador w_alloc control en I_tau
                        walloc[i + j * n] = (jFSCi[i + j * n] * np.sign(s[i + j * n]) + jFSCi[i + j * n]) / 2

                mo_next, m_exec, m_busy, Temp, tout, TempTime, m_TCPN_cont = solve_global_model(global_model,
                                                                                                mo.reshape(len(mo)),
                                                                                                walloc,
                                                                                                environment_specification.t_env,
                                                                                                np.asarray([time,
                                                                                                            time + step]))  # FIXME: Array orientation

                mo = mo_next
                # TEMP_2 = Temp.reshape((-1, 1))
                # TEMPERATURE_CONT = np.concatenate((TEMPERATURE_CONT, TEMP_2), axis=0)  #
                TEMPERATURE_CONT = TEMPERATURE_CONT + [Temp]
                TIMEstep = TIMEstep + [time]
                MEXEC_TCPN = MEXEC_TCPN + [m_exec]
                time = time + step

            # DISCRETIZATION
            if zeta_q > 239:
                i = 111
                pass
            # Todas las tareas se expulsan de los procesadores
            i_tau_disc[:, zeta_q] = 0

            # Se inicializa el conjunto ET de transiciones de tareas para el modelo discreto
            ET = np.zeros((m, n))

            FSC = np.zeros(m * n)

            # Se calcula el remaining jobs execution Re_tau(j,i)
            for j in range(0, m):
                for i in range(0, n):
                    FSC[i + j * n] = jFSCi[i + j * n] * sd
                    iREj[i + j * n] = m_exec[i + j * n] - Mexec[i + j * n]

                    if round(iREj[i + j * n], 4) > 0:
                        ET[j, i] = i + 1
                    else:
                        ET[j, i] = 0

            for j in range(0, m):
                # Si el conjunto no es vacio por cada j-esimo CPU, entonces se procede a
                # calcular la prioridad de cada tarea a ser asignada
                if not np.array_equal(ET[j, :], np.zeros((1, len(ET[0])))):
                    # Prioridad es igual al marcado del lugar continuo menos el marcado del lugar discreto
                    iPRj[j, :] = jFSCi[j * n: j * n + n] * sd - Mexec[j * n:j * n + n]

                    # Se ordenan de manera descendente por orden de prioridad,
                    # IndMaxPr contiene los indices de las tareas ordenado de mayor a
                    # menor prioridad
                    IndMaxPr = np.flip(np.argsort(iPRj[j, :]))  # FIXME: Check if is descend

                    # Si en el vector ET(j,k) existe un cero entonces significa que en
                    # la posicion k la tarea no tine a Re_tau(j,k)>0 (es decir la tarea ya ejecuto lo que debía)
                    # entonces hay que incrementar a la siguiente posicion k+1 para tomar a la tarea de
                    # mayor prioridad
                    k = 1
                    while ET[j, IndMaxPr[k - 1]] == 0:
                        k = k + 1

                    # Se toma la tarea de mayor prioridad en el conjunto ET
                    IndMaxPr = int(ET[j, IndMaxPr[k]])

                    # si se asigna la procesador j la tarea de mayor prioridad IndMaxPr(1), entonces si en el
                    # conjunto ET para los procesadores restantes debe pasar que ET(k,IndMaxPr(1))=0,
                    # para evitar que las tareas se ejecuten de manera paralela
                    for k in range(0, m):
                        if j != k:
                            ET[k, IndMaxPr] = 0

                    i_tau_disc[IndMaxPr + j * n, zeta_q] = 1

                    Mexec[IndMaxPr + j * n] += quantum

            MEXEC = np.concatenate((MEXEC, Mexec))
            mo_nextDisc, m_execDisc, m_busyDisc, TempDisc, toutDisc, TempTimeDisc, m_TCPN = solve_global_model(
                global_model, moDisc.reshape(len(moDisc)), i_tau_disc[:, zeta_q], environment_specification.t_env,
                np.asarray(list(np.arange(zeta, zeta + quantum + 1, step))))

            moDisc = mo_nextDisc
            M = M + [m_TCPN]

            TEMPERATURE_DISC = TEMPERATURE_DISC + [TempTimeDisc]
            TIME_Temp = TIME_Temp + [toutDisc]
            TIMEZ = TIMEZ + [zeta]

            if np.array_equal(round(zeta, 3), sd):
                kd = kd + 1
                if kd + 1 <= len(sd_u):
                    sd = sd_u[kd]

            zeta = zeta + quantum
            zeta_q = zeta_q + 1

        SCH_OLDTFS = i_tau_disc

        return M, mo, TIMEZ, SCH_OLDTFS, MEXEC, MEXEC_TCPN, TIMEstep, TIME_Temp, TEMPERATURE_CONT, TEMPERATURE_DISC
