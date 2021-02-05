import functools
import operator
from typing import List, Optional, Tuple, Dict, Set

import numpy
import scipy.sparse
import scipy.sparse.linalg
import scipy.linalg
import scipy.optimize

from tertimuss.tcpn_simulator import TCPNSimulatorVariableStepRK
from tertimuss.simulation_lib.math_utils import list_float_lcm, list_int_gcd
from ._system_tcpn_model import ThermalModelSelector, TasksModel, ProcessorModel, ThermalModelFrequencyAware, \
    ThermalModelEnergy
from tertimuss.simulation_lib.schedulers_definition import CentralizedAbstractScheduler
from tertimuss.simulation_lib.system_definition import ProcessorDefinition, EnvironmentSpecification, TaskSet


class OLDTFSScheduler(CentralizedAbstractScheduler):
    """
    Implements the OLDTFS scheduler

    Warning: Work in process. The implementation is not accurate and have some errors

    References:
        DOI: 10.1109/WODES.2016.7497860
    """

    def __init__(self, max_temperature_constraint: float, is_debug=True, simulate_thermal=True,
                 simulation_precision=numpy.float64, mesh_step: float = 0.01,
                 thermal_model_type: ThermalModelSelector = ThermalModelSelector.THERMAL_MODEL_FREQUENCY_BASED) -> None:
        super().__init__(is_debug)
        # Scheduler variables
        self.__set_of_deadlines = None
        self.__j_fsc_i = None
        self.__m_exec_accumulated = None
        self.__quantum = None

        # Specification variables
        self.__m = None
        self.__n = None

        # TCPN simulator variables
        self.__tcpn_simulator = None
        self.__tcpn_mo = None
        self.__tcpn_lambda_len = None

        # Scheduler specific parameters
        self.__simulate_thermal = simulate_thermal
        self.__simulation_precision = simulation_precision
        self.__mesh_step = mesh_step
        self.__thermal_model_type = thermal_model_type

        self.__max_temperature_constraint = max_temperature_constraint

        # Tasks id to index
        self.__index_to_task = {}
        self.__task_to_index = {}

        # Tasks id to jobs
        self.__task_to_job = {}
        self.__job_to_task = {}

    def check_schedulability(self, cpu_specification: ProcessorDefinition,
                             environment_specification: EnvironmentSpecification, task_set: TaskSet) \
            -> [bool, Optional[str]]:
        return True, ""

    @staticmethod
    def __obtain_thermal_constraint(cpu_specification: ProcessorDefinition,
                                    environment_specification: EnvironmentSpecification,
                                    task_set: TaskSet,
                                    thermal_model_type: ThermalModelSelector,
                                    simulation_precision
                                    ) -> [scipy.sparse.csc_matrix, scipy.sparse.csc_matrix, scipy.sparse.csc_matrix,
                                          scipy.sparse.csc_matrix]:
        """
        Returns the thermal constraint required in the LPP solving
        """
        # Number of cores
        m = len(cpu_specification.cores_definition)

        # We assume that we are in an homogeneous platform
        common_core_specification = cpu_specification.cores_definition[0].core_type

        thermal_model = ThermalModelFrequencyAware(
            cpu_specification, environment_specification, task_set, simulation_precision) if \
            thermal_model_type == ThermalModelSelector.THERMAL_MODEL_FREQUENCY_BASED else \
            ThermalModelEnergy(cpu_specification, environment_specification, task_set, simulation_precision)

        mesh_step = cpu_specification.measure_unit

        # Board and micros conductivity
        pre_board_cond, post_board_cond, lambda_board_cond = thermal_model.simple_conductivity(
            cpu_specification.board_definition.dimensions,
            cpu_specification.board_definition.material,
            mesh_step,
            simulation_precision)

        pre_micro_cond, post_micro_cond, lambda_micro_cond = thermal_model.simple_conductivity(
            common_core_specification.dimensions,
            common_core_specification.material,
            mesh_step,
            simulation_precision)

        # Number of places for the board
        p_board = pre_board_cond.shape[0]

        # Number of places and transitions for one CPU
        p_one_micro = pre_micro_cond.shape[0]

        # Create pre, post and lambda from the system with board and number of CPUs
        pre_cond = scipy.sparse.block_diag(([pre_board_cond] + [pre_micro_cond.copy() for _ in range(m)]))
        del pre_board_cond  # Recover memory space
        del pre_micro_cond  # Recover memory space

        post_cond = scipy.sparse.block_diag(([post_board_cond] + [post_micro_cond.copy() for _ in range(m)]))
        del post_board_cond  # Recover memory space
        del post_micro_cond  # Recover memory space

        lambda_vector_cond = numpy.concatenate(
            [lambda_board_cond] + m * [lambda_micro_cond])
        del lambda_board_cond  # Recover memory space
        del lambda_micro_cond  # Recover memory space

        # Add transitions between micro and board
        # Connections between micro places and board places
        pre_int, post_int, lambda_vector_int = thermal_model.add_interactions_layer(
            p_board, p_one_micro, cpu_specification, simulation_precision)

        # Convection
        pre_conv, post_conv, lambda_vector_conv, pre_conv_air, post_conv_air, lambda_vector_conv_air = \
            thermal_model.add_convection(p_board, p_one_micro, cpu_specification, environment_specification,
                                         simulation_precision)

        # Heat generation dynamic
        pre_heat_dynamic, post_heat_dynamic, lambda_vector_heat_dynamic, power_consumption = \
            thermal_model.add_heat_by_dynamic_power(p_board, p_one_micro, cpu_specification, task_set,
                                                    simulation_precision)

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

    @classmethod
    def __solve_linear_programing_problem(cls, cpu_specification: ProcessorDefinition,
                                          environment_specification: EnvironmentSpecification, task_set: TaskSet,
                                          thermal_model_type: ThermalModelSelector,
                                          simulation_precision,
                                          mesh_step: float,
                                          max_temperature_constraint: float,
                                          is_thermal_simulation: bool) -> [
        numpy.ndarray, numpy.ndarray, float, numpy.ndarray]:
        """
        Solves the linear programing problem
        """

        ti = [i.relative_deadline for i in task_set.periodic_tasks]

        h = list_float_lcm(ti)

        number_of_jobs = numpy.asarray([round(h / i) for i in ti])

        # h = global_specification.tasks_specification.convection_factor
        # ti = numpy.asarray([i.temperature for i in global_specification.tasks_specification.periodic_tasks])
        # ia = h / ti
        n = len(task_set.periodic_tasks)
        m = len(cpu_specification.cores_definition)

        # We assume that we are in an homogeneous platform
        common_core_specification = cpu_specification.cores_definition[0].core_type

        # Inequality constraint
        # Create matrix diag([cc1/H ... ccn/H cc1/H .....]) of n*m
        ch_vector = numpy.asarray(
            m * [i.worst_case_execution_time / max(common_core_specification.available_frequencies) for i in
                 task_set.periodic_tasks]) / h
        c_h = numpy.diag(ch_vector)

        a_eq = numpy.tile(numpy.eye(n), m)

        au = scipy.linalg.block_diag(
            *(m * [
                [i.worst_case_execution_time / max(common_core_specification.available_frequencies) for i in
                 task_set.periodic_tasks]])) / h

        beq = numpy.transpose(number_of_jobs)
        bu = numpy.ones((m, 1))

        # Variable bounds
        bounds = (n * m) * [(0, None)]

        # Objective function
        objective = numpy.ones(n * m)

        # Optimization
        if is_thermal_simulation:
            a_t, ct_exec, b_ta, s_t = cls.__obtain_thermal_constraint(cpu_specification,
                                                                      environment_specification,
                                                                      task_set,
                                                                      thermal_model_type,
                                                                      simulation_precision)

            # Inverse precision
            # WARNING: This is a workaround to deal with float precision
            inverse_precision = 5

            a_t.data = a_t.data.round(inverse_precision)
            a_t_inv = scipy.sparse.linalg.inv(a_t)

            a_int = - s_t.dot(a_t_inv).dot(ct_exec).dot(scipy.sparse.csc_matrix(c_h))
            a_int = a_int.toarray()

            b_int = scipy.sparse.csr_matrix(
                numpy.full((m, 1), max_temperature_constraint)) + (s_t.dot(a_t_inv).dot(
                b_ta.reshape((-1, 1)))) * environment_specification.temperature

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
                res = scipy.optimize.linprog(c=objective, A_ub=a, b_ub=b, A_eq=a_eq, b_eq=beq, bounds=bounds,
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

        rounded_list = functools.reduce(operator.add, ((sd[i] * j_fsc_i).tolist() for i in range(1, len(sd) - 1)))

        quantum = list_int_gcd([int(i) for i in rounded_list])

        return j_fsc_i, quantum

    @staticmethod
    def __obtain_tasks_processors_tcpn_model(cpu_specification: ProcessorDefinition,
                                             task_set: TaskSet, simulation_precision) -> [scipy.sparse.csr_matrix,
                                                                                          scipy.sparse.csr_matrix,
                                                                                          scipy.sparse.csr_matrix,
                                                                                          numpy.ndarray,
                                                                                          numpy.ndarray]:
        """
        Create a TCPN model for tasks and processors
        """
        # As the scheduler only accepts periodic tasks, it is not necessary to include aperiodic tasks in the TCPN
        # model of the scheduler
        n_periodic = len(task_set.periodic_tasks)

        m = len(cpu_specification.cores_definition)

        # Create tasks-processors model
        tasks_model: TasksModel = TasksModel(cpu_specification, task_set, simulation_precision)

        processor_model: ProcessorModel = ProcessorModel(cpu_specification, task_set, simulation_precision)

        pre = scipy.sparse.vstack([
            scipy.sparse.hstack([tasks_model.pre_tau, tasks_model.pre_alloc_tau, scipy.sparse.csr_matrix(
                (n_periodic + n_periodic, n_periodic * m),
                dtype=simulation_precision)]),

            scipy.sparse.hstack([scipy.sparse.csr_matrix(
                (m * (2 * n_periodic + 1), n_periodic),
                dtype=simulation_precision),
                processor_model.pre_alloc_proc, processor_model.pre_exec_proc])
        ])

        post = scipy.sparse.vstack([
            scipy.sparse.hstack([tasks_model.post_tau, tasks_model.post_alloc_tau,
                                 scipy.sparse.csr_matrix(
                                     (2 * n_periodic, n_periodic * m),
                                     dtype=simulation_precision)]),
            scipy.sparse.hstack([scipy.sparse.csr_matrix(
                (m * (2 * n_periodic + 1), n_periodic),
                dtype=simulation_precision),
                processor_model.post_alloc_proc, processor_model.post_exec_proc])
        ])

        pi = scipy.sparse.vstack([
            scipy.sparse.hstack([tasks_model.pi_tau, tasks_model.pi_alloc_tau,
                                 scipy.sparse.csr_matrix(
                                     (2 * n_periodic, n_periodic * m),
                                     dtype=simulation_precision)]),
            scipy.sparse.hstack([scipy.sparse.csr_matrix(
                (m * (2 * n_periodic + 1), n_periodic),
                dtype=simulation_precision),
                processor_model.pi_alloc_proc,
                processor_model.pi_exec_proc])
        ]).transpose()

        lambda_vector = numpy.block([tasks_model.lambda_vector_tau, processor_model.lambda_vector_alloc_proc,
                                     processor_model.lambda_vector_exec_proc])

        mo = numpy.block([[tasks_model.mo_tau], [processor_model.mo_proc]])

        return pre, post, pi, lambda_vector, mo

    def offline_stage(self, cpu_specification: ProcessorDefinition,
                      environment_specification: EnvironmentSpecification, task_set: TaskSet) -> int:
        # Obtain quantum and FSC

        # cpu_specification: Union[HomogeneousCpuSpecification],
        # environment_specification: EnvironmentSpecification, task_set: TaskSet,
        # thermal_model_type: ThermalModelSelector,
        # simulation_precision,
        # mesh_step: float,
        # max_temperature_constraint: float,
        # is_thermal_simulation

        j_fsc_i, quantum = self.__solve_linear_programing_problem(cpu_specification, environment_specification,
                                                                  task_set,
                                                                  self.__thermal_model_type,
                                                                  self.__simulation_precision,
                                                                  self.__mesh_step,
                                                                  self.__max_temperature_constraint,
                                                                  self.__simulate_thermal)

        self.__task_to_index = {i: j.identification for i, j in enumerate(task_set.periodic_tasks)}
        self.__index_to_task = {j.identification: i for i, j in enumerate(task_set.periodic_tasks)}

        # Number of tasks
        n = len(task_set.periodic_tasks)

        # Number of cores
        m = len(cpu_specification.cores_definition)

        ti = [i.relative_deadline for i in task_set.periodic_tasks]

        h = list_float_lcm(ti)

        number_of_jobs = [round(h / i) for i in ti]

        deadlines_of_jobs = numpy.zeros((n, numpy.amax(number_of_jobs)))

        # Set of deadlines including 0
        deadline_set = []
        for i in range(n):
            deadlines_of_jobs[i, 0: number_of_jobs[i]] = list(numpy.arange(ti[i], h + 1, ti[i]))
            deadline_set = numpy.union1d(deadline_set, deadlines_of_jobs[i, 0: number_of_jobs[i]])

        deadline_set = numpy.union1d(deadline_set, [0])

        # TCPN processor and tasks simulator that the scheduler needs to work
        tcpn_pre, tcpn_post, tcpn_pi, tcpn_lambda, tcpn_mo = self.__obtain_tasks_processors_tcpn_model(
            cpu_specification, task_set, self.__simulation_precision)

        self.__tcpn_simulator = TCPNSimulatorVariableStepRK(tcpn_pre,
                                                            tcpn_post,
                                                            tcpn_lambda,
                                                            tcpn_pi,
                                                            True)
        self.__tcpn_lambda_len = tcpn_lambda.shape[0]

        # Set of deadlines
        self.__set_of_deadlines = deadline_set[1:]

        self.__j_fsc_i = j_fsc_i
        self.__m_exec_accumulated = numpy.zeros(n * m)
        self.__quantum = quantum

        self.__tcpn_mo = tcpn_mo.reshape(-1)

        self.__m = m
        self.__n = n

        # We assume that we are in an homogeneous platform
        common_core_specification = cpu_specification.cores_definition[0].core_type

        return max(common_core_specification.available_frequencies)

    def schedule_policy(self, global_time: float, active_jobs_id: Set[int],
                        jobs_being_executed_id: Dict[int, int], cores_frequency: int,
                        cores_max_temperature: Optional[Dict[int, float]]) \
            -> Tuple[Dict[int, int], Optional[int], Optional[int]]:
        # Actual deadline
        actual_deadline = self.__set_of_deadlines[0]

        # Update deadline
        if round(actual_deadline * cores_frequency) == round(global_time * cores_frequency):
            self.__set_of_deadlines = self.__set_of_deadlines[1:]

        # Sliding mode control
        steps_in_quantum = int(round(self.__quantum * cores_frequency))

        for q_time in range(steps_in_quantum):
            # Obtain m_busy mark
            m_busy = numpy.concatenate([
                self.__tcpn_mo[
                2 * self.__n + (2 * self.__n + 1) * i: 2 * self.__n + (2 * self.__n + 1) * i + self.__n].reshape(-1) for
                i in range(self.__m)])

            # Obtain m_exec mark
            m_exec = numpy.concatenate([
                self.__tcpn_mo[
                2 * self.__n + (2 * self.__n + 1) * i + self.__n: 2 * self.__n + (
                        2 * self.__n + 1) * i + 2 * self.__n].reshape(-1) for i in range(self.__m)])

            # Obtain the thermal fluid execution error
            e_i_fsc_j = self.__j_fsc_i * (global_time + (q_time / cores_frequency)) - m_exec

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
            self.__tcpn_mo = self.__tcpn_simulator.simulate_step(self.__tcpn_mo, dt=self.__quantum)

        # Discretization
        # Obtain m_exec mark
        m_exec = numpy.concatenate([
            self.__tcpn_mo[
            2 * self.__n + (2 * self.__n + 1) * i + self.__n: 2 * self.__n + (
                        2 * self.__n + 1) * i + 2 * self.__n].reshape(-1) for i in range(self.__m)])

        # Remaining jobs execution Re_tau(j,i) calculation
        fsc = self.__j_fsc_i * actual_deadline

        re = m_exec - self.__m_exec_accumulated
        et = [round(re[i], 4) > 0 for i in range(self.__n * self.__m)]

        pr = fsc - re

        # Tasks that will be executed
        w_alloc = self.__m * [-1]

        # Tasks that can be executed this quantum
        executable_tasks = [self.__task_to_index[self.__job_to_task[i]] for i in active_jobs_id]

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

        return {i: self.__task_to_job[self.__index_to_task[j]] for (i, j) in enumerate(w_alloc) if j != -1}, \
               round(self.__quantum * cores_frequency), None

    def on_jobs_activation(self, global_time: float, activation_time: float,
                           jobs_id_tasks_ids: List[Tuple[int, int]]) -> bool:
        """
        Method to implement with the actual on job activation scheduler police.
        This method is the recommended place to detect the arrival of an aperiodic or sporadic task.

        :param jobs_id_tasks_ids: List[Identification of the job that have been activated,
         Identification of the task which job have been activated]
        :param global_time: Actual time in seconds since the simulation starts
        :param activation_time: Time where the activation was produced (It can be different from the global_time in the
         case that it doesn't adjust to a cycle end)
        :return: true if want to immediately call the scheduler (schedule_policy method), false otherwise
        """
        for job_id, task_id in jobs_id_tasks_ids:
            self.__job_to_task[job_id] = task_id
            self.__task_to_job[task_id] = job_id
        return super().on_jobs_activation(global_time, activation_time, jobs_id_tasks_ids)
