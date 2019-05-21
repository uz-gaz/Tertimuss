import scipy

from core.problem_specification_models.CpuSpecification import CpuSpecification
from core.problem_specification_models.TasksSpecification import TasksSpecification


class TasksModel(object):
    """
        Represents the Task arrival and CPU'S Module in the paper
    """

    def __init__(self, c_tau: scipy.ndarray, lambda_tau: scipy.ndarray, pi_tau: scipy.ndarray,
                 c_tau_alloc: scipy.ndarray,
                 m_tau_o: scipy.ndarray, a_tau: scipy.ndarray):
        # TODO: Convert to SPARSE MATRIXES
        self.c_tau = c_tau
        self.lambda_tau = lambda_tau
        self.pi_tau = pi_tau
        self.c_tau_alloc = c_tau_alloc
        self.m_tau_o = m_tau_o
        self.a_tau = a_tau


def generate_tasks_model(tasks_specification: TasksSpecification, cpu_specification: CpuSpecification) -> TasksModel:
    n = len(tasks_specification.tasks)
    m = cpu_specification.number_of_cores

    # total of places of the TCPN ((p^w_i,p^cc_i) for each task)
    p = 2 * n

    # Total of transitions ((t^w_i and ti,jAlloc for each processor) for each task)
    t = n + n * m

    # n transitions of tasks period and n * m transitions alloc ((ti,jAlloc for each processor) for each task)
    t_alloc = n * m

    # Incidence Matrix C
    pre = scipy.zeros((p, t))
    post = scipy.zeros((p, t))
    pre_alloc = scipy.zeros((p, t_alloc))
    post_alloc = scipy.zeros((p, t_alloc))
    lambda_vector = scipy.zeros(t)
    pi = scipy.zeros((t, p))
    mo = scipy.zeros((p, 1))

    # Construction of Pre an Post matrix for places(p^w_i,p^cc_i) and transition(t^w_i)
    for k in range(n):
        i = 2 * k
        pre[i, k] = 1  # Transition from p^w_i to t^w_i
        post[i:i + 2, k] = [1, tasks_specification.tasks[k].c]  # Transition from t^w_i to p^w_i, from t^w_i to p^cc_i
        lambda_vector[k] = 1 / tasks_specification.tasks[k].t
        pi[k, i] = 1
        mo[i: i + 2, 0] = [1, tasks_specification.tasks[k].c]

        # Construction of Pre an Post matrix for Transitions alloc
        for r in range(m):
            j = n + r * n + k
            pre[i + 1, j] = 1
            pi[j, i + 1] = 1

    pre_alloc[:, 0: t_alloc] = pre[:, n: t]

    c = post - pre
    c_alloc = post_alloc - pre_alloc
    lambda_tau = scipy.diag(lambda_vector)

    return TasksModel(c, lambda_tau, pi, c_alloc, mo, (c.dot(lambda_tau)).dot(pi))
