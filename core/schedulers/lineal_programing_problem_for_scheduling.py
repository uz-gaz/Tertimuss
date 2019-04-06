import scipy.optimize

import scipy

from core.kernel_generator.thermal_model import ThermalModel
from core.problem_specification_models.CpuSpecification import CpuSpecification
from core.problem_specification_models.EnvironmentSpecification import EnvironmentSpecification
from core.problem_specification_models.SimulationSpecification import SimulationSpecification
from core.problem_specification_models.TasksSpecification import TasksSpecification


def solve_lineal_programing_problem_for_scheduling(tasks_specification: TasksSpecification,
                                                   cpu_specification: CpuSpecification,
                                                   environment_specification: EnvironmentSpecification,
                                                   simulation_specification: SimulationSpecification,
                                                   thermal_model: ThermalModel) -> [scipy.ndarray, scipy.ndarray, float,
                                                                                    scipy.ndarray]:
    h = tasks_specification.h
    ti = scipy.asarray(list(map(lambda task: task.t, tasks_specification.tasks)))
    cci = scipy.asarray(list(map(lambda task: task.c, tasks_specification.tasks)))
    ia = h / ti
    n = len(tasks_specification.tasks)
    m = cpu_specification.number_of_cores

    # Inequality constraint
    # Create matrix diag([cc1/H ... ccn/H cc1/H .....]) of n*m
    ch_vector = scipy.asarray(m * list(cci)) / h
    c_h = scipy.diag(ch_vector)

    a_t = thermal_model.a_t

    b = thermal_model.ct_exec

    a_int = - ((thermal_model.s_t.dot(scipy.linalg.inv(a_t))).dot(b)).dot(c_h)  # Fixme: Problem in inverse precision
    b_int = environment_specification.t_max * scipy.ones((m, 1)) + (
        (thermal_model.s_t.dot(scipy.linalg.inv(thermal_model.a_t))).dot(
            thermal_model.b_ta.reshape((-1, 1)))) * environment_specification.t_env

    au = scipy.zeros((m, m * n))

    a_eq = scipy.tile(scipy.eye(n), m)

    for j in range(m):
        au[j, j * n:(j + 1) * n] = scipy.asarray(list(cci)) / h

    beq = scipy.transpose(ia)
    bu = scipy.ones((m, 1))

    # Variable bounds
    bounds = (n * m) * [(0, None)]

    # Objective function
    objetive = scipy.ones(n * m)

    # Optimization
    a = scipy.concatenate((a_int, au))
    b = scipy.concatenate((b_int.transpose(), bu.transpose()), axis=1)

    res = scipy.optimize.linprog(c=objetive, A_ub=a, b_ub=b, A_eq=a_eq,
                                 b_eq=beq, bounds=bounds, method='interior-point')

    if not res.success:
        # No solution found
        print("No solution")
        # TODO: Return error or throw exception
        return None

    jBi = res.x

    jFSCi = jBi * ch_vector

    walloc = jFSCi

    # Solve differential equation to get a initial condition
    theta = scipy.linalg.expm(thermal_model.a_t * h)

    beta_1 = (scipy.linalg.inv(thermal_model.a_t)).dot(
        theta - scipy.identity(len(thermal_model.a_t)))
    beta_2 = beta_1.dot(thermal_model.b_ta.reshape((- 1, 1)))
    beta_1 = beta_1.dot(thermal_model.ct_exec)

    # Inicializa la condicion inicial en ceros para obtener una condicion inicial=final SmT(0)=Y(H)
    mT0 = scipy.zeros((len(thermal_model.a_t), 1))
    mT = theta.dot(mT0) + beta_1.dot(walloc.reshape((len(walloc), 1))) + beta_2 * environment_specification.t_env
    temp = thermal_model.s_t.dot(mT)

    # Quantum calc
    jobs = ia
    diagonal = scipy.zeros((len(tasks_specification.tasks), int(jobs.max())))

    for i in range(0, len(tasks_specification.tasks)):
        diagonal[i, 0: int(jobs[i])] = list(range(ti[i], h + 1, ti[i]))

    sd = diagonal[0, 0:int(jobs[0])]

    for i in range(2, n + 1):
        sd = scipy.union1d(sd, diagonal[i - 1, 0:int(jobs[i - 1])])

    sd = scipy.union1d(sd, 0)

    quantum = 0.0

    round_factor = 1  # FIXME: 4 in original implementation
    fraction_denominator = 10 ** round_factor

    for i in range(2, len(sd)):
        not_round = scipy.concatenate(([quantum], sd[i - 1] * jFSCi))
        rounded = scipy.around(scipy.concatenate(([quantum], sd[i - 1] * jFSCi)), round_factor)
        rounded_as_fraction = list(map(lambda actual: int(actual * fraction_denominator), rounded))
        quantum = scipy.gcd.reduce(
            rounded_as_fraction) / fraction_denominator  # TODO: Review, jFSCi low precision -> quantum low precision

    if quantum < simulation_specification.dt:
        quantum = simulation_specification.dt

    # FIXME: Decimales a partir de aqui

    # Ver como en matlab se obtiene el gcd de floats
    walloc_Max = jFSCi / quantum
    mT_max = theta.dot(mT0) + beta_1.dot(
        walloc_Max.reshape((len(walloc_Max), 1))) + environment_specification.t_env * beta_2
    temp_max = thermal_model.s_t.dot(mT_max)

    if all(item[0] > environment_specification.t_max for item in temp_max / m):
        print("No solution...")
        # TODO: Return error or throw exception
        return None

    return jBi, jFSCi, quantum, mT
