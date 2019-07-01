from typing import List, Optional

import scipy

from core.kernel_generator.global_model import GlobalModel
from core.problem_specification_models.GlobalSpecification import GlobalSpecification

from core.schedulers.abstract_global_scheduler import AbstractGlobalScheduler
from core.schedulers.global_wodes_scheduler import GlobalSchedulerTask
from core.schedulers.utils.lineal_programing_problem_for_scheduling import \
    solve_lineal_programing_problem_for_scheduling


class GlobalThermalAwareScheduler(AbstractGlobalScheduler):
    def __init__(self) -> None:
        super().__init__()
        self.sd = None
        self.j_fsc_i = None
        self.m_exec_accumulated = None
        self.quantum = None
        self.m_exec_step = None
        self.m_busy = None
        self.step = None

    def offline_stage(self, global_specification: GlobalSpecification, global_model: GlobalModel) -> float:
        _, j_fsc_i, quantum, _ = solve_lineal_programing_problem_for_scheduling(
            global_specification.tasks_specification, global_specification.cpu_specification,
            global_specification.environment_specification,
            global_specification.simulation_specification, global_model)

        n = len(global_specification.tasks_specification.tasks)
        m = global_specification.cpu_specification.number_of_cores

        ti = [i.t for i in global_specification.tasks_specification.tasks]

        jobs = [int(i) for i in global_specification.tasks_specification.h / ti]

        diagonal = scipy.zeros((n, scipy.amax(jobs)))

        kd = 1
        sd_u = []
        for i in range(n):
            diagonal[i, 0: jobs[i]] = list(range(ti[i], global_specification.tasks_specification.h + 1, ti[i]))
            sd_u = scipy.union1d(sd_u, diagonal[i, 0: jobs[i]])

        sd_u = scipy.union1d(sd_u, [0])

        self.sd = sd_u[kd]
        self.j_fsc_i = j_fsc_i
        self.m_exec_accumulated = scipy.zeros(n * m)
        self.quantum = quantum
        self.m_exec_step = scipy.zeros(n * m)

        self.m_busy = scipy.zeros(n * m)

        self.step = global_specification.simulation_specification.dt

        return quantum

    def schedule_policy(self, time: float, tasks: List[GlobalSchedulerTask], m: int, active_tasks: List[int],
                        cores_frequency: List[float], cores_temperature: Optional[scipy.ndarray]) -> \
            List[int]:
        """
        Method to implement with the actual scheduler police
        :param cores_frequency: Frequencies of cores
        :param time: actual simulation time passed
        :param tasks: tasks
        :param m: number of cores
        :param active_tasks: actual id of tasks assigned to cores (task with id -1 is the idle task)
        :param cores_temperature: temperature of each core
        :return: tasks to assign to cores in next step (task with id -1 is the idle task)
        """
        n = len(tasks)

        sd = self.sd

        w_alloc = scipy.zeros(n * m)
        j_fsc_i = self.j_fsc_i

        i_re_j = scipy.zeros(n * m)
        i_pr_j = scipy.zeros((m, n))

        steps_in_quantum = int(round(self.quantum / self.step))
        step = self.step
        m_exec_step = self.m_exec_step

        m_busy = self.m_busy
        m_exec_accumulated = self.m_exec_accumulated

        for time_q in range(steps_in_quantum):
            for j in range(m):
                for i in range(n):
                    # Calculo del error, y la superficie para el sliding mode control
                    e_i_fsc_j = j_fsc_i[i + j * n] * time - m_exec_step[i + j * n]

                    # Cambio de variables
                    x1 = e_i_fsc_j
                    x2 = m_busy[i + j * n]  # m_bussy

                    # Superficie
                    s = x1 - x2 + j_fsc_i[i + j * n]

                    # Control Para tareas temporal en cada procesador w_alloc control en I_tau
                    w_alloc[i + j * n] = (j_fsc_i[i + j * n] * scipy.sign(s) + j_fsc_i[i + j * n]) / 2

            m_busy = w_alloc * step
            m_exec_step = m_exec_step + w_alloc * step

        # DISCRETIZATION
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

        w_alloc = m * [-1]

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

                w_alloc[j] = ind_max_pr

                m_exec_accumulated[ind_max_pr + j * n] += self.quantum

        self.m_exec_step = m_exec_step
        self.m_busy = m_busy
        self.m_exec_accumulated = m_exec_accumulated
        return w_alloc
