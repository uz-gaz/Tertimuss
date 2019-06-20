from typing import List

import scipy
from scipy.linalg import block_diag

from core.problem_specification_models.CpuSpecification import CpuSpecification, MaterialCuboid, Origin
from core.problem_specification_models.EnvironmentSpecification import EnvironmentSpecification
from core.problem_specification_models.SimulationSpecification import SimulationSpecification
from core.problem_specification_models.TasksSpecification import TasksSpecification


def simple_conductivity(material_cuboid: MaterialCuboid, simulation_specification: SimulationSpecification) -> [
    scipy.ndarray, scipy.ndarray, scipy.ndarray]:
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


def add_interactions_layer(p_board: int, p_one_micro: int, cpu_specification: CpuSpecification,
                           simulation_specification: SimulationSpecification) -> [scipy.ndarray, scipy.ndarray,
                                                                                  scipy.ndarray]:
    # Places and transitions for all CPUs
    p_micros = p_one_micro * cpu_specification.number_of_cores

    # Add transitions between micro and board
    # Connections between micro places and board places
    rel_micro = scipy.zeros(p_micros, dtype=int)

    for i in range(cpu_specification.number_of_cores):
        rel_micro[i * p_one_micro: (i + 1) * p_one_micro] = getCpuCoordinates(
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
                                                                            scipy.ndarray]:
    # TODO: Continuar por aqui
    rho_p1 = cpu_specification.board_specification.p
    cp_p1 = cpu_specification.board_specification.c_p

    h = environment_specification.h

    lambda_1 = (h / (cpu_specification.board_specification.z * rho_p1 * cp_p1)) * 1000

    lambda_convection = [lambda_1, lambda_1]  # TODO: Check, it might be lambda1, lambda2 (Ask authors)

    p_micros = p_one_micro * cpu_specification.number_of_cores

    # Number of places exposed at environment temperature
    exposed_places = p_board

    # Places under CPU
    # f = len(pre_sis)

    cota_micros = exposed_places - p_micros

    post_convection = scipy.concatenate(
        [block_diag(scipy.ones((cota_micros, 1)), scipy.ones((exposed_places - cota_micros, 1))),
         scipy.zeros((f - exposed_places, 2))])

    pre_it = scipy.concatenate([scipy.diag(scipy.ones(exposed_places)), scipy.zeros((f - exposed_places, exposed_places))])
    post_it = scipy.zeros((f, exposed_places))

    lambda_it = scipy.ones((exposed_places, 1)) * lambda_1

    pi = [1, 1]

    return pre_conv, post_convection, lambda_convection


def add_heat(pre_sis, post_sis, cpu_specification: CpuSpecification,
             task_specification: TasksSpecification) \
        -> [scipy.ndarray, scipy.ndarray, scipy.ndarray, scipy.ndarray]:
    rho = cpu_specification.cpu_core_specification.p
    cp = cpu_specification.cpu_core_specification.c_p

    # The generation is equal for each place in the same processor so lambdas are equal too
    lambda_gen = scipy.ones(len(task_specification.tasks) * cpu_specification.number_of_cores)

    for j in range(cpu_specification.number_of_cores):
        for i in range(len(task_specification.tasks)):
            lambda_gen[i + j * len(task_specification.tasks)] = cpu_specification.clock_relative_frequencies[j]

    places_proc = list(range(board_conductivity.p + 1,
                             board_conductivity.p + cpu_specification.number_of_cores * micro_conductivity.p + 1))

    l_places = len(places_proc)

    f = len(pre_sis)

    pre_gen = scipy.zeros((f, len(task_specification.tasks) * cpu_specification.number_of_cores))
    post_gen = scipy.zeros((f, len(task_specification.tasks) * cpu_specification.number_of_cores))

    j = 1
    for i in range(l_places):
        for k in range(len(task_specification.tasks)):
            post_gen[places_proc[i] - 1, j + k - 1] = (task_specification.tasks[k].e / (rho * cp)) * ((1000 ** 3) / (
                    cpu_specification.cpu_core_specification.x * cpu_specification.cpu_core_specification.y * cpu_specification.cpu_core_specification.z))

        if (i + 1) % micro_conductivity.p == 0:
            j = j + len(task_specification.tasks)

    pre_sis = scipy.concatenate((pre_sis, pre_gen), axis=1)
    post_sis = scipy.concatenate((post_sis, post_gen), axis=1)

    cp_exec = post_gen.dot(scipy.diag(lambda_gen))

    return cp_exec, lambda_gen, pre_sis, post_sis


def getCpuCoordinates(origin: Origin, cpu_spec: MaterialCuboid, board_spec: MaterialCuboid,
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
        p_one_micro = pre_micro_cond.shape[0] * cpu_specification.number_of_cores
        t_one_micro = pre_micro_cond.shape[1] * cpu_specification.number_of_cores

        # Create pre, post and lambda from the system with board and number of CPUs
        pre_sis = block_diag(*([pre_board_cond] + cpu_specification.number_of_cores * [pre_micro_cond]))
        del pre_board_cond  # Recover memory space
        del pre_micro_cond  # Recover memory space

        post_sis = block_diag(*([post_board_cond] + cpu_specification.number_of_cores * [post_micro_cond]))
        del post_board_cond  # Recover memory space
        del post_micro_cond  # Recover memory space

        lambda_vector = scipy.block([lambda_board_cond, lambda_micro_cond])
        del lambda_board_cond  # Recover memory space
        del lambda_micro_cond  # Recover memory space

        # Add transitions between micro and board
        # Connections between micro places and board places
        pre_int, post_int, lambda_vector_int = add_interactions_layer(p_board, p_one_micro, cpu_specification,
                                                                      simulation_specification)
        # pre_sis = scipy.concatenate((pre_sis, pre_int), axis=1)
        # post_sis = scipy.concatenate((post_sis, post_int), axis=1)

        # Convection
        diagonal, pre_sis, post_sis, lambda_vector = add_convection(pre_sis, post_sis, lambda_vector, cpu_specification,
                                                                    environment_specification)

        # Heat generation
        cp_exec, lambda_generated, pre_sis, post_sis = add_heat(pre_sis, post_sis, cpu_specification,
                                                                tasks_specification)

        lambda_vector = scipy.concatenate((lambda_vector, lambda_generated.reshape((-1, 1))))

        # Lineal system
        pi = pre_sis.transpose()

        # Output places
        l_measurement = scipy.zeros(cpu_specification.number_of_cores, dtype=scipy.int64)

        for i in range(cpu_specification.number_of_cores):
            l_measurement[i] = board_conductivity.p + i * micro_conductivity.p + scipy.math.ceil(
                micro_conductivity.p / 2)

        c = scipy.zeros((cpu_specification.number_of_cores, len(post_sis)))

        for i in range(cpu_specification.number_of_cores):
            c[i, l_measurement[i] - 1] = 1

        self.c_sis = post_sis - pre_sis
        self.lambda_sis = scipy.diag(lambda_vector.reshape(-1))
        self.pi = pi
        self.ct_exec = cp_exec
        self.s_t = c
        self.b_ta = diagonal
        self.lambda_gen = lambda_generated

    # def change_frequency(self, tasks_specification: TasksSpecification, cpu_specification: CpuSpecification):
    #     # TODO: TEST
    #     n = len(tasks_specification.tasks)
    #     m = cpu_specification.number_of_cores
    #
    #     # Transition rate
    #     eta = 100
    #
    #     # Total of transitions
    #     t = m * (2 * n)  # m processors*(n transitions alloc and n tramsition exec)
    #
    #     lambda_vector = scipy.zeros(t)
    #
    #     for k in range(n):
    #         f = cpu_specification.clock_frequencies[k]
    #
    #         # Execution rates for transitions exec for CPU_k \lambda^exec= eta*F
    #         lambda_vector[2 * k * n + n:2 * k * n + 2 * n] = eta * f * scipy.ones(n)
    #
    #         # Execution rates for transitions alloc \lambda^alloc= eta*\lambda^exec
    #         lambda_vector[2 * k * n:2 * k * n + n] = eta * lambda_vector[2 * k * n + n:2 * k * n + 2 * n]
    #
    #     lambda_proc = scipy.diag(lambda_vector)
    #     self.lambda_proc = lambda_proc
