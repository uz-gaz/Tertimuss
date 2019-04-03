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

        sd = sd_u[kd]

        m_exec = np.zeros(len(jFSCi))
        m_busy = np.zeros(len(jFSCi))
        Mexec = np.zeros(len(jFSCi))
        TIMEZ = np.ndarray((0, 1))
        TIMEstep = np.asarray([])
        TIME_Temp = np.ndarray((0, 1))
        TEMPERATURE_CONT = np.ndarray((len(global_model.s) - 2 * len(walloc), 0))
        TEMPERATURE_DISC = np.ndarray((len(global_model.s) - 2 * len(walloc), 0))
        MEXEC = []
        MEXEC_TCPN = np.ndarray((len(walloc), 0))
        moDisc = global_model.mo
        M = np.zeros((len(global_model.mo), 0))
        mo = global_model.mo

        for zeta_q in range(0, int(tasks_specification.h / quantum)):
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
                                                                                                            time + step]))

                mo = mo_next
                TEMPERATURE_CONT = np.concatenate((TEMPERATURE_CONT, Temp), axis=1)
                TIMEstep = np.concatenate((TIMEstep, np.asarray([time])))
                MEXEC_TCPN = np.concatenate((MEXEC_TCPN, m_exec), axis=1)
                time = time + step

            # DISCRETIZATION
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
            M = np.concatenate((M, m_TCPN), axis=1)

            TEMPERATURE_DISC = np.concatenate((TEMPERATURE_DISC, TempTimeDisc), axis=1)
            TIME_Temp = np.concatenate((TIME_Temp, toutDisc))
            TIMEZ = np.concatenate((TIMEZ, np.asarray([zeta]).reshape((1, 1))))

            if np.array_equal(round(zeta, 3), sd):
                kd = kd + 1
                if kd + 1 <= len(sd_u):
                    sd = sd_u[kd]

            zeta = zeta + quantum

        SCH_OLDTFS = i_tau_disc

        # TODO: MEXEC está mal, debería de ser 6 x 240

        return M, mo, TIMEZ, SCH_OLDTFS, MEXEC, MEXEC_TCPN, TIMEstep.reshape(
            (-1, 1)), TIME_Temp, TEMPERATURE_CONT, TEMPERATURE_DISC
