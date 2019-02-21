import numpy as np

from core.problem_specification_models.CpuSpecification import CpuSpecification
from core.problem_specification_models.TasksSpecification import TasksSpecification


class ProcessorModel(object):
    def __init__(self, c_proc, lambda_proc, pi_proc, c_proc_alloc, s_exec, s_busy, m_proc_o, a_proc):
        self.c_proc = c_proc
        self.lambda_proc = lambda_proc
        self.pi_proc = pi_proc
        self.c_proc_alloc = c_proc_alloc
        self.s_exec = s_exec
        self.s_busy = s_busy
        self.m_proc_o = m_proc_o
        self.a_proc = a_proc
        # TODO: Analyze if is necessary return Pre and Post matrix


def generate_processor_model(tasks_specification: TasksSpecification, cpu_specification: CpuSpecification) \
        -> ProcessorModel:
    f = 1  # TODO: Check if it's an error
    n = len(tasks_specification.tasks)
    m = cpu_specification.number_of_cores

    eta = 100

    # Total of places of the TCPN processor module
    p = m * (2 * n + 1)  # m processors*(n busy places, n exec places, 1 idle place)

    # Total of transitions
    t = m * (2 * n)  # m processors*(n transitions alloc and n tramsition exec)
    t_alloc = n * m  # m processors*(n transitions alloc)

    pre = np.zeros((p, t))
    post = np.zeros((p, t))
    pre_alloc = np.zeros((p, t_alloc))
    post_alloc = np.zeros((p, t_alloc))
    lambda_vector = np.zeros(t)
    lambda_alloc = np.zeros(t_alloc)
    pi = np.zeros((t, p))
    mo = np.zeros((p, 1))  # Different from np.zeros(p), column array
    s_exec = np.zeros((n * m, p))
    s_busy = np.zeros((n * m, p))

    # Incidence Matrix C construction
    # numeration of places and the corresponding label in the model for CPU_1:
    # busy places: p1-pn->p^busy_{1,1},..,p^busy_{n,1}
    # exec places: pn+1-p2n->p^exec_{1,1},...,p^exec_{n,1}
    # idle place:  p2n+1->p^idle_1

    for k in range(1, m):
        i = (2 * n + 1) * (k - 1) + 1

        # Construction of matrix Post and Pre for busy and exec places (connections to transitions alloc and exec)
        pre[i - 1:i + (n - 1), (k - 1) * (2 * n) + n: (k - 1) * (2 * n) + (2 * n)] = np.identity(n)
        post[i - 1:i + (2 * n - 1), (k - 1) * (2 * n):(k - 1) * (2 * n) + (2 * n)] = np.identity(2 * n)

        # Construction of matrix Post and Pre for idle place (connections to transitions alloc and exec)
        pre[k * (2 * n + 1) - 1, (k - 1) * (2 * n): (k - 1) * (2 * n) + n] = eta * np.ones(n)
        post[k * (2 * n + 1) - 1, (k - 1) * (2 * n) + n: (k - 1) * (2 * n) + (2 * n)] = eta * np.ones(n)

        # Construction of Pre an Post matrix for Transitions alloc
        pre_alloc[i - 1:i + (n - 1), (k - 1) * n: (k - 1) * n + n] = \
            pre[i - 1:i + (n - 1), (k - 1) * (2 * n): (k - 1) * (2 * n) + n]
        post_alloc[i - 1:i + (n - 1), (k - 1) * n: (k - 1) * n + n] = \
            post[i - 1:i + (n - 1), (k - 1) * (2 * n): (k - 1) * (2 * n) + n]

        # Execution rates for transitions exec for CPU_k \lambda^exec= eta*F
        lambda_vector[0, (k - 1) * (2 * n) + n:(k - 1) * (2 * n) + 2 * n] = eta * f * np.ones(n)

        # Execution rates for transitions alloc \lambda^alloc= eta*\lambda^exec
        lambda_vector[0, (k - 1) * (2 * n):(k - 1) * (2 * n) + n] = \
            eta * lambda_vector[0, (k - 1) * (2 * n) + n:(k - 1) * (2 * n) + 2 * n]
        lambda_alloc[0, (k - 1) * n:k * n] = lambda_vector[0, (k - 1) * (2 * n):(k - 1) * (2 * n) + n]

        # Configuration Matrix
        pi[(k - 1) * (2 * n) + n:(k - 1) * (2 * n) + 2 * n, i - 1:i + (n - 1)] = np.identity(n)

        # Initial condition
        mo[k * (2 * n + 1) - 1, 0] = 1

        # Output matrix of the processor model, ( m^exec )
        s_busy[(k - 1) * n:k * n, i - 1:(2 * n + 1) * (k - 1) + n] = np.identity(n)
        s_exec[(k - 1) * n:k * n, i + n - 1:(2 * n + 1) * (k - 1) + 2 * n] = np.identity(n)

    c = post - pre
    c_alloc = post_alloc - pre_alloc
    lambda_proc = np.diag(lambda_vector)

    return ProcessorModel(c, lambda_proc, pi, c_alloc, s_exec, s_busy, mo, (c.dot(lambda_proc)).dot(pi))
