import functools
import operator
from typing import List, Optional

import numpy
import scipy.sparse
import scipy.sparse.linalg

from main.core.problem_specification.GlobalSpecification import GlobalSpecification
from main.core.problem_specification.tasks_specification.TasksSpecification import TasksSpecification
from main.core.schedulers_definition.templates.AbstractScheduler import AbstractScheduler

from main.core.execution_simulator.system_simulator.SystemAperiodicTask import SystemAperiodicTask
from main.core.execution_simulator.system_simulator.SystemPeriodicTask import SystemPeriodicTask
from main.core.execution_simulator.system_simulator.SystemTask import SystemTask
from main.core.execution_simulator.system_modeling.ProcessorModel import ProcessorModel
from main.core.execution_simulator.system_modeling.TasksModel import TasksModel
from main.core.tcpn_simulator.implementation.numerical_integration.TcpnSimulatorOptimizedTasksAndProcessors import \
    TcpnSimulatorOptimizedTasksAndProcessors


class OLDTFSScheduler(AbstractScheduler):
    """
    Implements the OLDTFS scheduler
    """

    def __init__(self) -> None:
        super().__init__()
        # Scheduler variables
        self.__set_of_deadlines = None
        self.__j_fsc_i = None
        self.__m_exec_accumulated = None
        self.__quantum = None

        # Specification variables
        self.__dt = None
        self.__m = None
        self.__n = None

        # TCPN simulator variables
        self.__tcpn_simulator = None
        self.__tcpn_mo = None
        self.__tcpn_lambda_len = None

    @staticmethod
    def __obtain_thermal_constraint(global_specification: GlobalSpecification) \
            -> [scipy.sparse.csc_matrix, scipy.sparse.csc_matrix, scipy.sparse.csc_matrix, scipy.sparse.csc_matrix]:
        """
        Returns the thermal constraint required in the LPP solving
        """

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

        lambda_vector_cond = numpy.concatenate(
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
        pre = scipy.sparse.hstack([pre_cond, pre_int])

        # Creation of post matrix
        post = scipy.sparse.hstack([post_cond, post_int])

        # Creation of lambda matrix
        lambda_vector = numpy.concatenate([lambda_vector_cond, lambda_vector_int])

        # Creation of S_T
        s_t = scipy.sparse.lil_matrix((m, p_board + m * p_one_micro))

        for i in range(m):
            s_t[i, p_board + i * p_one_micro + int(p_one_micro / 2)] = 1

        # New variables
        a = (post - pre).dot(scipy.sparse.diags(lambda_vector.reshape(-1))).dot(pre.transpose())
        b = (post_heat_dynamic - pre_heat_dynamic)[:places_board_and_micros, :]
        b_star = scipy.sparse.vstack(
            [lambda_vector_conv.reshape((-1, 1)), scipy.sparse.lil_matrix((m * p_one_micro, 1))])

        return a.tocsc(), b.tocsc(), scipy.sparse.csc_matrix(b_star), s_t.tocsc()

    @staticmethod
    def __solve_linear_programing_problem(global_specification: GlobalSpecification, is_thermal_simulation: bool) -> [
        numpy.ndarray, numpy.ndarray, float, numpy.ndarray]:
        """
        Solves the linear programing problem
        """

        h = global_specification.tasks_specification.h
        ti = numpy.asarray([i.t for i in global_specification.tasks_specification.periodic_tasks])
        ia = h / ti
        n = len(global_specification.tasks_specification.periodic_tasks)
        m = len(global_specification.cpu_specification.cores_specification.operating_frequencies)

        # Inequality constraint
        # Create matrix diag([cc1/H ... ccn/H cc1/H .....]) of n*m
        ch_vector = numpy.asarray(
            m * [i.c / global_specification.cpu_specification.cores_specification.available_frequencies[-1] for i in
                 global_specification.tasks_specification.periodic_tasks]) / h
        c_h = numpy.diag(ch_vector)

        a_eq = numpy.tile(numpy.eye(n), m)

        au = numpy.block_diag(
            *(m * [[i.c / global_specification.cpu_specification.cores_specification.available_frequencies[-1] for i in
                    global_specification.tasks_specification.periodic_tasks]])) / h

        beq = numpy.transpose(ia)
        bu = numpy.ones((m, 1))

        # Variable bounds
        bounds = (n * m) * [(0, None)]

        # Objective function
        objective = numpy.ones(n * m)

        # Optimization
        if is_thermal_simulation:
            a_t, ct_exec, b_ta, s_t = OLDTFSScheduler.__obtain_thermal_constraint(global_specification)

            # Inverse precision
            # WARNING: This is a workaround to deal with float precision
            inverse_precision = 5

            a_t.data = a_t.data.round(inverse_precision)
            a_t_inv = scipy.sparse.linalg.inv(a_t)

            a_int = - s_t.dot(a_t_inv).dot(ct_exec).dot(scipy.sparse.csc_matrix(c_h))
            a_int = a_int.toarray()

            b_int = scipy.sparse.csr_matrix(
                numpy.full((m, 1), global_specification.environment_specification.t_max)) + (s_t.dot(a_t_inv).dot(
                b_ta.reshape((-1, 1)))) * global_specification.environment_specification.t_env

            b_int = b_int.toarray()

            a = numpy.concatenate((a_int, au))
            b = numpy.concatenate((b_int.transpose(), bu.transpose()), axis=1)
        else:
            a = au
            b = bu

        # Interior points was the default in the original version, but i found that simplex has better results
        methods_for_solving_the_lpp = ["simplex", "revised simplex", "interior-point"]
        lpp_solved = False
        lpp_method_index = 0
        res = None
        while lpp_method_index < len(methods_for_solving_the_lpp) and not lpp_solved:
            try:
                res = numpy.optimize.linprog(c=objective, A_ub=a, b_ub=b, A_eq=a_eq, b_eq=beq, bounds=bounds,
                                             method=methods_for_solving_the_lpp[lpp_method_index])

                if res.success:
                    lpp_solved = True
                else:
                    print("The LPP could't be solved with the", methods_for_solving_the_lpp[lpp_method_index], "method")

            except ValueError:
                print("The LPP could't be solved with the", methods_for_solving_the_lpp[lpp_method_index], "method")

            lpp_method_index = lpp_method_index + 1

        if not lpp_solved:
            # No solution found
            raise Exception("Error: Offline stage, no solution found when trying to solve the lineal" +
                            " programing problem")

        j_b_i = res.x

        j_fsc_i = j_b_i * ch_vector

        # Quantum calc
        sd = numpy.union1d(
            functools.reduce(operator.add, [list(numpy.arange(ti[i], h + 1, ti[i])) for i in range(n)], []), 0)

        # Quantum precision
        # WARNING: This is a workaround to deal with float precision
        round_factor = 4
        fraction_denominator = 10 ** round_factor

        rounded_list = functools.reduce(operator.add,
                                        [(sd[i] * j_fsc_i * fraction_denominator).tolist() for i in
                                         range(1, len(sd) - 1)])
        rounded_list = [int(i) for i in rounded_list]

        quantum = numpy.gcd.reduce(rounded_list) / fraction_denominator

        if quantum < global_specification.simulation_specification.dt:
            quantum = global_specification.simulation_specification.dt

        # I commented it because I thought it wasn't necessary. As soon as the LPP find a feasible solution, it
        # involves that accomplish the thermal constraint
        #
        # if is_thermal_simulation:
        #     # Solve differential equation to get a initial condition
        #     theta = scipy.linalg.expm(a_t * h)
        #
        #     beta_1 = (scipy.linalg.inv(a_t)).dot(
        #         theta - scipy.identity(len(a_t)))
        #     beta_2 = beta_1.dot(b_ta.reshape((- 1, 1)))
        #     beta_1 = beta_1.dot(ct_exec)
        #
        #     # Set initial condition to zero to archive a final condition where initial = final, SmT(0) = Y(H)
        #     m_t_o = scipy.zeros((len(a_t), 1))
        #
        #     w_alloc_max = j_fsc_i / quantum
        #     m_t_max = theta.dot(m_t_o) + beta_1.dot(
        #         w_alloc_max.reshape(
        #             (len(w_alloc_max), 1))) + global_specification.environment_specification.t_env * beta_2
        #     temp_max = s_t.dot(m_t_max)
        #
        #     if all(item[0] > global_specification.environment_specification.t_max for item in temp_max / m):
        #         raise Exception(
        #             "Error: No one solution found when trying to solve the linear programing problem")

        return j_fsc_i, quantum

    @staticmethod
    def __obtain_tasks_processors_tcpn_model(global_specification: GlobalSpecification) -> [scipy.sparse.csr_matrix,
                                                                                            scipy.sparse.csr_matrix,
                                                                                            scipy.sparse.csr_matrix,
                                                                                            numpy.ndarray,
                                                                                            numpy.ndarray]:
        """
        Create a TCPN model for tasks and processors
        """
        # As the scheduler only accepts periodic tasks, it is not necessary to include aperiodic tasks in the TCPN
        # model of the scheduler
        n_periodic = len(global_specification.tasks_specification.periodic_tasks)

        m = len(global_specification.cpu_specification.cores_specification.operating_frequencies)

        # Create tasks-processors model
        tasks_model: TasksModel = TasksModel(
            TasksSpecification(global_specification.tasks_specification.periodic_tasks),
            global_specification.cpu_specification,
            global_specification.simulation_specification)

        processor_model: ProcessorModel = ProcessorModel(
            TasksSpecification(global_specification.tasks_specification.periodic_tasks),
            global_specification.cpu_specification,
            global_specification.simulation_specification)

        pre = scipy.sparse.vstack([
            scipy.sparse.hstack([tasks_model.pre_tau, tasks_model.pre_alloc_tau, scipy.sparse.csr_matrix(
                (n_periodic + n_periodic, n_periodic * m),
                dtype=global_specification.simulation_specification.type_precision)]),

            scipy.sparse.hstack([scipy.sparse.csr_matrix(
                (m * (2 * n_periodic + 1), n_periodic),
                dtype=global_specification.simulation_specification.type_precision),
                processor_model.pre_alloc_proc, processor_model.pre_exec_proc])
        ])

        post = scipy.sparse.vstack([
            scipy.sparse.hstack([tasks_model.post_tau, tasks_model.post_alloc_tau,
                                 scipy.sparse.csr_matrix(
                                     (2 * n_periodic, n_periodic * m),
                                     dtype=global_specification.simulation_specification.type_precision)]),
            scipy.sparse.hstack([scipy.sparse.csr_matrix(
                (m * (2 * n_periodic + 1), n_periodic),
                dtype=global_specification.simulation_specification.type_precision),
                processor_model.post_alloc_proc, processor_model.post_exec_proc])
        ])

        pi = scipy.sparse.vstack([
            scipy.sparse.hstack([tasks_model.pi_tau, tasks_model.pi_alloc_tau,
                                 scipy.sparse.csr_matrix(
                                     (2 * n_periodic, n_periodic * m),
                                     dtype=global_specification.simulation_specification.type_precision)]),
            scipy.sparse.hstack([scipy.sparse.csr_matrix(
                (m * (2 * n_periodic + 1), n_periodic),
                dtype=global_specification.simulation_specification.type_precision),
                processor_model.pi_alloc_proc,
                processor_model.pi_exec_proc])
        ]).transpose()

        lambda_vector = numpy.block([tasks_model.lambda_vector_tau, processor_model.lambda_vector_alloc_proc,
                                     processor_model.lambda_vector_exec_proc])

        mo = numpy.block([[tasks_model.mo_tau], [processor_model.mo_proc]])

        return pre, post, pi, lambda_vector, mo

    def offline_stage(self, global_specification: GlobalSpecification,
                      periodic_tasks: List[SystemPeriodicTask],
                      aperiodic_tasks: List[SystemAperiodicTask]) -> float:
        """
        Method to implement with the offline stage scheduler tasks
        :param aperiodic_tasks: list of aperiodic tasks with their assigned ids
        :param periodic_tasks: list of periodic tasks with their assigned ids
        :param global_specification: Global specification
        :return: 1 - Scheduling quantum (default will be the step specified in problem creation)
        """
        is_thermal_simulation = global_specification.environment_specification is not None

        # Obtain quantum and FSC
        j_fsc_i, quantum = self.__solve_linear_programing_problem(global_specification, is_thermal_simulation)

        # Number of tasks
        n = len(global_specification.tasks_specification.periodic_tasks)

        # Number of cores
        m = len(global_specification.cpu_specification.cores_specification.operating_frequencies)

        ti = [i.t for i in global_specification.tasks_specification.periodic_tasks]

        jobs = [int(i) for i in global_specification.tasks_specification.h / ti]

        d = numpy.zeros((n, numpy.amax(jobs)))

        sd_u = []
        for i in range(n):
            d[i, 0: jobs[i]] = list(numpy.arange(ti[i], global_specification.tasks_specification.h + 1, ti[i]))
            sd_u = numpy.union1d(sd_u, d[i, 0: jobs[i]])

        sd_u = numpy.union1d(sd_u, [0])

        # TCPN processor and tasks simulator that the scheduler needs to work
        tcpn_pre, tcpn_post, tcpn_pi, tcpn_lambda, tcpn_mo = self.__obtain_tasks_processors_tcpn_model(
            global_specification)

        self.__tcpn_simulator = TcpnSimulatorOptimizedTasksAndProcessors(tcpn_pre,
                                                                         tcpn_post,
                                                                         tcpn_pi,
                                                                         tcpn_lambda,
                                                                         global_specification.simulation_specification.dt_fragmentation_processor_task,
                                                                         global_specification.simulation_specification.dt)
        self.__tcpn_lambda_len = tcpn_lambda.shape[0]

        # Set of deadlines
        self.__set_of_deadlines = sd_u[1:]

        self.__j_fsc_i = j_fsc_i
        self.__m_exec_accumulated = numpy.zeros(n * m)
        self.__quantum = quantum

        self.__tcpn_mo = tcpn_mo

        self.__dt = global_specification.simulation_specification.dt

        self.__m = m
        self.__n = n

        return quantum

    def aperiodic_arrive(self, time: float, aperiodic_tasks_arrived: List[SystemTask],
                         actual_cores_frequency: List[float], cores_max_temperature: Optional[numpy.ndarray]) -> bool:
        """
        Method to implement with the actual on aperiodic arrive scheduler police
        :param actual_cores_frequency: Frequencies of cores
        :param time: actual simulation time passed
        :param aperiodic_tasks_arrived: aperiodic tasks arrived in this step (arrive_time == time)
        :param cores_max_temperature: temperature of each core
        :return: true if want to immediately call the scheduler (schedule_policy method), false otherwise
        """
        # Nothing to do, this scheduler can't execute aperiodic tasks
        return False

    def schedule_policy(self, time: float, executable_tasks: List[SystemTask], active_tasks: List[int],
                        actual_cores_frequency: List[float], cores_max_temperature: Optional[numpy.ndarray]) -> \
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
        # Actual deadline
        actual_deadline = self.__set_of_deadlines[0]

        # Update deadline
        if round(actual_deadline / self.__dt) == round(time / self.__dt):
            self.__set_of_deadlines = self.__set_of_deadlines[1:]

        # Sliding mode control
        steps_in_quantum = int(round(self.__quantum / self.__dt))

        for q_time in range(steps_in_quantum):
            # Obtain m_busy mark
            m_busy = numpy.concatenate([
                self.__tcpn_mo[2 * self.__n + (2 * self.__n + 1) * i: 2 * self.__n + (2 * self.__n + 1) * i + self.__n,
                0].reshape(-1) for i in range(self.__m)])

            # Obtain m_exec mark
            m_exec = numpy.concatenate([
                self.__tcpn_mo[
                2 * self.__n + (2 * self.__n + 1) * i + self.__n: 2 * self.__n + (2 * self.__n + 1) * i + 2 * self.__n,
                0].reshape(-1) for i in range(self.__m)])

            # Obtain the thermal fluid execution error
            e_i_fsc_j = self.__j_fsc_i * (time + q_time * self.__dt) - m_exec

            # Change of variable
            x1 = e_i_fsc_j
            x2 = m_busy

            # Sliding surface
            s = x1 - x2 + self.__j_fsc_i

            # Control for each task-processor pair
            w_alloc = (self.__j_fsc_i * numpy.asarray([numpy.sign(i) for i in s]) + self.__j_fsc_i) / 2

            # Simulate TCPN
            new_control = numpy.ones(self.__tcpn_lambda_len)
            new_control[self.__n:self.__n + self.__m * self.__n] = w_alloc

            self.__tcpn_simulator.set_control(new_control)
            self.__tcpn_mo = self.__tcpn_simulator.simulate_step(self.__tcpn_mo)

        # Discretization
        # Obtain m_exec mark
        m_exec = numpy.concatenate([
            self.__tcpn_mo[
            2 * self.__n + (2 * self.__n + 1) * i + self.__n: 2 * self.__n + (2 * self.__n + 1) * i + 2 * self.__n,
            0].reshape(-1) for i in range(self.__m)])

        # Remaining jobs execution Re_tau(j,i) calculation
        fsc = self.__j_fsc_i * actual_deadline

        re = m_exec - self.__m_exec_accumulated
        et = [round(re[i], 4) > 0 for i in range(self.__n * self.__m)]

        pr = fsc - re

        # Tasks that will be executed
        w_alloc = self.__m * [-1]

        # Tasks that can be executed this quantum
        executable_tasks = [i.id for i in executable_tasks]

        for j in range(self.__m):
            # Actual CPU ET
            local_et = et[self.__n * j: self.__n * j + self.__n]

            # Executable tasks in CPU j
            cpu_j_executable_tasks = [i not in w_alloc and i in executable_tasks and local_et[i] for i in
                                      range(self.__n)]

            # If exist at least one executable task
            if any(cpu_j_executable_tasks):
                # Obtain the tasks priority order
                ind_max_pr = numpy.flip(numpy.argsort(pr[self.__n * j: self.__n * j + self.__n]))

                # Only keep index of tasks that can be executed
                ind_max_pr = [i for i in ind_max_pr if cpu_j_executable_tasks[i]]

                w_alloc[j] = ind_max_pr[0]

                self.__m_exec_accumulated[j * self.__n + ind_max_pr[0]] += self.__quantum

        return w_alloc, None, None
