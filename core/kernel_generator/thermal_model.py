import abc
from typing import List

import scipy
import scipy.sparse
import scipy.linalg

from core.problem_specification_models.CpuSpecification import CpuSpecification, MaterialCuboid, Origin
from core.problem_specification_models.EnvironmentSpecification import EnvironmentSpecification
from core.problem_specification_models.SimulationSpecification import SimulationSpecification
from core.problem_specification_models.TasksSpecification import TasksSpecification


class ThermalModel(object):

    @staticmethod
    def simple_conductivity(material_cuboid: MaterialCuboid,
                            simulation_specification: SimulationSpecification) \
            -> [scipy.sparse.lil_matrix, scipy.sparse.lil_matrix, scipy.ndarray]:
        """

        :param material_cuboid: Board or CPU
        :param simulation_specification: Specification
        :return: Model
        """
        d_side = simulation_specification.step / 1000

        x: int = round(material_cuboid.x / simulation_specification.step)
        y: int = round(material_cuboid.y / simulation_specification.step)

        rho: float = material_cuboid.p
        k: float = material_cuboid.k
        cp: float = material_cuboid.c_p

        # Horizontal lambda and vertical lambda was refactored to achieve more precision
        # Horizontal lambda is equal to vertical lambda because sides are equals
        lambda_side = k / (rho * cp * (d_side ** 2))

        # Total number of PN places
        p: int = x * y

        # Total number of transitions -> One for each side in contact (two shared between two)
        t: int = 4 * p - 2 * (x + y)

        # C incidence matrix
        i_pre = [[1, 0],
                 [0, 1]]

        i_post = [[0, 1],
                  [1, 0]]

        # The places have been named in snake form
        # ie. 1 2 3
        #     6 5 4
        #     7 8 9 [...]
        # That is the way to create the incidence matrix with the transitions who connects
        # 1-2 (both), 2-3 [...], 8-9 until the transition t=[(x*2)*(y-1)] + (x-1)*2
        pre = scipy.sparse.lil_matrix((p, t), dtype=simulation_specification.type_precision)
        post = scipy.sparse.lil_matrix((p, t), dtype=simulation_specification.type_precision)

        # All lambdas are equals
        lambda_vector = scipy.full(t, lambda_side, dtype=simulation_specification.type_precision)

        for i in range(p - 1):
            j = i * 2
            pre[i:i + 2, j:j + 2] = i_pre
            post[i:i + 2, j:j + 2] = i_post

        # In the next part, we create the transitions that connect 1-6, 2-5, 4-9 y 5-8 (ie. t18 y t17 associated to 1-6)
        v_pre = [1, 0]
        v_post = [0, 1]

        for r in range(y - 1):
            i = (r + 2) * x - 1
            u = r * x
            j = 2 * (p - 1 + r * (x - 1))

            for _ in range(x - 1):
                pre[u, j: j + 2] = v_pre
                pre[i, j: j + 2] = v_post

                post[u, j: j + 2] = v_post
                post[i, j: j + 2] = v_pre

                i = i - 1
                j = j + 2
                u = u + 1

        return pre, post, lambda_vector

    @staticmethod
    def __get_cpu_coordinates(origin: Origin, cpu_spec: MaterialCuboid, board_spec: MaterialCuboid,
                              step: float) -> List[int]:
        x: int = round(cpu_spec.x / step)
        y: int = round(cpu_spec.y / step)

        x_0: int = round(origin.x / step)
        y_0: int = round(origin.y / step)

        x_1: int = x_0 + x
        y_1: int = y_0 + y

        places = []

        x_board: int = round(board_spec.x / step)

        for j in range(y_0, y_1):
            local_places = []
            for i in range(x_0, x_1):
                if j % 2 == 0:
                    local_places.append(j * x_board - (i - 1))
                else:
                    local_places.append((j - 1) * x_board + i)

            if j % 2 == 1:
                local_places.reverse()

            places = places + local_places

        return places

    @staticmethod
    def add_interactions_layer(p_board: int, p_one_micro: int, cpu_specification: CpuSpecification,
                               step: float, simulation_specification: SimulationSpecification) \
            -> [scipy.sparse.lil_matrix, scipy.sparse.lil_matrix, scipy.ndarray]:
        # Places and transitions for all CPUs
        p_micros = p_one_micro * cpu_specification.number_of_cores

        # Add transitions between micro and board
        # Connections between micro places and board places
        rel_micro = scipy.zeros(p_micros, dtype=int)

        for i in range(cpu_specification.number_of_cores):
            rel_micro[i * p_one_micro: (i + 1) * p_one_micro] = ThermalModel.__get_cpu_coordinates(
                cpu_specification.cpu_origins[i],
                cpu_specification.cpu_core_specification,
                cpu_specification.board_specification,
                step)

        rho_p1 = cpu_specification.board_specification.p
        k_p1 = cpu_specification.board_specification.k
        cp_p1 = cpu_specification.board_specification.c_p

        rho_p2 = cpu_specification.cpu_core_specification.p
        k_p2 = cpu_specification.cpu_core_specification.k
        cp_p2 = cpu_specification.cpu_core_specification.c_p

        # Refactored to improve precision
        lambda1 = (k_p1 * k_p2 / (cpu_specification.board_specification.z * rho_p1 * cp_p1 * (
                k_p2 * cpu_specification.board_specification.z + k_p1 * cpu_specification.cpu_core_specification.z))) \
                  * (2 * (1000 ** 2))

        lambda2 = (k_p1 * k_p2 / (cpu_specification.cpu_core_specification.z * rho_p2 * cp_p2 * (
                k_p2 * cpu_specification.board_specification.z + k_p1 * cpu_specification.cpu_core_specification.z))) \
                  * (2 * (1000 ** 2))

        lambda1_div_lambda2 = (cpu_specification.cpu_core_specification.z * rho_p2 * cp_p2) / (
                cpu_specification.board_specification.z * rho_p1 * cp_p1)
        lambda2_div_lambda1 = (cpu_specification.board_specification.z * rho_p1 * cp_p1) / (
                cpu_specification.cpu_core_specification.z * rho_p2 * cp_p2)

        pre_int = scipy.sparse.lil_matrix((p_micros + p_board, 2 * p_micros), dtype=simulation_specification.type_precision)
        post_int = scipy.sparse.lil_matrix((p_micros + p_board, 2 * p_micros), dtype=simulation_specification.type_precision)

        lambda_vector_int = scipy.asarray(p_micros * [lambda1, lambda2], dtype=simulation_specification.type_precision)

        for i in range(p_micros):
            j = i * 2
            pre_int[rel_micro[i] - 1, j] = 1
            pre_int[i + p_board, j + 1] = 1

            post_int[rel_micro[i] - 1, j + 1] = lambda1_div_lambda2
            post_int[i + p_board, j] = lambda2_div_lambda1

        return pre_int, post_int, lambda_vector_int

    @staticmethod
    def add_convection(p_board: int, p_one_micro: int, cpu_specification: CpuSpecification,
                       environment_specification: EnvironmentSpecification,
                       simulation_specification: SimulationSpecification) -> [scipy.sparse.lil_matrix,
                                                                              scipy.sparse.lil_matrix,
                                                                              scipy.ndarray,
                                                                              scipy.sparse.lil_matrix,
                                                                              scipy.sparse.lil_matrix,
                                                                              scipy.ndarray]:
        rho_p1 = cpu_specification.board_specification.p
        cp_p1 = cpu_specification.board_specification.c_p

        h = environment_specification.h

        lambda_convection = (h / (cpu_specification.board_specification.z * rho_p1 * cp_p1)) * 1000

        p_micros = p_one_micro * cpu_specification.number_of_cores

        # Number of places exposed at environment temperature
        exposed_places = p_board

        # Places under CPU
        total_places = p_micros + exposed_places

        # Transition t1 in the convection paper (temperature dissipation into the air)

        pre_conv = scipy.sparse.vstack(
            [scipy.sparse.identity(exposed_places, dtype=simulation_specification.type_precision, format="lil"),
             scipy.sparse.lil_matrix((p_micros, exposed_places), dtype=simulation_specification.type_precision)])
        post_conv = scipy.sparse.lil_matrix((total_places, exposed_places), dtype=simulation_specification.type_precision)
        lambda_conv = scipy.full(exposed_places, lambda_convection, dtype=simulation_specification.type_precision)

        # Transition t2 and place p2 in the convection paper
        pre_conv_air = scipy.sparse.lil_matrix((total_places + 1, 1), dtype=simulation_specification.type_precision)
        pre_conv_air[-1, 0] = 1
        post_conv_air = scipy.sparse.lil_matrix((total_places + 1, 1), dtype=simulation_specification.type_precision)
        post_conv_air[-1, 0] = 1
        post_conv_air[:exposed_places, 0] = 1

        lambda_conv_air = scipy.asarray([lambda_convection], dtype=simulation_specification.type_precision)

        return pre_conv, post_conv, lambda_conv, pre_conv_air, post_conv_air, lambda_conv_air

    @staticmethod
    def add_heat_by_leakage_power(p_board: int, p_one_micro: int, cpu_specification: CpuSpecification,
                                  simulation_specification: SimulationSpecification) \
            -> [scipy.sparse.lil_matrix, scipy.sparse.lil_matrix, scipy.ndarray]:
        # The generation is equal for each place in the same processor so lambdas are equal too
        lambda_coefficient_delta = cpu_specification.leakage_delta
        lambda_coefficient_alpha = cpu_specification.leakage_alpha

        # Places and transitions for all CPUs
        p_micros = p_one_micro * cpu_specification.number_of_cores

        # Total places (p_board + p_micros + p_air + p_alpha_heat_generation)
        total_places = p_board + p_micros + 1 + 1

        # Number of transitions m * ( t_1_delta_heat_generation ) + t_1_alpha_heat_generation
        number_of_transitions = p_micros + 1

        pre_gen = scipy.sparse.lil_matrix((total_places, number_of_transitions), dtype=simulation_specification.type_precision)

        # Connection between each P_temp and t_1_delta
        pre_gen[p_board:p_board + p_micros, 0:p_micros] = \
            scipy.sparse.identity(p_micros, dtype=simulation_specification.type_precision, format="lil")

        pre_gen[-1, -1] = 1  # Connection between P_alpha and t_1_alpha

        post_gen = scipy.sparse.lil_matrix((total_places, number_of_transitions), dtype=simulation_specification.type_precision)

        # Connection between t_1_delta and each P_temp
        post_gen[p_board:p_board + p_micros, 0:p_micros] = \
            2 * scipy.sparse.identity(p_micros, dtype=simulation_specification.type_precision, format="lil")

        post_gen[-1, -1] = 1  # Connection between t_1_alpha and P_alpha

        post_gen[p_board:p_board + p_micros, -1] = 1  # Connections between t_1_alpha and each P_temp

        lambda_gen = scipy.concatenate(
            [scipy.full(p_micros, lambda_coefficient_delta, dtype=simulation_specification.type_precision),
             scipy.asarray([lambda_coefficient_alpha], dtype=simulation_specification.type_precision)])

        return pre_gen, post_gen, lambda_gen

    @staticmethod
    @abc.abstractmethod
    def _get_dynamic_power_consumption(cpu_specification: CpuSpecification,
                                       tasks_specification: TasksSpecification,
                                       clock_relative_frequencies: List[float]) -> scipy.ndarray:
        """
        Method to implement. Return an array with shape (m , n). Each place contains the weight in the
        arcs t_exec_n -> cpu_m

        :param cpu_specification: Cpu specification
        :param tasks_specification: Tasks specification
        :param clock_relative_frequencies: Core frequencies
        :return: an array with shape (m , n). Each place contains the weight in the arcs t_exec_n -> cpu_m
        """
        pass

    @classmethod
    def add_heat_by_dynamic_power(cls, p_board: int, p_one_micro: int, cpu_specification: CpuSpecification,
                                  tasks_specification: TasksSpecification,
                                  simulation_specification: SimulationSpecification) \
            -> [scipy.sparse.lil_matrix, scipy.sparse.lil_matrix, scipy.ndarray]:
        n = len(tasks_specification.periodic_tasks) + len(tasks_specification.aperiodic_tasks)

        # Places and transitions for all CPUs
        p_micros = p_one_micro * cpu_specification.number_of_cores

        # Total places (p_board + p_micros + p_air + p_alpha_heat_generation + one for each t_exec)
        total_places = p_board + p_micros + 1 + 1 + cpu_specification.number_of_cores * n

        # Number of transitions one for each t_exec
        number_of_transitions = cpu_specification.number_of_cores * n

        pre_gen = scipy.sparse.lil_matrix((total_places, number_of_transitions), dtype=simulation_specification.type_precision)
        # Connection with p2 in paper
        pre_gen[p_board + p_micros + 1 + 1:p_board + p_micros + 1 + 1 + number_of_transitions, :] = \
            scipy.sparse.identity(number_of_transitions, dtype=simulation_specification.type_precision, format="lil")

        post_gen = scipy.sparse.lil_matrix((total_places, number_of_transitions), dtype=simulation_specification.type_precision)

        # This will ensure that m_exec will remain constant
        post_gen[p_board + p_micros + 1 + 1:p_board + p_micros + 1 + 1 + number_of_transitions, :] = \
            scipy.sparse.identity(number_of_transitions, dtype=simulation_specification.type_precision, format="lil")

        # Get power consumption by task in cpu
        dynamic_power_consumption = cls._get_dynamic_power_consumption(cpu_specification, tasks_specification,
                                                                       cpu_specification.clock_relative_frequencies)

        dynamic_power_consumption = scipy.sparse.csr_matrix(dynamic_power_consumption).tolil()

        # Transitions from exec to core places

        post_gen[p_board: p_board + p_micros, :] = scipy.sparse.block_diag([
            scipy.sparse.vstack(p_one_micro * [scipy.sparse.lil_matrix(dynamic_power_consumption[i, :])]) for i in
            range(dynamic_power_consumption.shape[0])])

        lambda_gen = scipy.concatenate([scipy.full(n, f, dtype=simulation_specification.type_precision) for f in
                                        cpu_specification.clock_relative_frequencies])

        return pre_gen, post_gen, lambda_gen

    @classmethod
    def change_frequency(cls, frequency_vector: List[float], post: scipy.ndarray, lambda_vector: scipy.ndarray,
                         cpu_specification: CpuSpecification, tasks_specification: TasksSpecification, p_board: int,
                         p_one_micro: int, simulation_specification: SimulationSpecification) \
            -> [scipy.sparse.lil_matrix, scipy.ndarray]:
        """
        Return new models adapted to the new frequencies
        :param simulation_specification:
        :param p_one_micro:
        :param p_board:
        :param frequency_vector:
        :param post:
        :param lambda_vector:
        :param cpu_specification:
        :param tasks_specification:
        :return:
        """
        # Get power consumption by task in cpu
        dynamic_power_consumption = cls._get_dynamic_power_consumption(cpu_specification, tasks_specification,
                                                                       cpu_specification.clock_relative_frequencies)

        dynamic_power_consumption = scipy.sparse.csr_matrix(dynamic_power_consumption).tolil()

        # Transitions from exec to core places
        post_sustitution = scipy.sparse.block_diag([
            scipy.sparse.vstack(p_one_micro * [scipy.sparse.lil_matrix(dynamic_power_consumption[i, :])]) for i in
            range(dynamic_power_consumption.shape[0])])

        n: int = len(tasks_specification.periodic_tasks) + len(tasks_specification.aperiodic_tasks)

        m = cpu_specification.number_of_cores

        lambda_sustitution = scipy.concatenate(
            [f * scipy.ones(n, dtype=simulation_specification.type_precision) for f in frequency_vector])

        lambda_vector[-n * m:] = lambda_sustitution

        post[p_board: p_board + p_one_micro * m, -n * m:] = post_sustitution

        return post, lambda_vector

    def __init__(self, tasks_specification: TasksSpecification, cpu_specification: CpuSpecification,
                 environment_specification: EnvironmentSpecification,
                 simulation_specification: SimulationSpecification):
        # Board and micros conductivity
        pre_board_cond, post_board_cond, lambda_board_cond = self.simple_conductivity(
            cpu_specification.board_specification,
            simulation_specification)

        pre_micro_cond, post_micro_cond, lambda_micro_cond = self.simple_conductivity(
            cpu_specification.cpu_core_specification, simulation_specification)

        # Number of places for the board
        p_board = pre_board_cond.shape[0]
        t_board = pre_board_cond.shape[1]

        # Number of places and transitions for one CPU
        p_one_micro = pre_micro_cond.shape[0]
        t_one_micro = pre_micro_cond.shape[1]

        # Create pre, post and lambda from the system with board and number of CPUs

        pre_cond = scipy.sparse.block_diag(([pre_board_cond] + [pre_micro_cond.copy() for _ in
                                                                range(cpu_specification.number_of_cores)]))
        del pre_board_cond  # Recover memory space
        del pre_micro_cond  # Recover memory space

        post_cond = scipy.sparse.block_diag(([post_board_cond] + [post_micro_cond.copy() for _ in
                                                                  range(cpu_specification.number_of_cores)]))
        del post_board_cond  # Recover memory space
        del post_micro_cond  # Recover memory space

        lambda_vector_cond = scipy.concatenate(
            [lambda_board_cond] + cpu_specification.number_of_cores * [lambda_micro_cond])
        del lambda_board_cond  # Recover memory space
        del lambda_micro_cond  # Recover memory space

        # Add transitions between micro and board
        # Connections between micro places and board places
        pre_int, post_int, lambda_vector_int = self.add_interactions_layer(p_board, p_one_micro, cpu_specification,
                                                                           simulation_specification.step,
                                                                           simulation_specification)

        # Convection
        pre_conv, post_conv, lambda_vector_conv, pre_conv_air, post_conv_air, lambda_vector_conv_air = \
            self.add_convection(p_board, p_one_micro, cpu_specification, environment_specification,
                                simulation_specification)

        # Heat generation leakage
        pre_heat_leakage, post_heat_leakage, lambda_vector_heat_leakage = \
            self.add_heat_by_leakage_power(p_board,
                                           p_one_micro,
                                           cpu_specification,
                                           simulation_specification)

        # Heat generation dynamic
        pre_heat_dynamic, post_heat_dynamic, lambda_vector_heat_dynamic = \
            self.add_heat_by_dynamic_power(p_board,
                                           p_one_micro,
                                           cpu_specification,
                                           tasks_specification,
                                           simulation_specification)

        # Thermal model generation
        zero_11 = scipy.sparse.lil_matrix((1, t_board + t_one_micro * cpu_specification.number_of_cores +
                                           2 * p_one_micro * cpu_specification.number_of_cores + p_board),
                                          dtype=simulation_specification.type_precision)
        zero_21 = scipy.sparse.lil_matrix((1, t_board + t_one_micro * cpu_specification.number_of_cores +
                                           2 * p_one_micro * cpu_specification.number_of_cores + p_board),
                                          dtype=simulation_specification.type_precision)

        zero_12 = scipy.sparse.lil_matrix((1, t_board + t_one_micro *
                                           cpu_specification.number_of_cores + 2 * p_one_micro *
                                           cpu_specification.number_of_cores +
                                           p_board + 1), dtype=simulation_specification.type_precision)
        zero_22 = scipy.sparse.lil_matrix((1, t_board + t_one_micro *
                                           cpu_specification.number_of_cores + 2 * p_one_micro *
                                           cpu_specification.number_of_cores +
                                           p_board + 1), dtype=simulation_specification.type_precision)

        n = len(tasks_specification.periodic_tasks) + len(tasks_specification.aperiodic_tasks)

        zero_13 = scipy.sparse.lil_matrix((cpu_specification.number_of_cores * n, t_board +
                                           t_one_micro * cpu_specification.number_of_cores + 2 * p_one_micro *
                                           cpu_specification.number_of_cores + p_board + 1 +
                                           cpu_specification.number_of_cores *
                                           p_one_micro + 1), dtype=simulation_specification.type_precision)
        zero_23 = scipy.sparse.lil_matrix((cpu_specification.number_of_cores * n, t_board +
                                           t_one_micro * cpu_specification.number_of_cores + 2 * p_one_micro *
                                           cpu_specification.number_of_cores + p_board + 1 +
                                           cpu_specification.number_of_cores *
                                           p_one_micro + 1), dtype=simulation_specification.type_precision)

        # Creation of pre matrix
        pre = scipy.sparse.hstack([pre_cond, pre_int, pre_conv])
        pre = scipy.sparse.vstack([pre, zero_11])
        pre = scipy.sparse.hstack([pre, pre_conv_air])
        pre = scipy.sparse.vstack([pre, zero_12])
        pre = scipy.sparse.hstack([pre, pre_heat_leakage])
        pre = scipy.sparse.vstack([pre, zero_13])
        pre = scipy.sparse.hstack([pre, pre_heat_dynamic])

        # Creation of post matrix
        post = scipy.sparse.hstack([post_cond, post_int, post_conv])
        post = scipy.sparse.vstack([post, zero_21])
        post = scipy.sparse.hstack([post, post_conv_air])
        post = scipy.sparse.vstack([post, zero_22])
        post = scipy.sparse.hstack([post, post_heat_leakage])
        post = scipy.sparse.vstack([post, zero_23])
        post = scipy.sparse.hstack([post, post_heat_dynamic])

        # Creation of lambda matrix
        lambda_vector = scipy.concatenate([lambda_vector_cond, lambda_vector_int, lambda_vector_conv,
                                           lambda_vector_conv_air, lambda_vector_heat_leakage,
                                           lambda_vector_heat_dynamic])

        # Creation of pi
        pi = pre.transpose().copy()

        # Creation of mo
        mo = scipy.concatenate([scipy.full(p_board + p_one_micro * cpu_specification.number_of_cores + 1,
                                           environment_specification.t_env),
                                scipy.asarray([1]),
                                scipy.zeros(cpu_specification.number_of_cores * n)
                                ]).reshape((-1, 1))

        self.pre_sis: scipy.sparse.csr_matrix = pre.tocsr()
        self.post_sis: scipy.sparse.csr_matrix = post.tocsr()
        self.pi_sis: scipy.sparse.csr_matrix = pi.tocsr()
        self.lambda_vector_sis = lambda_vector
        self.mo_sis: scipy.ndarray = mo
        self.p_board: int = p_board
        self.p_one_micro: int = p_one_micro
        self.t_board: int = t_board
        self.t_one_micro: int = t_one_micro
