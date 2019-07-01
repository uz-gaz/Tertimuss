import functools
import operator
from typing import Optional
import scipy.optimize
import scipy
import scipy.linalg

from core.kernel_generator.global_model import GlobalModel
from core.kernel_generator.thermal_model import ThermalModel
from core.problem_specification_models.CpuSpecification import CpuSpecification
from core.problem_specification_models.EnvironmentSpecification import EnvironmentSpecification
from core.problem_specification_models.SimulationSpecification import SimulationSpecification
from core.problem_specification_models.TasksSpecification import TasksSpecification


def solve_lineal_programing_problem_for_scheduling(tasks_specification: TasksSpecification,
                                                   cpu_specification: CpuSpecification,
                                                   environment_specification: EnvironmentSpecification,
                                                   simulation_specification: SimulationSpecification,
                                                   global_model: Optional[GlobalModel]) -> [scipy.ndarray,
                                                                                            scipy.ndarray, float,
                                                                                            scipy.ndarray]:
    h = tasks_specification.h
    ti = scipy.asarray([i.t for i in tasks_specification.tasks])
    ia = h / ti
    n = len(tasks_specification.tasks)
    m = cpu_specification.number_of_cores

    # Inequality constraint
    # Create matrix diag([cc1/H ... ccn/H cc1/H .....]) of n*m

    ch_vector = scipy.asarray(m * [i.c for i in tasks_specification.tasks]) / h
    c_h = scipy.diag(ch_vector)

    a_eq = scipy.tile(scipy.eye(n), m)

    au = scipy.linalg.block_diag(*(m * [[i.c for i in tasks_specification.tasks]])) / h

    beq = scipy.transpose(ia)
    bu = scipy.ones((m, 1))

    # Variable bounds
    bounds = (n * m) * [(0, None)]

    # Objective function
    objective = scipy.ones(n * m)

    # Optimization
    if global_model.enable_thermal_mode:
        a_t = global_model.a_t

        b = global_model.ct_exec

        s_t = global_model.selector_of_core_temperature

        b_ta = global_model.b_ta

        # Fixme: Check why a_t can't be inverted
        a_int = - ((s_t.dot(scipy.linalg.inv(a_t))).dot(b)).dot(c_h)

        b_int = environment_specification.t_max * scipy.ones((m, 1)) + (
            (s_t.dot(scipy.linalg.inv(a_t))).dot(
                b_ta.reshape((-1, 1)))) * environment_specification.t_env

        a = scipy.concatenate((a_int, au))
        b = scipy.concatenate((b_int.transpose(), bu.transpose()), axis=1)
    else:
        a = au
        b = bu

    # res = scipy.optimize.linprog(c=objetive, A_ub=a, b_ub=b, A_eq=a_eq,
    #                              b_eq=beq, bounds=bounds, method='interior-point')
    # Interior points was the default in the original version, but i found that simplex has better results
    res = scipy.optimize.linprog(c=objective, A_ub=a, b_ub=b, A_eq=a_eq,
                                 b_eq=beq, bounds=bounds, method='simplex')  # FIXME: Answer original authors

    if not res.success:
        # No solution found
        raise Exception("Error: No solution found when trying to solve the lineal programing problem")

    j_b_i = res.x

    j_fsc_i = j_b_i * ch_vector

    w_alloc = j_fsc_i

    # Quantum calc
    sd = scipy.union1d(functools.reduce(operator.add, [list(range(ti[i], h + 1, ti[i])) for i in range(n)], []), 0)

    round_factor = 4  # Fixme: Check if higher round factor can be applied
    fraction_denominator = 10 ** round_factor

    rounded_list = functools.reduce(operator.add,
                                    [(sd[i] * j_fsc_i * fraction_denominator).tolist() for i in range(1, len(sd) - 1)])
    rounded_list = [int(i) for i in rounded_list]

    quantum = scipy.gcd.reduce(rounded_list) / fraction_denominator

    if quantum < simulation_specification.dt:
        quantum = simulation_specification.dt

    if global_model.enable_thermal_mode:
        # Solve differential equation to get a initial condition
        theta = scipy.linalg.expm(global_model.a_t * h)

        beta_1 = (scipy.linalg.inv(global_model.a_t)).dot(
            theta - scipy.identity(len(global_model.a_t)))
        beta_2 = beta_1.dot(global_model.b_ta.reshape((- 1, 1)))
        beta_1 = beta_1.dot(global_model.ct_exec)

        # Set initial condition to zero to archive a final condition where initial = final, SmT(0) = Y(H)
        m_t_o = scipy.zeros((len(global_model.a_t), 1))
        m_t = theta.dot(m_t_o) + beta_1.dot(
            w_alloc.reshape((len(w_alloc), 1))) + beta_2 * environment_specification.t_env

        w_alloc_max = j_fsc_i / quantum
        m_t_max = theta.dot(m_t_o) + beta_1.dot(
            w_alloc_max.reshape((len(w_alloc_max), 1))) + environment_specification.t_env * beta_2
        temp_max = global_model.s_t.dot(m_t_max)

        if all(item[0] > environment_specification.t_max for item in temp_max / m):
            raise Exception(
                "Error: No one solution found when trying to solve the linear programing problem is feasible")
    else:
        m_t = None

    return j_b_i, j_fsc_i, quantum, m_t
