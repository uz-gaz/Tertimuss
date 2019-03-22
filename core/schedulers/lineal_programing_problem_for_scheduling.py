import scipy.optimize

import numpy as np

from core.kernel_generator.thermal_model import ThermalModel
from core.problem_specification_models.CpuSpecification import CpuSpecification
from core.problem_specification_models.EnvironmentSpecification import EnvironmentSpecification
from core.problem_specification_models.SimulationSpecification import SimulationSpecification
from core.problem_specification_models.TasksSpecification import TasksSpecification


def solve_lineal_programing_problem_for_scheduling(tasks_specification: TasksSpecification,
                                                   cpu_specification: CpuSpecification,
                                                   environment_specification: EnvironmentSpecification,
                                                   simulation_specification: SimulationSpecification,
                                                   thermal_model: ThermalModel):
    # TODO: Implement function
    h = tasks_specification.h
    ti = np.asarray(list(map(lambda a: a.t, tasks_specification.tasks)))
    cci = np.asarray(list(map(lambda a: a.c, tasks_specification.tasks)))
    ia = h / ti
    n = len(tasks_specification.tasks)
    m = cpu_specification.number_of_cores

    # Inequality constraint
    # Create matrix diag([cc1/H ... ccn/H cc1/H .....]) of n*m
    ch_vector = np.asarray(m * list(map(lambda a: a.c / h, tasks_specification.tasks)))

    c_h = np.diag(ch_vector)

    a_int = - ((thermal_model.s_t.dot(np.linalg.inv(thermal_model.a_t))).dot(thermal_model.ct_exec)).dot(c_h)
    b_int = environment_specification.t_max * np.ones((m, 1)) + (
        (thermal_model.s_t.dot(np.linalg.inv(thermal_model.a_t))).dot(
            thermal_model.b_ta)) * environment_specification.t_env

    au = np.zeros((m, m * n))

    a_eq = np.tile(np.eye(n), m)

    for j in range(0, m):
        for i in range(0, n):
            au[j, i + 1 + (j - 1) * n] = tasks_specification.tasks[i].c / h

    beq = np.transpose(ia)
    bu = np.ones((m, 1))

    # Initial condition
    x0 = np.zeros((n * m, 1))

    # Variable bounds
    bounds = (n * m) * [(0, None)]

    # Objective function
    objetive = np.ones(n * m)

    # Optimization
    a = np.concatenate((a_int, au))
    b = np.concatenate((b_int, bu))

    scipy.optimize.linprog(c=objetive, A_ub=a, b_ub=b, A_eq=a_eq,
                           b_eq=beq, bounds=bounds, method='interior-point')

    pass
