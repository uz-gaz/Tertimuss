import functools
import operator
from typing import List, Optional

import scipy

import scipy.optimize

from core.kernel_generator.global_model import GlobalModel
from core.problem_specification_models.GlobalSpecification import GlobalSpecification

from core.schedulers.templates.abstract_global_scheduler import AbstractGlobalScheduler
from core.schedulers.implementations.global_wodes import GlobalSchedulerTask


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

    @staticmethod
    def __solve_linear_programing_problem(global_specification: GlobalSpecification,
                                          global_model: Optional[GlobalModel]) -> [scipy.ndarray,
                                                                                   scipy.ndarray, float,
                                                                                   scipy.ndarray]:
        h = global_specification.tasks_specification.h
        ti = scipy.asarray([i.t for i in global_specification.tasks_specification.tasks])
        ia = h / ti
        n = len(global_specification.tasks_specification.tasks)
        m = global_specification.cpu_specification.number_of_cores

        # Inequality constraint
        # Create matrix diag([cc1/H ... ccn/H cc1/H .....]) of n*m

        ch_vector = scipy.asarray(m * [i.c for i in global_specification.tasks_specification.tasks]) / h
        c_h = scipy.diag(ch_vector)

        a_eq = scipy.tile(scipy.eye(n), m)

        au = scipy.linalg.block_diag(*(m * [[i.c for i in global_specification.tasks_specification.tasks]])) / h

        beq = scipy.transpose(ia)
        bu = scipy.ones((m, 1))

        # Variable bounds
        bounds = (n * m) * [(0, None)]

        # Objective function
        objective = scipy.ones(n * m)

        # Optimization
        if global_model.enable_thermal_mode:
            a_t = global_model.a_t

            b = global_model.ct_exec

            s_t = global_model.selector_of_core_temperature

            b_ta = global_model.b_ta

            # Fixme: Check why a_t can't be inverted
            a_int = - ((s_t.dot(scipy.linalg.inv(a_t))).dot(b)).dot(c_h)

            b_int = global_specification.environment_specification.t_max * scipy.ones((m, 1)) + (
                (s_t.dot(scipy.linalg.inv(a_t))).dot(
                    b_ta.reshape((-1, 1)))) * global_specification.environment_specification.t_env

            a = scipy.concatenate((a_int, au))
            b = scipy.concatenate((b_int.transpose(), bu.transpose()), axis=1)
        else:
            a = au
            b = bu

        # Interior points was the default in the original version, but i found that simplex has better results
        res = scipy.optimize.linprog(c=objective, A_ub=a, b_ub=b, A_eq=a_eq,
                                     b_eq=beq, bounds=bounds, method='simplex')  # FIXME: Answer original authors

        if not res.success:
            # No solution found
            raise Exception("Error: No solution found when trying to solve the lineal programing problem")

        j_b_i = res.x

        j_fsc_i = j_b_i * ch_vector

        # Quantum calc
        sd = scipy.union1d(functools.reduce(operator.add, [list(range(ti[i], h + 1, ti[i])) for i in range(n)], []), 0)

        round_factor = 4  # Fixme: Check if higher round factor can be applied
        fraction_denominator = 10 ** round_factor

        rounded_list = functools.reduce(operator.add,
                                        [(sd[i] * j_fsc_i * fraction_denominator).tolist() for i in
                                         range(1, len(sd) - 1)])
        rounded_list = [int(i) for i in rounded_list]

        quantum = scipy.gcd.reduce(rounded_list) / fraction_denominator

        if quantum < global_specification.simulation_specification.dt:
            quantum = global_specification.simulation_specification.dt

        if global_model.enable_thermal_mode:
            # Solve differential equation to get a initial condition
            theta = scipy.linalg.expm(global_model.a_t * h)

            beta_1 = (scipy.linalg.inv(global_model.a_t)).dot(
                theta - scipy.identity(len(global_model.a_t)))
            beta_2 = beta_1.dot(global_model.b_ta.reshape((- 1, 1)))
            beta_1 = beta_1.dot(global_model.ct_exec)

            # Set initial condition to zero to archive a final condition where initial = final, SmT(0) = Y(H)
            m_t_o = scipy.zeros((len(global_model.a_t), 1))

            w_alloc_max = j_fsc_i / quantum
            m_t_max = theta.dot(m_t_o) + beta_1.dot(
                w_alloc_max.reshape(
                    (len(w_alloc_max), 1))) + global_specification.environment_specification.t_env * beta_2
            temp_max = global_model.selector_of_core_temperature.dot(m_t_max)

            if all(item[0] > global_specification.environment_specification.t_max for item in temp_max / m):
                raise Exception(
                    "Error: No one solution found when trying to solve the linear programing problem is feasible")

        return j_fsc_i, quantum

    def offline_stage(self, global_specification: GlobalSpecification, global_model: GlobalModel) -> [float,
                                                                                                      List[float]]:
        """
        This method can be overridden with the offline stage scheduler tasks
        :param global_specification: Global specification
        :param global_model: Global model
        :return: 1 - Scheduling quantum
        """

        j_fsc_i, quantum = self.__solve_linear_programing_problem(global_specification, global_model)

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
                        cores_frequency: Optional[List[float]], cores_temperature: Optional[scipy.ndarray]) -> \
            [List[int], Optional[float], Optional[List[float]]]:
        """
        Method to implement with the actual scheduler police
        :param cores_frequency: Frequencies of cores
        :param time: actual simulation time passed
        :param tasks: tasks
        :param m: number of cores
        :param active_tasks: actual id of tasks assigned to cores (task with id -1 is the idle task)
        :param cores_temperature: temperature of each core
        :return: 1 - tasks to assign to cores in next step (task with id -1 is the idle task)
                 2 - next quantum size (if None, will be taken the quantum specified in the offline_stage)
                 3 - cores relatives frequencies for the next quantum (if None, will be taken the frequencies specified
                  in the offline_stage)
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

        return w_alloc, None, None
