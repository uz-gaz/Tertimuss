from core.problem_specification_models.CpuSpecification import CpuSpecification
from core.problem_specification_models.TasksSpecification import TasksSpecification
import numpy as np


class TasksModel(object):
    def __init__(self, c_tau, lambda_tau, pi_tau, c_tau_alloc, m_tau_o):
        self.c_tau = c_tau
        self.lambda_tau = lambda_tau
        self.pi_tau = pi_tau
        self.c_tau_alloc = c_tau_alloc
        self.m_tau_o = m_tau_o
        # TODO: Analyze if is necessary return Pre and Post matrix


def generate_tasks_model(tasks_specification: TasksSpecification, cpu_specification: CpuSpecification) -> TasksModel:
    n = len(tasks_specification.tasks)
    m = cpu_specification.number_of_cores

    # total of places of the TCPN
    p = 2 * n

    # Total of transitions
    t = n + n * m

    # n transitions of tasks period and n * m transitions alloc
    t_alloc = n * m

    # Incidence Matrix C
    pre = np.zeros((p, t))
    post = np.zeros((p, t))
    pre_alloc = np.zeros((p, t_alloc))
    post_alloc = np.zeros((p, t_alloc))
    lambda_vector = np.zeros(t)
    pi = np.zeros((t, p))
    mo = np.zeros((p, 1))

    k = 1

    # Construction of Pre an Post matrix for places(p^w_i,p^cc_i) and transition(t^w_i)
    for actual_task in tasks_specification.tasks:
        i = k * 2 - 1
        pre[i - 1, k - 1] = 1
        post[i - 1:i + 1, k - 1] = [1, actual_task.c]
        lambda_vector[k - 1] = 1 / actual_task.t
        pi[k - 1, i - 1] = 1
        mo[i - 1: i + 1, 0] = [1, actual_task.c]

        # Construction of Pre an Post matrix for Transitions alloc
        j = n + k
        while j <= t:
            pre[i, j - 1] = 1
            pi[j - 1, i] = 1
            j = j + n

        k = k + 1

    pre_alloc[:, 0: t_alloc] = pre[:, n: t]

    c = post - pre
    c_alloc = post_alloc - pre_alloc
    lambda_tau = np.diag(lambda_vector)

    return TasksModel(c, lambda_tau, pi, c_alloc, mo)
