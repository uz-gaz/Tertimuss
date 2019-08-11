import functools
import operator
from typing import List, Optional

import scipy
import scipy.sparse
import scipy.sparse.linalg

import scipy.optimize

from main.core.problem_specification.GlobalSpecification import GlobalSpecification
from main.core.problem_specification.tasks_specification.TasksSpecification import TasksSpecification

from main.core.schedulers.templates.abstract_base_scheduler.AbstractBaseScheduler import AbstractBaseScheduler
from main.core.schedulers.templates.abstract_base_scheduler.BaseSchedulerAperiodicTask import BaseSchedulerAperiodicTask
from main.core.schedulers.templates.abstract_base_scheduler.BaseSchedulerPeriodicTask import BaseSchedulerPeriodicTask
from main.core.schedulers.templates.abstract_base_scheduler.BaseSchedulerTask import BaseSchedulerTask


class GlobalThermalAwareScheduler(AbstractBaseScheduler):
    def __init__(self) -> None:
        super().__init__()
        self.sd = None
        self.j_fsc_i = None
        self.m_exec_accumulated = None
        self.quantum = None
        self.m_exec_step = None
        self.m_busy = None
        self.step = None
        self.__m = None
        self.__n = None

    @staticmethod
    def __obtain_thermal_constraint(global_specification: GlobalSpecification) \
            -> [scipy.sparse.csc_matrix, scipy.sparse.csc_matrix, scipy.sparse.csc_matrix, scipy.sparse.csc_matrix]:

        tasks_specification = TasksSpecification(global_specification.tasks_specification.periodic_tasks)
        cpu_specification = global_specification.cpu_specification
        environment_specification = global_specification.environment_specification
        simulation_specification = global_specification.simulation_specification
        tcpn_model_specification = global_specification.tcpn_model_specification

        # Number of cores
        m = len(cpu_specification.cores_specification.operating_frequencies)

        # Board and micros conductivity
        pre_board_cond, post_board_cond, lambda_board_cond = tcpn_model_specification.thermal_model_selector.value.simple_conductivity(
            cpu_specification.board_specification.physical_properties,
            simulation_specification)

        pre_micro_cond, post_micro_cond, lambda_micro_cond = tcpn_model_specification.thermal_model_selector.value.simple_conductivity(
            cpu_specification.cores_specification.physical_properties, simulation_specification)

        # Number of places for the board
        p_board = pre_board_cond.shape[0]

        # Number of places and transitions for one CPU
        p_one_micro = pre_micro_cond.shape[0]

        # Create pre, post and lambda from the system with board and number of CPUs
        pre_cond = scipy.sparse.block_diag(([pre_board_cond] + [pre_micro_cond.copy() for _ in
                                                                range(m)]))
        del pre_board_cond  # Recover memory space
        del pre_micro_cond  # Recover memory space

        post_cond = scipy.sparse.block_diag(([post_board_cond] + [post_micro_cond.copy() for _ in
                                                                  range(m)]))
        del post_board_cond  # Recover memory space
        del post_micro_cond  # Recover memory space

        lambda_vector_cond = scipy.concatenate(
            [lambda_board_cond] + m * [lambda_micro_cond])
        del lambda_board_cond  # Recover memory space
        del lambda_micro_cond  # Recover memory space

        # Add transitions between micro and board
        # Connections between micro places and board places
        pre_int, post_int, lambda_vector_int = tcpn_model_specification.thermal_model_selector.value.add_interactions_layer(
            p_board, p_one_micro, cpu_specification,
            simulation_specification.mesh_step,
            simulation_specification)

        # Convection
        pre_conv, post_conv, lambda_vector_conv, pre_conv_air, post_conv_air, lambda_vector_conv_air = \
            tcpn_model_specification.thermal_model_selector.value.add_convection(p_board, p_one_micro,
                                                                                 cpu_specification,
                                                                                 environment_specification,
                                                                                 simulation_specification)

        # Heat generation dynamic
        pre_heat_dynamic, post_heat_dynamic, lambda_vector_heat_dynamic, power_consumption = \
            tcpn_model_specification.thermal_model_selector.value.add_heat_by_dynamic_power(p_board,
                                                                                            p_one_micro,
                                                                                            cpu_specification,
                                                                                            tasks_specification,
                                                                                            simulation_specification)

        # Number places of boards and micros
        places_board_and_micros = m * p_one_micro + p_board

        # Creation of pre matrix
        pre = scipy.sparse.hstack([pre_cond, pre_int, pre_conv, pre_heat_dynamic[:places_board_and_micros]])

        # Creation of post matrix
        post = scipy.sparse.hstack([post_cond, post_int, post_conv, post_heat_dynamic[:places_board_and_micros]])

        # Creation of lambda matrix
        lambda_vector = scipy.concatenate([lambda_vector_cond, lambda_vector_int, lambda_vector_conv,
                                           lambda_vector_heat_dynamic])

        # Creation of pre matrix
        pre_2 = scipy.sparse.hstack([pre_cond, pre_int])

        # Creation of post matrix
        post_2 = scipy.sparse.hstack([post_cond, post_int])

        # Creation of lambda matrix
        lambda_vector_2 = scipy.concatenate([lambda_vector_cond, lambda_vector_int])

        a_t = (pre - post).dot(scipy.sparse.diags(lambda_vector.reshape(-1))).dot(pre.transpose())

        ct_exec = (post_heat_dynamic[:places_board_and_micros]).dot(scipy.sparse.diags(lambda_vector_heat_dynamic))

        b_ta = (post_conv.dot(scipy.sparse.diags(lambda_vector_conv))).dot(
            scipy.sparse.csc_matrix(scipy.ones((p_board, 1))))

        # Creation of S_T
        s_t = scipy.sparse.lil_matrix((m, p_board + m * p_one_micro))

        for i in range(m):
            s_t[i, p_board + i * p_one_micro + int(p_one_micro / 2)] = 1

        # New variables
        a = (post_2 - pre_2).dot(scipy.sparse.diags(lambda_vector_2.reshape(-1))).dot(pre_2.transpose())
        b = (post_heat_dynamic - pre_heat_dynamic)[:places_board_and_micros, :]
        b_star = scipy.sparse.vstack(
            [lambda_vector_conv.reshape((-1, 1)), scipy.sparse.lil_matrix((m * p_one_micro, 1))])

        return a.tocsc(), b.tocsc(), scipy.sparse.csc_matrix(b_star), s_t.tocsc()

    @staticmethod
    def __obtain_thermal_constraint_2(global_specification: GlobalSpecification) \
            -> [scipy.ndarray, scipy.ndarray, scipy.ndarray, scipy.ndarray]:

        tasks_specification = TasksSpecification(global_specification.tasks_specification.periodic_tasks)
        cpu_specification = global_specification.cpu_specification
        environment_specification = global_specification.environment_specification
        simulation_specification = global_specification.simulation_specification
        tcpn_model_specification = global_specification.tcpn_model_specification

        # Number of cores
        m = len(cpu_specification.cores_specification.operating_frequencies)

        # Board and micros conductivity
        pre_board_cond, post_board_cond, lambda_board_cond = tcpn_model_specification.thermal_model_selector.value.simple_conductivity(
            cpu_specification.board_specification.physical_properties,
            simulation_specification)

        pre_micro_cond, post_micro_cond, lambda_micro_cond = tcpn_model_specification.thermal_model_selector.value.simple_conductivity(
            cpu_specification.cores_specification.physical_properties, simulation_specification)

        # Number of places for the board
        p_board = pre_board_cond.shape[0]

        # Number of places and transitions for one CPU
        p_one_micro = pre_micro_cond.shape[0]

        # Create pre, post and lambda from the system with board and number of CPUs
        pre_cond = scipy.sparse.block_diag(([pre_board_cond] + [pre_micro_cond.copy() for _ in
                                                                range(m)]))
        del pre_board_cond  # Recover memory space
        del pre_micro_cond  # Recover memory space

        post_cond = scipy.sparse.block_diag(([post_board_cond] + [post_micro_cond.copy() for _ in
                                                                  range(m)]))
        del post_board_cond  # Recover memory space
        del post_micro_cond  # Recover memory space

        lambda_vector_cond = scipy.concatenate(
            [lambda_board_cond] + m * [lambda_micro_cond])
        del lambda_board_cond  # Recover memory space
        del lambda_micro_cond  # Recover memory space

        # Add transitions between micro and board
        # Connections between micro places and board places
        pre_int, post_int, lambda_vector_int = tcpn_model_specification.thermal_model_selector.value.add_interactions_layer(
            p_board, p_one_micro, cpu_specification,
            simulation_specification.mesh_step,
            simulation_specification)

        # Convection
        pre_conv, post_conv, lambda_vector_conv, pre_conv_air, post_conv_air, lambda_vector_conv_air = \
            tcpn_model_specification.thermal_model_selector.value.add_convection(p_board, p_one_micro,
                                                                                 cpu_specification,
                                                                                 environment_specification,
                                                                                 simulation_specification)

        # Heat generation dynamic
        pre_heat_dynamic, post_heat_dynamic, lambda_vector_heat_dynamic, power_consumption = \
            tcpn_model_specification.thermal_model_selector.value.add_heat_by_dynamic_power(p_board,
                                                                                            p_one_micro,
                                                                                            cpu_specification,
                                                                                            tasks_specification,
                                                                                            simulation_specification)

        # Number places of boards and micros
        places_board_and_micros = m * p_one_micro + p_board

        # Creation of pre matrix
        pre = scipy.sparse.hstack([pre_cond, pre_int, pre_conv, pre_heat_dynamic[:places_board_and_micros]])

        # Creation of post matrix
        post = scipy.sparse.hstack([post_cond, post_int, post_conv, post_heat_dynamic[:places_board_and_micros]])

        # Creation of lambda matrix
        lambda_vector = scipy.concatenate([lambda_vector_cond, lambda_vector_int, lambda_vector_conv,
                                           lambda_vector_heat_dynamic])

        # Creation of pre matrix
        pre_2 = scipy.sparse.hstack([pre_cond, pre_int])

        # Creation of post matrix
        post_2 = scipy.sparse.hstack([post_cond, post_int])

        # Creation of lambda matrix
        lambda_vector_2 = scipy.concatenate([lambda_vector_cond, lambda_vector_int])

        a_t = (pre - post).dot(scipy.sparse.diags(lambda_vector.reshape(-1))).dot(pre.transpose())

        ct_exec = (post_heat_dynamic[:places_board_and_micros]).dot(scipy.sparse.diags(lambda_vector_heat_dynamic))

        b_ta = (post_conv.dot(scipy.sparse.diags(lambda_vector_conv))).dot(
            scipy.sparse.csc_matrix(scipy.ones((p_board, 1))))

        # Creation of S_T
        s_t = scipy.sparse.lil_matrix((m, p_board + m * p_one_micro))

        for i in range(m):
            s_t[i, p_board + i * p_one_micro + int(p_one_micro / 2)] = 1

        # New variables
        a = (post_2 - pre_2).dot(scipy.sparse.diags(lambda_vector_2.reshape(-1))).dot(pre_2.transpose())
        b = (post_heat_dynamic - pre_heat_dynamic)[:places_board_and_micros, :]
        b_star = lambda_vector_conv.reshape((-1, 1))

        return a_t.toarray(), ct_exec.toarray(), b_ta.toarray(), s_t.toarray()

    @staticmethod
    def __solve_linear_programing_problem(global_specification: GlobalSpecification, is_thermal_simulation: bool) -> [
        scipy.ndarray, scipy.ndarray, float, scipy.ndarray]:

        h = global_specification.tasks_specification.h
        ti = scipy.asarray([i.t for i in global_specification.tasks_specification.periodic_tasks])
        ia = h / ti
        n = len(global_specification.tasks_specification.periodic_tasks)
        m = len(global_specification.cpu_specification.cores_specification.operating_frequencies)

        # Inequality constraint
        # Create matrix diag([cc1/H ... ccn/H cc1/H .....]) of n*m
        ch_vector = scipy.asarray(
            m * [i.c / global_specification.cpu_specification.cores_specification.available_frequencies[-1] for i in
                 global_specification.tasks_specification.periodic_tasks]) / h
        c_h = scipy.diag(ch_vector)

        a_eq = scipy.tile(scipy.eye(n), m)

        au = scipy.linalg.block_diag(
            *(m * [[i.c for i in global_specification.tasks_specification.periodic_tasks]])) / h

        beq = scipy.transpose(ia)
        bu = scipy.ones((m, 1))

        # Variable bounds
        bounds = (n * m) * [(0, None)]

        # Objective function
        objective = scipy.ones(n * m)

        a_t = None
        ct_exec = None
        b_ta = None
        s_t = None

        # Optimization
        if is_thermal_simulation:
            a_t, ct_exec, b_ta, s_t = GlobalThermalAwareScheduler.__obtain_thermal_constraint(global_specification)

            # a_int = - ((s_t.dot(scipy.sparse.linalg.inv(a_t.tocsc()).tocsr())).dot(ct_exec)).dot(
            #     scipy.sparse.csr_matrix(c_h))
            a_int = - s_t.dot(scipy.sparse.linalg.inv(a_t)).dot(ct_exec).dot(scipy.sparse.csc_matrix(c_h))
            a_int = a_int.toarray()

            a_t_inv = scipy.sparse.linalg.inv(a_t)

            a_t_2 = a_t.toarray()
            a_t_inv_2 = a_t_inv.toarray()
            inverse_check = a_t_2.dot(a_t_inv_2)

            b_int = scipy.sparse.csr_matrix(
                scipy.full((m, 1), global_specification.environment_specification.t_max)) + (
                        s_t.dot(scipy.sparse.linalg.inv(a_t)).dot(
                            b_ta.reshape((-1, 1)))) * global_specification.environment_specification.t_env

            b_int = b_int.toarray()

            a = scipy.concatenate((a_int, au))
            b = scipy.concatenate((b_int.transpose(), bu.transpose()), axis=1)
        else:
            a = au
            b = bu

        # Interior points was the default in the original version, but i found that simplex has better results
        res = scipy.optimize.linprog(c=objective, A_ub=a, b_ub=b, A_eq=a_eq, b_eq=beq, bounds=bounds, method='simplex')

        if not res.success:
            # No solution found
            raise Exception("Error: Offline stage, no solution found when trying to solve the lineal" +
                            " programing problem")

        j_b_i = res.x

        j_fsc_i = j_b_i * ch_vector

        # Quantum calc
        sd = scipy.union1d(
            functools.reduce(operator.add, [list(scipy.arange(ti[i], h + 1, ti[i])) for i in range(n)], []), 0)

        round_factor = 4  # Fixme: Check if higher round factor can be applied
        fraction_denominator = 10 ** round_factor

        rounded_list = functools.reduce(operator.add,
                                        [(sd[i] * j_fsc_i * fraction_denominator).tolist() for i in
                                         range(1, len(sd) - 1)])
        rounded_list = [int(i) for i in rounded_list]

        quantum = scipy.gcd.reduce(rounded_list) / fraction_denominator

        if quantum < global_specification.simulation_specification.dt:
            quantum = global_specification.simulation_specification.dt

        if is_thermal_simulation:
            # Solve differential equation to get a initial condition
            theta = scipy.linalg.expm(a_t * h)

            beta_1 = (scipy.linalg.inv(a_t)).dot(
                theta - scipy.identity(len(a_t)))
            beta_2 = beta_1.dot(b_ta.reshape((- 1, 1)))
            beta_1 = beta_1.dot(ct_exec)

            # Set initial condition to zero to archive a final condition where initial = final, SmT(0) = Y(H)
            m_t_o = scipy.zeros((len(a_t), 1))

            w_alloc_max = j_fsc_i / quantum
            m_t_max = theta.dot(m_t_o) + beta_1.dot(
                w_alloc_max.reshape(
                    (len(w_alloc_max), 1))) + global_specification.environment_specification.t_env * beta_2
            temp_max = s_t.dot(m_t_max)

            if all(item[0] > global_specification.environment_specification.t_max for item in temp_max / m):
                raise Exception(
                    "Error: No one solution found when trying to solve the linear programing problem is feasible")

        return j_fsc_i, quantum

    def offline_stage(self, global_specification: GlobalSpecification,
                      periodic_tasks: List[BaseSchedulerPeriodicTask],
                      aperiodic_tasks: List[BaseSchedulerAperiodicTask]) -> float:
        """
        Method to implement with the offline stage scheduler tasks
        :param aperiodic_tasks: list of aperiodic tasks with their assigned ids
        :param periodic_tasks: list of periodic tasks with their assigned ids
        :param global_specification: Global specification
        :return: 1 - Scheduling quantum (default will be the step specified in problem creation)
        """

        is_thermal_simulation = global_specification.environment_specification is not None

        j_fsc_i, quantum = self.__solve_linear_programing_problem(global_specification, is_thermal_simulation)

        # Number of tasks
        n = len(global_specification.tasks_specification.periodic_tasks)

        # Number of cores
        m = len(global_specification.cpu_specification.cores_specification.operating_frequencies)

        ti = [i.t for i in global_specification.tasks_specification.periodic_tasks]

        jobs = [int(i) for i in global_specification.tasks_specification.h / ti]

        diagonal = scipy.zeros((n, scipy.amax(jobs)))

        kd = 1
        sd_u = []
        for i in range(n):
            diagonal[i, 0: jobs[i]] = list(scipy.arange(ti[i], global_specification.tasks_specification.h + 1, ti[i]))
            sd_u = scipy.union1d(sd_u, diagonal[i, 0: jobs[i]])

        sd_u = scipy.union1d(sd_u, [0])

        self.sd = sd_u[kd]
        self.j_fsc_i = j_fsc_i
        self.m_exec_accumulated = scipy.zeros(n * m)
        self.quantum = quantum
        self.m_exec_step = scipy.zeros(n * m)

        self.m_busy = scipy.zeros(n * m)

        self.step = global_specification.simulation_specification.dt

        self.__m = m
        self.__n = n

        return quantum

    def aperiodic_arrive(self, time: float, aperiodic_tasks_arrived: List[BaseSchedulerTask],
                         actual_cores_frequency: List[float], cores_max_temperature: Optional[scipy.ndarray]) -> bool:
        """
        Method to implement with the actual on aperiodic arrive scheduler police
        :param actual_cores_frequency: Frequencies of cores
        :param time: actual simulation time passed
        :param aperiodic_tasks_arrived: aperiodic tasks arrived in this step (arrive_time == time)
        :param cores_max_temperature: temperature of each core
        :return: true if want to immediately call the scheduler (schedule_policy method), false otherwise
        """
        # Nothing to do, this scheduler won't execute aperiodics
        return False

    def schedule_policy(self, time: float, executable_tasks: List[BaseSchedulerTask], active_tasks: List[int],
                        actual_cores_frequency: List[float], cores_max_temperature: Optional[scipy.ndarray]) -> \
            [List[int], Optional[float], Optional[List[float]]]:
        """
        Method to implement with the actual scheduler police
        :param actual_cores_frequency: Frequencies of cores
        :param time: actual simulation time passed
        :param executable_tasks: actual tasks that can be executed ( c > 0 and arrive_time <= time)
        :param active_tasks: actual id of tasks assigned to cores (task with id -1 is the idle task)
        :param cores_max_temperature: temperature of each core
        :return: 1 - tasks to assign to cores in next step (task with id -1 is the idle task)
                 2 - next quantum size (if None, will be taken the quantum specified in the offline_stage)
                 3 - cores relatives frequencies for the next quantum (if None, will be taken the frequencies specified
                  in the problem specification)
        """

        sd = self.sd

        w_alloc = scipy.zeros(self.__n * self.__m)
        j_fsc_i = self.j_fsc_i

        i_re_j = scipy.zeros(self.__n * self.__m)
        i_pr_j = scipy.zeros((self.__m, self.__n))

        steps_in_quantum = int(round(self.quantum / self.step))
        step = self.step
        m_exec_step = self.m_exec_step

        m_busy = self.m_busy
        m_exec_accumulated = self.m_exec_accumulated

        for time_q in range(steps_in_quantum):
            for j in range(self.__m):
                for i in range(self.__n):
                    # Calculo del error, y la superficie para el sliding mode control
                    e_i_fsc_j = j_fsc_i[i + j * self.__n] * time - m_exec_step[i + j * self.__n]

                    # Cambio de variables
                    x1 = e_i_fsc_j
                    x2 = m_busy[i + j * self.__n]  # m_bussy

                    # Superficie
                    s = x1 - x2 + j_fsc_i[i + j * self.__n]

                    # Control Para tareas temporal en cada procesador w_alloc control en I_tau
                    w_alloc[i + j * self.__n] = (j_fsc_i[i + j * self.__n] * scipy.sign(s) + j_fsc_i[
                        i + j * self.__n]) / 2

            m_busy = w_alloc * step
            m_exec_step = m_exec_step + w_alloc * step

        # DISCRETIZATION
        # Se inicializa el conjunto ET de transiciones de tareas para el modelo discreto
        et = scipy.zeros((self.__m, self.__n), dtype=int)

        fsc = scipy.zeros(self.__m * self.__n)

        # Se calcula el remaining jobs execution Re_tau(j,i)
        for j in range(self.__m):
            for i in range(self.__n):
                fsc[i + j * self.__n] = j_fsc_i[i + j * self.__n] * sd
                i_re_j[i + j * self.__n] = m_exec_step[i + j * self.__n] - m_exec_accumulated[i + j * self.__n]

                if round(i_re_j[i + j * self.__n], 4) > 0:
                    et[j, i] = i + 1

        w_alloc = self.__m * [-1]

        for j in range(self.__m):
            # Si el conjunto no es vacio por cada j-esimo CPU, entonces se procede a
            # calcular la prioridad de cada tarea a ser asignada
            if scipy.count_nonzero(et[j]) > 0:
                # Prioridad es igual al marcado del lugar continuo menos el marcado del lugar discreto
                i_pr_j[j, :] = j_fsc_i[j * self.__n: j * self.__n + self.__n] * \
                               sd - m_exec_accumulated[j * self.__n:j * self.__n + self.__n]

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
                for k in range(self.__m):
                    if j != k:
                        et[k, ind_max_pr] = 0

                w_alloc[j] = ind_max_pr

                m_exec_accumulated[ind_max_pr + j * self.__n] += self.quantum

        self.m_exec_step = m_exec_step
        self.m_busy = m_busy
        self.m_exec_accumulated = m_exec_accumulated

        return w_alloc, None, None
