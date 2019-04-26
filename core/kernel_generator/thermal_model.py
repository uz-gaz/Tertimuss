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
    """

    :param material_cuboid: Board or CPU
    :param simulation_specification: Specification
    :return: Model
    """
    dx = simulation_specification.step / 1000
    dy = simulation_specification.step / 1000

    x: int = int(material_cuboid.x / simulation_specification.step)
    y: int = int(material_cuboid.y / simulation_specification.step)

    rho: float = material_cuboid.p
    k: float = material_cuboid.k
    cp: float = material_cuboid.c_p

    # Horizontal lambda and vertical lambda was refactored to achieve more precision
    horizontal_lambda = k / (rho * cp * (dx ** 2))
    vertical_lambda = k / (rho * cp * (dy ** 2))

    # Total number of PN places
    p: int = x * y

    # Total number of transitions
    t: int = 4 * p - 2 * (x + y)

    # C incidence matrix
    i_pre = [[1, 0], [0, 1]]
    i_post = [[0, 1], [1, 0]]

    # The places have been named in snake form
    # ie. 1 2 3
    #     6 5 4
    #     7 8 9 [...]
    # That is the way to create the incidence matrix with the transitions who connects
    # 1-2 (both), 2-3 [...], 8-9 until the transition t=[(x*2)*(y-1)] + (x-1)*2
    pre = scipy.zeros((p, t))
    post = scipy.zeros((p, t))

    lambda_vector = scipy.zeros(t)

    # FIXME: I think we achieve the same in pre if we create a diagonal matrix with [1, 0] p -2 times and [0, 1]
    # in the last
    for i in range(p - 1):
        j = i * 2
        pre[i:i + 2, j:j + 2] = i_pre
        post[i:i + 2, j:j + 2] = i_post

        lambda_vector[j: j + 2] = [vertical_lambda, vertical_lambda] if (i + 1) % x == 0 else [horizontal_lambda,
                                                                                               horizontal_lambda]

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

            lambda_vector[j: j + 2] = [vertical_lambda, vertical_lambda]

            i = i - 1
            j = j + 2
            u = u + 1

    return ConductivityModel(pre, post, t, p, lambda_vector)


def add_interactions_layer(rel_micro: scipy.ndarray, pre_sis: scipy.ndarray, post_sis: scipy.ndarray,
                           lambda_vector: scipy.ndarray,
                           board_conductivity: ConductivityModel, cpu_specification: CpuSpecification) -> \
        [scipy.ndarray, scipy.ndarray, scipy.ndarray]:
    rho_p1 = cpu_specification.board.p
    k_p1 = cpu_specification.board.k
    cp_p1 = cpu_specification.board.c_p

    rho_p2 = cpu_specification.cpu_core.p
    k_p2 = cpu_specification.cpu_core.k
    cp_p2 = cpu_specification.cpu_core.c_p

    # Refactored to improve precision
    lambda1 = (k_p1 * k_p2 / (cpu_specification.board.z * rho_p1 * cp_p1 * (
            k_p2 * cpu_specification.board.z + k_p1 * cpu_specification.cpu_core.z))) * (2 * (1000 ** 2))

    lambda2 = (k_p1 * k_p2 / (cpu_specification.cpu_core.z * rho_p2 * cp_p2 * (
            k_p2 * cpu_specification.board.z + k_p1 * cpu_specification.cpu_core.z))) * (2 * (1000 ** 2))

    lambda1_div_lambda2 = (cpu_specification.cpu_core.z * rho_p2 * cp_p2) / (cpu_specification.board.z * rho_p1 * cp_p1)
    lambda2_div_lambda1 = (cpu_specification.board.z * rho_p1 * cp_p1) / (cpu_specification.cpu_core.z * rho_p2 * cp_p2)

    l_lug = len(rel_micro)

    v_pre = [1, 0]
    v_post = [0, 1]

    pre_int = scipy.zeros((len(pre_sis), 2 * l_lug))
    post_int = scipy.zeros((len(post_sis), 2 * l_lug))

    lambda_int = scipy.zeros((2 * l_lug, 1))

    for i in range(l_lug):
        j = i * 2
        pre_int[rel_micro[i] - 1, j: j + 2] = v_pre
        pre_int[i + board_conductivity.p, j: j + 2] = v_post

        post_int[rel_micro[i] - 1, j: j + 2] = [0, lambda1_div_lambda2]
        post_int[i + board_conductivity.p, j: j + 2] = [lambda2_div_lambda1, 0]

        lambda_int[j: j + 2, 0] = [lambda1, lambda2]

    pre_sis = scipy.concatenate((pre_sis, pre_int), axis=1)
    post_sis = scipy.concatenate((post_sis, post_int), axis=1)

    lambda_vector = scipy.concatenate((lambda_vector, lambda_int))

    return pre_sis, post_sis, lambda_vector


def add_convection(pre_sis, post_sis, lambda_vector, board_conductivity: ConductivityModel,
                   micro_conductivity: ConductivityModel, cpu_specification: CpuSpecification,
                   environment_specification: EnvironmentSpecification) -> [scipy.ndarray, scipy.ndarray, scipy.ndarray,
                                                                            scipy.ndarray]:
    rho_p1 = cpu_specification.board.p
    cp_p1 = cpu_specification.board.c_p

    h = environment_specification.h

    lambda_1 = (h / (cpu_specification.board.z * rho_p1 * cp_p1)) * 1000

    lambda_convection = [lambda_1, lambda_1]  # TODO: Check, it might be lambda1, lambda2 (Ask authors)

    p_micros = micro_conductivity.p * cpu_specification.number_of_cores

    # Number of places exposed at environment temperature
    l_places = board_conductivity.p

    # Places under CPU
    f = len(pre_sis)

    cota_micros = l_places - p_micros

    post_convection = scipy.zeros((f, 2))

    pre_it = scipy.zeros((f, l_places))
    post_it = scipy.zeros((f, l_places))

    lambda_it = scipy.zeros((l_places, 1))

    k = 0
    for i in range(l_places):
        pre_it[i, i] = 1

        post_it[i, i] = 0
        post_convection[i, k] = 1

        lambda_it[i] = lambda_1

        if i + 1 == cota_micros:
            k = k + 1

    pi = [1, 1]

    pre_sis = scipy.concatenate((pre_sis, pre_it), axis=1)
    post_sis = scipy.concatenate((post_sis, post_it), axis=1)

    lambda_vector = scipy.concatenate((lambda_vector, lambda_it))

    return post_convection.dot(scipy.diag(lambda_convection)).dot(
        pi), pre_sis, post_sis, lambda_vector


def add_heat(pre_sis, post_sis, board_conductivity: ConductivityModel,
             micro_conductivity: ConductivityModel, cpu_specification: CpuSpecification,
             task_specification: TasksSpecification) \
        -> [scipy.ndarray, scipy.ndarray, scipy.ndarray, scipy.ndarray]:
    rho = cpu_specification.cpu_core.p
    cp = cpu_specification.cpu_core.c_p

    # The generation is equal for each place in the same processor so lambdas are equal too
    lambda_gen = scipy.ones(len(task_specification.tasks) * cpu_specification.number_of_cores)

    for j in range(cpu_specification.number_of_cores):
        for i in range(len(task_specification.tasks)):
            lambda_gen[i] = cpu_specification.clock_frequency
            # FIXME: Cambiar Actualmente estoy suponiendo frecuencia uniforme
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
    for i in range(l_places):
        for k in range(len(task_specification.tasks)):
            post_gen[places_proc[i] - 1, j + k - 1] = (task_specification.tasks[k].e / (rho * cp)) * ((1000 ** 3) / (
                    cpu_specification.cpu_core.x * cpu_specification.cpu_core.y * cpu_specification.cpu_core.z))

        if (i + 1) % micro_conductivity.p == 0:
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

    for i in range(cpu_specification.number_of_cores):
        r_in = board_conductivity.p + micro_conductivity.p * i
        r_fin = board_conductivity.p + micro_conductivity.p * (i + 1)

        c_in = board_conductivity.t + micro_conductivity.t * i
        c_fin = board_conductivity.t + micro_conductivity.t * (i + 1)

        pre_sis[r_in: r_fin, c_in: c_fin] = micro_conductivity.pre
        post_sis[r_in: r_fin, c_in: c_fin] = micro_conductivity.post

        lambda_vector[c_in:c_fin, 0] = micro_conductivity.lambda_vector

    # Add transitions between micro and board
    # Connections between micro places and board places
    rel_micro = scipy.zeros(p_micros, dtype=int)

    for i in range(cpu_specification.number_of_cores):
        rel_micro[i * micro_conductivity.p: (i + 1) * micro_conductivity.p] = getCpuCoordinates(
            cpu_specification.cpu_origins[i],
            cpu_specification.cpu_core,
            cpu_specification.board,
            simulation_specification)

    # Pre,Post,lambda
    pre_sis, post_sis, lambda_vector = add_interactions_layer(rel_micro, pre_sis, post_sis, lambda_vector,
                                                              board_conductivity, cpu_specification)

    # Convection
    diagonal, pre_sis, post_sis, lambda_vector = add_convection(pre_sis, post_sis, lambda_vector,
                                                                board_conductivity, micro_conductivity,
                                                                cpu_specification, environment_specification)

    # Heat generation
    cp_exec, lambda_generated, pre_sis, post_sis = add_heat(pre_sis, post_sis, board_conductivity, micro_conductivity,
                                                            cpu_specification, tasks_specification)

    lambda_vector = scipy.concatenate((lambda_vector, lambda_generated.reshape((-1, 1))))

    # Lineal system
    pi = pre_sis.transpose()
    a = ((post_sis - pre_sis).dot(scipy.diag(lambda_vector.reshape(-1)))).dot(pi)

    # Output places
    l_measurement = scipy.zeros(cpu_specification.number_of_cores)

    for i in range(cpu_specification.number_of_cores):
        l_measurement[i] = board_conductivity.p + i * micro_conductivity.p + scipy.math.ceil(micro_conductivity.p / 2)

    c = scipy.zeros((len(l_measurement), len(a)))

    for i in range(len(l_measurement)):
        c[i, int(l_measurement[i]) - 1] = 1

    return ThermalModel(a, cp_exec, c, diagonal, lambda_generated)
