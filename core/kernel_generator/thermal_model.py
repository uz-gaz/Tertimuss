from typing import List

import scipy
from scipy.linalg import block_diag

from core.problem_specification_models.CpuSpecification import CpuSpecification, MaterialCuboid, Origin
from core.problem_specification_models.EnvironmentSpecification import EnvironmentSpecification
from core.problem_specification_models.SimulationSpecification import SimulationSpecification
from core.problem_specification_models.TasksSpecification import TasksSpecification, Task


def simple_conductivity(material_cuboid: MaterialCuboid,
                        simulation_specification: SimulationSpecification) -> [scipy.ndarray,
                                                                               scipy.ndarray,
                                                                               scipy.ndarray]:
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
    pre = scipy.zeros((p, t))
    post = scipy.zeros((p, t))

    # All lambdas are equals
    lambda_vector = scipy.full(t, lambda_side)

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


def __get_cpu_coordinates(origin: Origin, cpu_spec: MaterialCuboid, board_spec: MaterialCuboid,
                          simulation_specification: SimulationSpecification) -> List[int]:
    x: int = round(cpu_spec.x / simulation_specification.step)
    y: int = round(cpu_spec.y / simulation_specification.step)

    x_0: int = round(origin.x / simulation_specification.step)
    y_0: int = round(origin.y / simulation_specification.step)

    x_1: int = x_0 + x
    y_1: int = y_0 + y

    places = []

    x_board: int = round(board_spec.x / simulation_specification.step)

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


def add_interactions_layer(p_board: int, p_one_micro: int, cpu_specification: CpuSpecification,
                           simulation_specification: SimulationSpecification) -> [scipy.ndarray, scipy.ndarray,
                                                                                  scipy.ndarray]:
    # Places and transitions for all CPUs
    p_micros = p_one_micro * cpu_specification.number_of_cores

    # Add transitions between micro and board
    # Connections between micro places and board places
    rel_micro = scipy.zeros(p_micros, dtype=int)

    for i in range(cpu_specification.number_of_cores):
        rel_micro[i * p_one_micro: (i + 1) * p_one_micro] = __get_cpu_coordinates(
            cpu_specification.cpu_origins[i],
            cpu_specification.cpu_core_specification,
            cpu_specification.board_specification,
            simulation_specification)

    rho_p1 = cpu_specification.board_specification.p
    k_p1 = cpu_specification.board_specification.k
    cp_p1 = cpu_specification.board_specification.c_p

    rho_p2 = cpu_specification.cpu_core_specification.p
    k_p2 = cpu_specification.cpu_core_specification.k
    cp_p2 = cpu_specification.cpu_core_specification.c_p

    # Refactored to improve precision
    lambda1 = (k_p1 * k_p2 / (cpu_specification.board_specification.z * rho_p1 * cp_p1 * (
            k_p2 * cpu_specification.board_specification.z + k_p1 * cpu_specification.cpu_core_specification.z))) * (
                      2 * (1000 ** 2))

    lambda2 = (k_p1 * k_p2 / (cpu_specification.cpu_core_specification.z * rho_p2 * cp_p2 * (
            k_p2 * cpu_specification.board_specification.z + k_p1 * cpu_specification.cpu_core_specification.z))) * (
                      2 * (1000 ** 2))

    lambda1_div_lambda2 = (cpu_specification.cpu_core_specification.z * rho_p2 * cp_p2) / (
            cpu_specification.board_specification.z * rho_p1 * cp_p1)
    lambda2_div_lambda1 = (cpu_specification.board_specification.z * rho_p1 * cp_p1) / (
            cpu_specification.cpu_core_specification.z * rho_p2 * cp_p2)

    pre_int = scipy.zeros((p_micros + p_board, 2 * p_micros))
    post_int = scipy.zeros((p_micros + p_board, 2 * p_micros))

    lambda_vector_int = scipy.asarray(p_micros * [lambda1, lambda2])

    for i in range(p_micros):
        j = i * 2
        pre_int[rel_micro[i] - 1, j: j + 2] = [1, 0]
        pre_int[i + p_board, j: j + 2] = [0, 1]

        post_int[rel_micro[i] - 1, j: j + 2] = [0, lambda1_div_lambda2]
        post_int[i + p_board, j: j + 2] = [lambda2_div_lambda1, 0]

    return pre_int, post_int, lambda_vector_int


def add_convection(p_board: int, p_one_micro: int, cpu_specification: CpuSpecification,
                   environment_specification: EnvironmentSpecification) -> [scipy.ndarray, scipy.ndarray, scipy.ndarray,
                                                                            scipy.ndarray, scipy.ndarray,
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
    pre_conv = scipy.concatenate(
        [scipy.diag(scipy.ones(exposed_places)), scipy.zeros((p_micros, exposed_places))])
    post_conv = scipy.zeros((total_places, exposed_places))
    lambda_conv = scipy.full(exposed_places, lambda_convection)

    # Transition t2 and place p2 in the convection paper
    pre_conv_air = scipy.zeros((total_places + 1, 1))
    pre_conv_air[-1, 0] = 1
    post_conv_air = scipy.zeros((total_places + 1, 1))
    post_conv_air[-1, 0] = 1
    post_conv_air[0:exposed_places, 0] = scipy.ones(exposed_places)
    lambda_conv_air = scipy.asarray([lambda_convection])

    return pre_conv, post_conv, lambda_conv, pre_conv_air, post_conv_air, lambda_conv_air


def add_heat_by_leakage_power(p_board: int, p_one_micro: int, cpu_specification: CpuSpecification) \
        -> [scipy.ndarray, scipy.ndarray, scipy.ndarray]:
    # The generation is equal for each place in the same processor so lambdas are equal too
    lambda_coefficient_delta = cpu_specification.leakage_delta
    lambda_coefficient_alpha = cpu_specification.leakage_alpha

    # Places and transitions for all CPUs
    p_micros = p_one_micro * cpu_specification.number_of_cores

    # Total places (p_board + p_micros + p_air + p_alpha_heat_generation)
    total_places = p_board + p_micros + 1 + 1

    # Number of transitions m * ( t_1_delta_heat_generation ) + t_1_alpha_heat_generation
    number_of_transitions = p_micros + 1

    pre_gen = scipy.zeros((total_places, number_of_transitions))

    pre_gen[p_board:p_board + p_micros, 0:p_micros] = scipy.identity(
        p_micros)  # Connection between each P_temp and t_1_delta

    pre_gen[-1, -1] = 1  # Connection between P_alpha and t_1_alpha

    post_gen = scipy.zeros((total_places, number_of_transitions))

    post_gen[p_board:p_board + p_micros, 0:p_micros] = 2 * scipy.identity(
        p_micros)  # Connection between t_1_delta and each P_temp

    post_gen[-1, -1] = 1  # Connection between t_1_alpha and P_alpha

    post_gen[p_board:p_board + p_micros, -1] = scipy.ones(p_micros)  # Connection between t_1_alpha and each P_temp

    lambda_gen = scipy.concatenate(
        [scipy.full(p_micros, lambda_coefficient_delta), [lambda_coefficient_alpha]])

    return pre_gen, post_gen, lambda_gen


def add_heat_by_dynamic_power(p_board: int, p_one_micro: int, cpu_specification: CpuSpecification,
                              tasks_specification: TasksSpecification) \
        -> [scipy.ndarray, scipy.ndarray, scipy.ndarray]:
    n = len(tasks_specification.periodic_tasks) + len(tasks_specification.aperiodic_tasks)

    rho = cpu_specification.cpu_core_specification.p
    cp = cpu_specification.cpu_core_specification.c_p
    v_cpu = cpu_specification.cpu_core_specification.z * cpu_specification.cpu_core_specification.x * \
            cpu_specification.cpu_core_specification.y / (1000 ** 3)

    # Places and transitions for all CPUs
    p_micros = p_one_micro * cpu_specification.number_of_cores

    # Total places (p_board + p_micros + p_air + p_alpha_heat_generation + one for each t_exec)
    total_places = p_board + p_micros + 1 + 1 + cpu_specification.number_of_cores * n

    # Number of transitions one for each t_exec
    number_of_transitions = cpu_specification.number_of_cores * n

    pre_gen = scipy.zeros((total_places, number_of_transitions))
    pre_gen[p_board + p_micros + 1 + 1:p_board + p_micros + 1 + 1 + number_of_transitions, :] = scipy.identity(
        number_of_transitions)  # Connection with p2 in paper

    post_gen = scipy.zeros((total_places, number_of_transitions))

    tasks: List[Task] = tasks_specification.periodic_tasks + tasks_specification.aperiodic_tasks
    post_power_by_cpu = scipy.concatenate(
        [scipy.full((p_one_micro, 1), task.e / (v_cpu * rho * cp)) for task in tasks], axis=1)

    post_gen[p_board: p_board + p_micros, :] = block_diag(*(cpu_specification.number_of_cores * [post_power_by_cpu]))

    # lambda_gen = scipy.concatenate(
    #     [f * scipy.ones(len(tasks_specification.tasks)) for f in cpu_specification.clock_relative_frequencies])
    lambda_gen = scipy.ones(n * cpu_specification.number_of_cores)

    return pre_gen, post_gen, lambda_gen


class ThermalModel(object):
    def __init__(self, tasks_specification: TasksSpecification, cpu_specification: CpuSpecification,
                 environment_specification: EnvironmentSpecification,
                 simulation_specification: SimulationSpecification):
        # Board and micros conductivity
        pre_board_cond, post_board_cond, lambda_board_cond = simple_conductivity(cpu_specification.board_specification,
                                                                                 simulation_specification)

        pre_micro_cond, post_micro_cond, lambda_micro_cond = simple_conductivity(
            cpu_specification.cpu_core_specification, simulation_specification)

        # Number of places for the board
        p_board = pre_board_cond.shape[0]
        t_board = pre_board_cond.shape[1]

        # Number of places and transitions for one CPU
        p_one_micro = pre_micro_cond.shape[0]
        t_one_micro = pre_micro_cond.shape[1]

        # Create pre, post and lambda from the system with board and number of CPUs
        pre_cond = block_diag(*([pre_board_cond] + cpu_specification.number_of_cores * [pre_micro_cond]))
        del pre_board_cond  # Recover memory space
        del pre_micro_cond  # Recover memory space

        post_cond = block_diag(*([post_board_cond] + cpu_specification.number_of_cores * [post_micro_cond]))
        del post_board_cond  # Recover memory space
        del post_micro_cond  # Recover memory space

        lambda_vector_cond = scipy.concatenate(
            [lambda_board_cond] + cpu_specification.number_of_cores * [lambda_micro_cond])
        del lambda_board_cond  # Recover memory space
        del lambda_micro_cond  # Recover memory space

        # Add transitions between micro and board
        # Connections between micro places and board places
        pre_int, post_int, lambda_vector_int = add_interactions_layer(p_board, p_one_micro, cpu_specification,
                                                                      simulation_specification)

        # Convection
        pre_conv, post_conv, lambda_vector_conv, pre_conv_air, post_conv_air, lambda_vector_conv_air = \
            add_convection(p_board, p_one_micro, cpu_specification, environment_specification)

        # Heat generation leakage
        pre_heat_leakage, post_heat_leakage, lambda_vector_heat_leakage = add_heat_by_leakage_power(p_board,
                                                                                                    p_one_micro,
                                                                                                    cpu_specification)

        # Heat generation dynamic
        pre_heat_dynamic, post_heat_dynamic, lambda_vector_heat_dynamic = add_heat_by_dynamic_power(p_board,
                                                                                                    p_one_micro,
                                                                                                    cpu_specification,
                                                                                                    tasks_specification)

        # Thermal model generation
        zero_1 = scipy.zeros((1, t_board + t_one_micro * cpu_specification.number_of_cores +
                              2 * p_one_micro * cpu_specification.number_of_cores + p_board))

        zero_2 = scipy.zeros((1, t_board + t_one_micro *
                              cpu_specification.number_of_cores + 2 * p_one_micro * cpu_specification.number_of_cores +
                              p_board + 1))

        n = len(tasks_specification.periodic_tasks) + len(tasks_specification.aperiodic_tasks)

        zero_3 = scipy.zeros((cpu_specification.number_of_cores * n, t_board +
                              t_one_micro * cpu_specification.number_of_cores + 2 * p_one_micro *
                              cpu_specification.number_of_cores + p_board + 1 + cpu_specification.number_of_cores *
                              p_one_micro + 1))

        # Creation of pre matrix
        pre = scipy.concatenate([pre_cond, pre_int, pre_conv], axis=1)
        pre = scipy.concatenate([pre, zero_1], axis=0)
        pre = scipy.concatenate([pre, pre_conv_air], axis=1)
        pre = scipy.concatenate([pre, zero_2], axis=0)
        pre = scipy.concatenate([pre, pre_heat_leakage], axis=1)
        pre = scipy.concatenate([pre, zero_3], axis=0)
        pre = scipy.concatenate([pre, pre_heat_dynamic], axis=1)

        # Creation of post matrix
        post = scipy.concatenate([post_cond, post_int, post_conv], axis=1)
        post = scipy.concatenate([post, zero_1], axis=0)
        post = scipy.concatenate([post, post_conv_air], axis=1)
        post = scipy.concatenate([post, zero_2], axis=0)
        post = scipy.concatenate([post, post_heat_leakage], axis=1)
        post = scipy.concatenate([post, zero_3], axis=0)
        post = scipy.concatenate([post, post_heat_dynamic], axis=1)

        # Creation of lambda matrix
        lambda_vector = scipy.concatenate([lambda_vector_cond, lambda_vector_int, lambda_vector_conv,
                                           lambda_vector_conv_air, lambda_vector_heat_leakage,
                                           lambda_vector_heat_dynamic])

        # Creation of pi
        pi = pre.transpose()

        # Creation of mo
        mo = scipy.concatenate([scipy.full(p_board + p_one_micro * cpu_specification.number_of_cores + 1,
                                           environment_specification.t_env),
                                scipy.asarray([1]),
                                scipy.zeros(cpu_specification.number_of_cores * n)
                                ]).reshape((-1, 1))

        self.pre_sis = pre
        self.post_sis = post
        self.pi_sis = pi
        self.lambda_vector_sis = lambda_vector
        self.mo_sis = mo
        self.p_board = p_board
        self.p_one_micro = p_one_micro
        self.t_board = t_board
        self.t_one_micro = t_one_micro
