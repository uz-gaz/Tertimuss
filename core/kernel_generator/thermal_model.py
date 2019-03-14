import numpy as np

from core.problem_specification_models.CpuSpecification import CpuSpecification, MaterialCuboid
from core.problem_specification_models.EnvironmentSpecification import EnvironmentSpecification
from core.problem_specification_models.SimulationSpecification import SimulationSpecification
from core.problem_specification_models.TasksSpecification import TasksSpecification


class ConductivityModel(object):
    def __init__(self, pre, post, t, p, lambda_vector):
        self.pre = pre
        self.post = post
        self.t = t
        self.p = p
        self.lambda_vector = lambda_vector


def simple_conductivity(material_cuboid: MaterialCuboid,
                        simulation_specification: SimulationSpecification) -> ConductivityModel:
    dx = simulation_specification.step
    dy = simulation_specification.step
    dz = simulation_specification.step

    x = material_cuboid.x / dx
    y = material_cuboid.y / dy

    rho = material_cuboid.p
    k = material_cuboid.k
    cp = material_cuboid.c_p

    volume = dx * dy * dz  # Volumen, igual para todos los elementos
    horizontal_area = dy * dz  # Area de contacto para lugares contiguos horizontales
    vertical_area = dx * dz  # Area de contacto para lugares contiguos verticales

    dx_horizontal = dx / 2
    dx_vertical = dy / 2

    horizontal_lambda = (1 / (volume * rho * cp)) * (k * k * horizontal_area) / (k * dx_horizontal + k * dx_horizontal)
    vertical_lambda = (1 / (volume * rho * cp)) * (k * k * vertical_area) / (k * dx_vertical + k * dx_vertical)

    # Total de lugares de la RP
    p = x * y

    # Total de transiciones
    t = (x * y * 4) - 8 - 2 * (x - 2) - 2 * (y - 2)

    # Matriz de incidencia C
    i_pre = [[1, 0], [0, 1]]
    i_post = [[0, 1], [1, 0]]

    # Los lugares se numeran en forma de "serpiente"
    # ie. 1 2 3
    #     6 5 4
    #     7 8 9 [...]
    # Con eso se forma la matriz de incidencia
    # con las transiciones que conectan 1-2 (las dos), 2-3 [...], 8-9
    # hasta la transicion t=[(x*2)*(y-1)] + (x-1)*2
    pre = np.zeros((p, t))
    post = np.zeros((p, t))

    lambda_vector = np.zeros(p)

    for i in range(0, p):
        j = i * 3
        pre[i:i + 2, j:j + 2] = i_pre
        post[i:i + 2, j:j + 2] = i_post

        if (i + 1) % x == 0:
            lambda_vector[j, j + 2] = [vertical_lambda, vertical_lambda]
        else:
            lambda_vector[j, j + 2] = [horizontal_lambda, horizontal_lambda]

    # Para la siguiente parte de C se numeran las transiciones que
    # conectan 1-6, 2-5, 4-9 y 5-8 (ie. t18 y t17 asociadas a 1-6)
    v_pre = [1, 0]
    v_post = [0, 1]

    start = 1
    # TODO: REVISAR
    j = 1 + 2 * (p - 1)

    for count in range(2, y + 1):
        xx = count * x
        for i in range(1, x):
            pre[start - 1, j - 1: j + 1] = v_pre
            pre[xx - 1, j - 1: j + 1] = v_post

            post[start - 1, j - 1: j + 1] = v_post
            post[xx - 1, j - 1: j + 1] = v_pre
            lambda_vector[j - 1: j + 1] = [vertical_lambda, vertical_lambda]

            xx = xx - 1
            j = j + 2
            start = start + 1
        start = xx

    return ConductivityModel(pre, post, t, p, lambda_vector)


def add_interactions_layer(rel_micro, pre_sis, post_sis, lambda_vector, board_conductivity: ConductivityModel,
                           micro_conductivity: ConductivityModel, cpu_specification: CpuSpecification,
                           simulation_specification: SimulationSpecification):
    # TODO: REVISAR
    dx_p1 = cpu_specification.cpu_core.x
    dy_p1 = cpu_specification.cpu_core.y
    dz_p1 = cpu_specification.cpu_core.z

    rho_p1 = cpu_specification.cpu_core.p
    k_p1 = cpu_specification.cpu_core.k
    cp_p1 = cpu_specification.cpu_core.c_p

    dx_p2 = cpu_specification.board.x
    dy_p2 = cpu_specification.board.y
    dz_p2 = cpu_specification.board.z

    rho_p2 = cpu_specification.board.p
    k_p2 = cpu_specification.board.k
    cp_p2 = cpu_specification.board.c_p

    a = dx_p1 * dy_p1

    v_p1 = a * dz_p1
    deltax_p1 = dz_p1 / 2

    v_p2 = dx_p2 * dy_p2 * dz_p2
    deltax_p2 = dz_p2 / 2

    lambda1 = (1 / (v_p1 * rho_p1 * cp_p1)) * (k_p1 * k_p2 * a) / (k_p2 * deltax_p1 + k_p1 * deltax_p2)
    lambda2 = (1 / (v_p2 * rho_p2 * cp_p2)) * (k_p1 * k_p2 * a) / (k_p2 * deltax_p1 + k_p1 * deltax_p2)

    l_lug = len(rel_micro)

    len_pre = len(pre_sis)

    j = len_pre + 1

    v_pre = [1, 0]
    v_post = [0, 1]

    for i in range(1, l_lug + 1):
        pre_sis[rel_micro[i - 1], j - 1, j + 1] = v_pre
        pre_sis[i + cpu_specification.board.p, j - 1: j + 1] = v_post

        post_sis[rel_micro[i - 1], j - 1, j + 1] = [0, lambda1 / lambda2]
        post_sis[i + cpu_specification.board.p, j - 1: j + 1] = [lambda2 / lambda1, 0]

        lambda_vector[j - 1, j + 1] = [lambda1, lambda2]
        j = j + 2


def add_convection(diagonal, rel_micro, pre_sis, post_sis, lambda_vector, board_conductivity: ConductivityModel,
                   micro_conductivity: ConductivityModel, cpu_specification: CpuSpecification,
                   simulation_specification: SimulationSpecification):
    # TODO:
    pass


def add_heat(cp_exec, lambda_gen, pre_sis, post_sis, lambda_vector, board_conductivity: ConductivityModel,
             micro_conductivity: ConductivityModel, cpu_specification: CpuSpecification,
             simulation_specification: SimulationSpecification):
    # TODO:
    pass


class ThermalModel(object):
    def __init__(self, a_t, ct_exec, s_t, b_ta, lambda_gen):
        self.a_t = a_t
        self.ct_exec = ct_exec
        self.s_t = s_t
        self.b_ta = b_ta
        self.lambda_gen = lambda_gen


def generate_thermal_model(tasks_specification: TasksSpecification, cpu_specification: CpuSpecification,
                           environment_specification: EnvironmentSpecification,
                           simulation_specification: SimulationSpecification) -> ThermalModel:
    # TODO: Try to improve implementation
    # Board and micros conductivity
    board_conductivity = simple_conductivity(cpu_specification.board, simulation_specification)
    micro_conductivity = simple_conductivity(cpu_specification.cpu_core, simulation_specification)

    # Number of places for all CPUs
    p_micros = micro_conductivity.p * cpu_specification.number_of_cores

    # Create pre, post and lambda from the system with board and number of CPUs
    r_pre = micro_conductivity.p + cpu_specification.number_of_cores * micro_conductivity.p
    c_pre = micro_conductivity.t + cpu_specification.number_of_cores * micro_conductivity.t

    pre_sis = np.zeros((r_pre, c_pre))
    pre_sis[0:board_conductivity.p, 0:board_conductivity.t] = board_conductivity.pre

    post_sis = np.zeros((r_pre, c_pre))
    post_sis[0:board_conductivity.p, 0:board_conductivity.t] = board_conductivity.post

    lambda_vector = np.zeros((c_pre, 1))
    lambda_vector[0:board_conductivity.t, 0] = board_conductivity.lambda_vector

    for i in range(1, cpu_specification.number_of_cores + 1):
        r_in = board_conductivity.p + micro_conductivity.p * (i - 1)
        r_fin = board_conductivity.p + micro_conductivity.p * i

        c_in = board_conductivity.t + micro_conductivity.t * (i - 1)
        c_fin = board_conductivity.t + micro_conductivity.t * i

        pre_sis[r_in: r_fin, c_in: c_fin] = micro_conductivity.pre
        post_sis[r_in: r_fin, c_in: c_fin] = micro_conductivity.post

        lambda_vector[c_in:c_fin, 0] = micro_conductivity.lambda_vector

    # Add transitions between micro and board

    # Connections between micro places and board places
    rel_micro = np.zeros(p_micros)

    coordinates = cpu_specification.coordinates(simulation_specification)

    for i in range(1, cpu_specification.number_of_cores + 1):
        rel_micro[(i - 1) * micro_conductivity.p: i * micro_conductivity.p] = coordinates[i - 1]

    add_interactions_layer(rel_micro, pre_sis, post_sis, lambda_vector, board_conductivity, micro_conductivity,
                           cpu_specification, simulation_specification)

    # Convection
    diagonal = np.zeros((r_pre, 1))
    add_convection(diagonal, rel_micro, pre_sis, post_sis, lambda_vector, board_conductivity, micro_conductivity,
                   cpu_specification, simulation_specification)

    # Heat generation
    cp_exec = np.zeros((r_pre, cpu_specification.number_of_cores * len(
        tasks_specification.tasks)))
    lambda_generated = np.zeros(
        (cpu_specification.number_of_cores * len(tasks_specification.tasks)))

    add_heat(cp_exec, lambda_generated, pre_sis, post_sis, lambda_vector, board_conductivity, micro_conductivity,
             cpu_specification, simulation_specification)

    lambda_vector = [lambda_vector,
                     lambda_generated]  # TODO: Check if this assignation is the same as Lambda =[Lambda;Lambda_gen']

    # Lineal system
    pi = pre_sis.copy()
    a = (((post_sis - pre_sis).dot(lambda_vector)).dot(pi))

    # Output places
    l_measurement = np.zeros(cpu_specification.number_of_cores)

    for i in range(0, cpu_specification.number_of_cores):
        l_measurement[i] = board_conductivity.p + i * micro_conductivity.p + np.math.ceil(micro_conductivity.p / 2)

    c = np.zeros((len(l_measurement), len(a)))  # TODO: Check if is correct

    for i in range(0, len(l_measurement)):
        c[i, l_measurement[i]] = 1

    return ThermalModel(a, cp_exec, c, diagonal, lambda_generated)
