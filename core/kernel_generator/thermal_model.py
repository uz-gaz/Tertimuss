import numpy as np

from core.problem_specification_models.CpuSpecification import CpuSpecification, MaterialCuboid, Origin
from core.problem_specification_models.EnvironmentSpecification import EnvironmentSpecification
from core.problem_specification_models.SimulationSpecification import SimulationSpecification
from core.problem_specification_models.TasksSpecification import TasksSpecification


class ConductivityModel(object):
    def __init__(self, pre: np.ndarray, post: np.ndarray, t: int, p: int, lambda_vector: np.ndarray):
        self.pre = pre
        self.post = post
        self.t = t
        self.p = p
        self.lambda_vector = lambda_vector


def simple_conductivity(material_cuboid: MaterialCuboid,
                        simulation_specification: SimulationSpecification) -> ConductivityModel:
    dx = simulation_specification.step / 1000
    dy = simulation_specification.step / 1000
    dz = material_cuboid.z / 1000

    x: int = int(material_cuboid.x / simulation_specification.step)
    y: int = int(material_cuboid.y / simulation_specification.step)

    rho: float = material_cuboid.p
    k: float = material_cuboid.k
    cp: float = material_cuboid.c_p

    volume: float = dx * dy * dz  # Volumen de cada cuadrado, igual para todos los elementos
    horizontal_area: float = dy * dz  # Area de contacto para lugares contiguos horizontales
    vertical_area: float = dx * dz  # Area de contacto para lugares contiguos verticales

    dx_horizontal = dx / 2
    dx_vertical = dy / 2

    horizontal_lambda = (1 / (volume * rho * cp)) * (k * k * horizontal_area) / (k * dx_horizontal + k * dx_horizontal)
    vertical_lambda = (1 / (volume * rho * cp)) * (k * k * vertical_area) / (k * dx_vertical + k * dx_vertical)

    # Total de lugares de la RP
    p: int = x * y

    # Total de transiciones
    t: int = 4 * p - 2 * (x + y)  # Original = (x * y * 4) - 8 - 2 * (x - 2) - 2 * (y - 2)

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

    lambda_vector = np.zeros(t)

    for i in range(1, p):
        j = 1 + ((i - 1) * 2)
        pre[i - 1:i + 1, j - 1:j + 1] = i_pre
        post[i - 1:i + 1, j - 1:j + 1] = i_post

        if i % x == 0:
            lambda_vector[j - 1: j + 1] = [vertical_lambda, vertical_lambda]
        else:
            lambda_vector[j - 1:  j + 1] = [horizontal_lambda, horizontal_lambda]

    # Para la siguiente parte de C se numeran las transiciones que
    # conectan 1-6, 2-5, 4-9 y 5-8 (ie. t18 y t17 asociadas a 1-6)
    v_pre = [1, 0]
    v_post = [0, 1]

    start = 1
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


def add_interactions_layer(rel_micro: np.ndarray, pre_sis: np.ndarray, post_sis: np.ndarray, lambda_vector: np.ndarray,
                           board_conductivity: ConductivityModel, cpu_specification: CpuSpecification,
                           simulation_specification: SimulationSpecification) -> [np.ndarray, np.ndarray, np.ndarray]:
    # Return: Pre,Post,lambda
    # TODO: REVISAR V2
    dx_p1 = simulation_specification.step  # cpu_specification.cpu_core.x
    dy_p1 = simulation_specification.step  # cpu_specification.cpu_core.y
    dz_p1 = cpu_specification.cpu_core.z

    rho_p1 = cpu_specification.cpu_core.p
    k_p1 = cpu_specification.cpu_core.k
    cp_p1 = cpu_specification.cpu_core.c_p

    dx_p2 = simulation_specification.step  # cpu_specification.board.x
    dy_p2 = simulation_specification.step  # cpu_specification.board.y
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
        pre_sis[i + board_conductivity.p, j - 1: j + 1] = v_post

        post_sis[rel_micro[i - 1], j - 1, j + 1] = [0, lambda1 / lambda2]
        post_sis[i + board_conductivity.p, j - 1: j + 1] = [lambda2 / lambda1, 0]

        lambda_vector[j - 1, j + 1] = [lambda1, lambda2]
        j = j + 2

    return pre_sis, post_sis, lambda_vector


def add_convection(rel_micro, pre_sis, post_sis, lambda_vector, board_conductivity: ConductivityModel,
                   micro_conductivity: ConductivityModel, cpu_specification: CpuSpecification,
                   simulation_specification: SimulationSpecification,
                   environment_specification: EnvironmentSpecification) -> [np.ndarray, np.ndarray, np.ndarray,
                                                                            np.ndarray]:
    # D,Pre,Post,Lambda
    # TODO: REVISAR
    dx_p1 = simulation_specification.step  # cpu_specification.cpu_core.x
    dy_p1 = simulation_specification.step  # cpu_specification.cpu_core.y
    dz_p1 = cpu_specification.cpu_core.z

    rho_p1 = cpu_specification.cpu_core.p
    k_p1 = cpu_specification.cpu_core.k
    cp_p1 = cpu_specification.cpu_core.c_p

    h = environment_specification.h

    dx_p2 = simulation_specification.step  # cpu_specification.board.x
    dy_p2 = simulation_specification.step  # cpu_specification.board.y
    dz_p2 = cpu_specification.board.z  # TODO: Seguramente el valor sea entre cpu specification

    rho_p2 = cpu_specification.board.p
    k_p2 = cpu_specification.board.k
    cp_p2 = cpu_specification.board.c_p

    lambda_1 = (h / (dz_p1 * rho_p1 * cp_p1))
    lambda_2 = (h / (dz_p2 * rho_p2 * cp_p2))

    lambda_conv = [lambda_1, lambda_2]

    l_lug = len(rel_micro)

    # vector con el numero de lugares expuestos a temp. ambiente
    places = range(1, board_conductivity.p + 1)  # TODO: Revisar

    # Eliminamos los lugares bajo la CPU

    len_pre = len(pre_sis)
    f = len(pre_sis[0])

    j = len_pre + 1
    l_places = len(places)  # TODO: Revisar, debería de ser board_conductivity.p

    cota_micros = l_places - micro_conductivity.p

    pre_conv = np.zeros((f, 2))

    post_conv = np.zeros((f, 2))  # TODO: Comprobar

    k = 1

    for i in range(1, l_places):
        pre_sis[places[i - 1] - 1, j - 1] = 1
        pre_conv[places[i - 1] - 1, k - 1] = 0

        post_sis[places[i - 1] - 1, j - 1] = 0
        post_conv[places[i - 1] - 1, k - 1] = 1

        if i > cota_micros:
            k = k + 1

        lambda_vector[j - 1] = lambda_1
        j = j + 1

    pi = [1, 1]

    return post_conv.dot(np.diag(lambda_conv)).dot(
        pi), pre_sis, post_conv, lambda_vector


def add_heat(pre_sis, post_sis, board_conductivity: ConductivityModel,
             micro_conductivity: ConductivityModel, cpu_specification: CpuSpecification,
             task_specification: TasksSpecification, simulation_specification: SimulationSpecification) \
        -> [np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    # Cp_exec,Lambda_gen, Pre,Post
    # TODO:
    dx = simulation_specification.step  # cpu_specification.cpu_core.x
    dy = simulation_specification.step  # cpu_specification.cpu_core.y
    dz = cpu_specification.cpu_core.z  # TODO: Seguramente el valor sea entre cpu specification

    x = cpu_specification.cpu_core.x
    y = cpu_specification.cpu_core.y
    z = cpu_specification.cpu_core.z

    rho = cpu_specification.cpu_core.p
    cp = cpu_specification.cpu_core.c_p

    v_d = dx * dy * dz
    v_cpu = x * y * z

    cte = 5e8 / len(task_specification.tasks)  # constante para compensar (amerita revision)

    # Lambdas
    # Como la generacion es igual para cada lugar del procesador las lambdas
    # son iguales para todos los lugares de un mismo procesador
    lambda_gen = np.ones((1, len(task_specification.tasks) * cpu_specification.number_of_cores))

    for j in range(1, cpu_specification.number_of_cores + 1):
        for i in range(1, len(task_specification.tasks) + 1):
            lambda_gen[i - 1] = cpu_specification.clock_frequency
            # TODO: Cambiar Actualmente estoy suponiendo frecuencia uniforme
            # Pero en el codigo original a cada lugar se le asigna la frecuencia de cada
            # procesador Lambda_gen(i)=F(j);

    places_proc = list(range(board_conductivity.p + 1, board_conductivity.p * micro_conductivity.p + 1))

    l_places = len(places_proc)

    len_pre = len(pre_sis)
    f = len(pre_sis[0])

    pre_gen = np.zeros((f, len(task_specification.tasks) * cpu_specification.number_of_cores))
    post_gen = np.zeros((f, len(task_specification.tasks) * cpu_specification.number_of_cores))

    j = 1

    for i in range(1, l_places + 1):
        for k in range(0, len(task_specification.tasks)):
            post_gen[places_proc[i] - 1, j + k - 1] = (1 / (v_cpu * rho * cp * task_specification.tasks[k].e))

        if i % micro_conductivity.p == 0:
            j = j + len(task_specification.tasks)

    pre_sis = [pre_sis, pre_gen]
    post_sis = [post_sis, post_gen]

    cp_exec = post_gen.dot(np.diag(lambda_gen))

    return cp_exec, lambda_gen, pre_sis, post_sis


def getCpuCoordinates(origin: Origin, cpu_spec: MaterialCuboid, board_spec: MaterialCuboid,
                      simulation_specification: SimulationSpecification) -> list:
    x = cpu_spec.x // simulation_specification.step
    y = cpu_spec.y // simulation_specification.step

    x_0: int = round(origin.x / simulation_specification.step)
    y_0: int = round(origin.y / simulation_specification.step)

    x_1: int = x_0 + x
    y_1: int = y_0 + y

    lugares = np.zeros(x * y)

    x_placa = board_spec.x // simulation_specification.step

    count = 1
    for j in range(y_0, y_1):
        for i in range(x_0, x_1):
            if j % 2 == 0:
                lugares[count - 1] = j * x_placa - (i - 1)
            else:
                lugares[count - 1] = (j - 1) * x_placa + i

            count = count + 1

        if j % 2 == 1:
            # TODO: Revisar que se pretende hacer y corregirlo
            aux = np.flip(lugares[count - x - 1: count - 1])
            lugares = lugares[0: count - x - 1] + aux

    return lugares


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
    r_pre = board_conductivity.p + p_micros
    c_pre = board_conductivity.t + cpu_specification.number_of_cores * micro_conductivity.t

    pre_sis: np.ndarray = np.zeros((r_pre, c_pre))
    pre_sis[0:board_conductivity.p, 0:board_conductivity.t] = board_conductivity.pre

    post_sis: np.ndarray = np.zeros((r_pre, c_pre))
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

    coordinates = cpu_specification.cpu_origins

    for i in range(1, cpu_specification.number_of_cores + 1):
        rel_micro[(i - 1) * micro_conductivity.p: i * micro_conductivity.p] = getCpuCoordinates(coordinates[i - 1],
                                                                                                cpu_specification.cpu_core,
                                                                                                cpu_specification.board,
                                                                                                simulation_specification)

    # Pre,Post,lambda
    pre_sis, post_sis, lambda_vector = add_interactions_layer(rel_micro, pre_sis, post_sis, lambda_vector,
                                                              board_conductivity, cpu_specification,
                                                              simulation_specification)

    # Convection
    # diagonal = np.zeros((r_pre, 1))
    diagonal, pre_sis, post_sis, lambda_vector = add_convection(rel_micro, pre_sis, post_sis, lambda_vector,
                                                                board_conductivity, micro_conductivity,
                                                                cpu_specification, simulation_specification,
                                                                environment_specification)

    # Heat generation
    cp_exec, lambda_generated, pre_sis, post_sis = add_heat(pre_sis, post_sis, board_conductivity, micro_conductivity,
                                                            cpu_specification, tasks_specification,
                                                            simulation_specification)

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
