import scipy

from core.problem_specification_models.CpuSpecification import CpuSpecification, MaterialCuboid, Origin
from core.problem_specification_models.EnvironmentSpecification import EnvironmentSpecification
from core.problem_specification_models.SimulationSpecification import SimulationSpecification
from core.problem_specification_models.TasksSpecification import TasksSpecification


class ConductivityModel(object):
    def __init__(self, pre: scipy.ndarray, post: scipy.ndarray, t: int, p: int, lambda_vector: scipy.ndarray):
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
    pre = scipy.zeros((p, t))
    post = scipy.zeros((p, t))

    lambda_vector = scipy.zeros(t)

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


def add_interactions_layer(rel_micro: scipy.ndarray, pre_sis: scipy.ndarray, post_sis: scipy.ndarray,
                           lambda_vector: scipy.ndarray,
                           board_conductivity: ConductivityModel, cpu_specification: CpuSpecification,
                           simulation_specification: SimulationSpecification) -> [scipy.ndarray, scipy.ndarray,
                                                                                  scipy.ndarray]:
    dx_p1 = simulation_specification.step / 1000
    dy_p1 = simulation_specification.step / 1000
    dz_p1 = cpu_specification.board.z / 1000

    rho_p1 = cpu_specification.board.p
    k_p1 = cpu_specification.board.k
    cp_p1 = cpu_specification.board.c_p

    dx_p2 = simulation_specification.step / 1000
    dy_p2 = simulation_specification.step / 1000
    dz_p2 = cpu_specification.cpu_core.z / 1000

    rho_p2 = cpu_specification.cpu_core.p
    k_p2 = cpu_specification.cpu_core.k
    cp_p2 = cpu_specification.cpu_core.c_p

    a = dx_p1 * dy_p1

    v_p1 = a * dz_p1
    deltax_p1 = dz_p1 / 2

    v_p2 = dx_p2 * dy_p2 * dz_p2
    deltax_p2 = dz_p2 / 2

    lambda1 = (k_p1 * k_p2 * a) / (v_p1 * rho_p1 * cp_p1) / (k_p2 * deltax_p1 + k_p1 * deltax_p2)
    lambda2 = (k_p1 * k_p2 * a) / (v_p2 * rho_p2 * cp_p2) / (k_p2 * deltax_p1 + k_p1 * deltax_p2)

    lambda1_div_lambda2 = (v_p2 * rho_p2 * cp_p2) / (v_p1 * rho_p1 * cp_p1)
    lambda2_div_lambda1 = (v_p1 * rho_p1 * cp_p1) / (v_p2 * rho_p2 * cp_p2)

    l_lug = len(rel_micro)

    v_pre = [1, 0]
    v_post = [0, 1]

    pre_int = scipy.zeros((len(pre_sis), 2 * l_lug))
    post_int = scipy.zeros((len(post_sis), 2 * l_lug))

    lambda_int = scipy.zeros((2 * l_lug, 1))

    j = 1
    for i in range(1, l_lug + 1):
        pre_int[rel_micro[i - 1] - 1, j - 1: j + 1] = v_pre
        pre_int[i + board_conductivity.p - 1, j - 1: j + 1] = v_post

        post_int[rel_micro[i - 1] - 1, j - 1: j + 1] = [0, lambda1_div_lambda2]
        post_int[i + board_conductivity.p - 1, j - 1: j + 1] = [lambda2_div_lambda1, 0]

        lambda_int[j - 1: j + 1, 0] = [lambda1, lambda2]
        j = j + 2

    pre_sis = scipy.concatenate((pre_sis, pre_int), axis=1)
    post_sis = scipy.concatenate((post_sis, post_int), axis=1)

    lambda_vector = scipy.concatenate((lambda_vector, lambda_int), axis=0)

    return pre_sis, post_sis, lambda_vector


def add_convection(pre_sis, post_sis, lambda_vector, board_conductivity: ConductivityModel,
                   micro_conductivity: ConductivityModel, cpu_specification: CpuSpecification,
                   environment_specification: EnvironmentSpecification) -> [scipy.ndarray, scipy.ndarray, scipy.ndarray,
                                                                            scipy.ndarray]:
    # D,Pre,Post,Lambda
    dz_p1 = cpu_specification.board.z / 1000

    rho_p1 = cpu_specification.board.p
    cp_p1 = cpu_specification.board.c_p

    dz_p2 = cpu_specification.cpu_core.z / 1000

    rho_p2 = cpu_specification.cpu_core.p
    cp_p2 = cpu_specification.cpu_core.c_p

    h = environment_specification.h

    lambda_1 = (h / (dz_p1 * rho_p1 * cp_p1))

    lambda_conv = [lambda_1, lambda_1]  # TODO: Check, it might be lambda1, lambda2 (Ask authors)

    p_micros = micro_conductivity.p * cpu_specification.number_of_cores

    # vector con el numero de lugares expuestos a temp. ambiente
    places = list(range(1, board_conductivity.p + 1))

    # Eliminamos los lugares bajo la CPU
    f = len(pre_sis)

    l_places = len(places)

    cota_micros = l_places - p_micros

    # pre_conv = scipy.zeros((f, 2)) # It was unused

    post_conv = scipy.zeros((f, 2))

    pre_it = scipy.zeros((f, l_places))
    post_it = scipy.zeros((f, l_places))

    lambda_it = scipy.zeros((l_places, 1))

    k = 1
    for i in range(1, l_places + 1):
        pre_it[places[i - 1] - 1, i - 1] = 1
        # pre_conv[places[i - 1] - 1, k - 1] = 0

        post_it[places[i - 1] - 1, i - 1] = 0
        post_conv[places[i - 1] - 1, k - 1] = 1

        if i == cota_micros:
            k = k + 1

        lambda_it[i - 1] = lambda_1

    pi = [1, 1]

    pre_sis = scipy.concatenate((pre_sis, pre_it), axis=1)
    post_sis = scipy.concatenate((post_sis, post_it), axis=1)

    lambda_vector = scipy.concatenate((lambda_vector, lambda_it), axis=0)

    return post_conv.dot(scipy.diag(lambda_conv)).dot(
        pi), pre_sis, post_sis, lambda_vector


def add_heat(pre_sis, post_sis, board_conductivity: ConductivityModel,
             micro_conductivity: ConductivityModel, cpu_specification: CpuSpecification,
             task_specification: TasksSpecification, simulation_specification: SimulationSpecification) \
        -> [scipy.ndarray, scipy.ndarray, scipy.ndarray, scipy.ndarray]:
    # Cp_exec,Lambda_gen, Pre,Post
    dx = simulation_specification.step / 1000
    dy = simulation_specification.step / 1000
    dz = cpu_specification.cpu_core.z / 1000

    x = cpu_specification.cpu_core.x / 1000
    y = cpu_specification.cpu_core.y / 1000
    z = cpu_specification.cpu_core.z / 1000

    rho = cpu_specification.cpu_core.p
    cp = cpu_specification.cpu_core.c_p

    v_cpu = x * y * z

    # Lambdas
    # Como la generacion es igual para cada lugar del procesador las lambdas
    # son iguales para todos los lugares de un mismo procesador
    lambda_gen = scipy.ones(len(task_specification.tasks) * cpu_specification.number_of_cores)

    for j in range(1, cpu_specification.number_of_cores + 1):
        for i in range(1, len(task_specification.tasks) + 1):
            lambda_gen[i - 1] = cpu_specification.clock_frequency
            # TODO: Cambiar Actualmente estoy suponiendo frecuencia uniforme
            # Por otro lado, se esta quedando siempre la frecuencia del ultimo procesador, el bucle no tiene sentido,
            # creo que debería de ser (i - 1) * (j - 1)
            # Pero en el codigo original a cada lugar se le asigna la frecuencia de cada
            # procesador Lambda_gen(i)=F(j);

    places_proc = list(range(board_conductivity.p + 1,
                             board_conductivity.p + cpu_specification.number_of_cores * micro_conductivity.p + 1))

    l_places = len(places_proc)

    f = len(pre_sis)

    pre_gen = scipy.zeros((f, len(task_specification.tasks) * cpu_specification.number_of_cores))
    post_gen = scipy.zeros((f, len(task_specification.tasks) * cpu_specification.number_of_cores))

    j = 1

    for i in range(1, l_places + 1):
        for k in range(0, len(task_specification.tasks)):
            post_gen[places_proc[i - 1] - 1, j + k - 1] = ((1 / (v_cpu * rho * cp)) * task_specification.tasks[k].e)

        if i % micro_conductivity.p == 0:
            j = j + len(task_specification.tasks)

    pre_sis = scipy.concatenate((pre_sis, pre_gen), axis=1)
    post_sis = scipy.concatenate((post_sis, post_gen), axis=1)

    cp_exec = post_gen.dot(scipy.diag(lambda_gen))

    return cp_exec, lambda_gen, pre_sis, post_sis


def getCpuCoordinates(origin: Origin, cpu_spec: MaterialCuboid, board_spec: MaterialCuboid,
                      simulation_specification: SimulationSpecification) -> list:
    x = cpu_spec.x // simulation_specification.step
    y = cpu_spec.y // simulation_specification.step

    x_0: int = round(origin.x / simulation_specification.step)
    y_0: int = round(origin.y / simulation_specification.step)

    x_1: int = x_0 + x
    y_1: int = y_0 + y

    places = []

    x_board = board_spec.x // simulation_specification.step

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
    def __init__(self, a_t: scipy.ndarray, ct_exec: scipy.ndarray, s_t: scipy.ndarray, b_ta: scipy.ndarray,
                 lambda_gen: scipy.ndarray):
        self.a_t = a_t
        self.ct_exec = ct_exec
        self.s_t = s_t
        self.b_ta = b_ta
        self.lambda_gen = lambda_gen


def generate_thermal_model(tasks_specification: TasksSpecification, cpu_specification: CpuSpecification,
                           environment_specification: EnvironmentSpecification,
                           simulation_specification: SimulationSpecification) -> ThermalModel:
    # Board and micros conductivity
    board_conductivity = simple_conductivity(cpu_specification.board, simulation_specification)
    micro_conductivity = simple_conductivity(cpu_specification.cpu_core, simulation_specification)

    # Number of places for all CPUs
    p_micros = micro_conductivity.p * cpu_specification.number_of_cores

    # Create pre, post and lambda from the system with board and number of CPUs
    r_pre = board_conductivity.p + p_micros
    c_pre = board_conductivity.t + cpu_specification.number_of_cores * micro_conductivity.t

    pre_sis: scipy.ndarray = scipy.zeros((r_pre, c_pre))
    pre_sis[0:board_conductivity.p, 0:board_conductivity.t] = board_conductivity.pre

    post_sis: scipy.ndarray = scipy.zeros((r_pre, c_pre))
    post_sis[0:board_conductivity.p, 0:board_conductivity.t] = board_conductivity.post

    lambda_vector = scipy.zeros((c_pre, 1))
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
    rel_micro = scipy.zeros(p_micros, dtype=int)

    for i in range(1, cpu_specification.number_of_cores + 1):
        rel_micro[(i - 1) * micro_conductivity.p: i * micro_conductivity.p] = getCpuCoordinates(
            cpu_specification.cpu_origins[i - 1],
            cpu_specification.cpu_core,
            cpu_specification.board,
            simulation_specification)

    # Pre,Post,lambda
    pre_sis, post_sis, lambda_vector = add_interactions_layer(rel_micro, pre_sis, post_sis, lambda_vector,
                                                              board_conductivity, cpu_specification,
                                                              simulation_specification)

    # Convection
    diagonal, pre_sis, post_sis, lambda_vector = add_convection(pre_sis, post_sis, lambda_vector,
                                                                board_conductivity, micro_conductivity,
                                                                cpu_specification, environment_specification)

    # Heat generation
    cp_exec, lambda_generated, pre_sis, post_sis = add_heat(pre_sis, post_sis, board_conductivity, micro_conductivity,
                                                            cpu_specification, tasks_specification,
                                                            simulation_specification)

    lambda_vector = scipy.concatenate((lambda_vector, lambda_generated.reshape((-1, 1))), axis=0)

    # Lineal system
    pi = pre_sis.transpose()
    a = ((post_sis - pre_sis).dot(scipy.diag(lambda_vector.reshape(-1)))).dot(
        pi)  # Access to lambda_vector.transpose())[0]) is the way to archive a diagonal matrix

    # Output places
    l_measurement = scipy.zeros(cpu_specification.number_of_cores)

    for i in range(0, cpu_specification.number_of_cores):
        l_measurement[i] = board_conductivity.p + i * micro_conductivity.p + scipy.math.ceil(micro_conductivity.p / 2)

    c = scipy.zeros((len(l_measurement), len(a)))

    for i in range(0, len(l_measurement)):
        c[i, int(l_measurement[i]) - 1] = 1

    # Fixme error accumulated in A_T
    return ThermalModel(a, cp_exec, c, diagonal, lambda_generated)
