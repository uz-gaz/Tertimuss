import scipy

from core.problem_specification_models.CpuSpecification import CpuSpecification
from core.problem_specification_models.TasksSpecification import TasksSpecification


class ProcessorModel(object):
    """
        Represents the task execution module in the paper
    """

    def __init__(self, tasks_specification: TasksSpecification, cpu_specification: CpuSpecification):
        n = len(tasks_specification.tasks)
        m = cpu_specification.number_of_cores

        # Transition rate (n)
        eta = 100

        # Total of places of the TCPN processor module
        p = m * (2 * n + 1)  # m processors*(n busy places, n exec places, 1 idle place)

        # Total of transitions
        t = m * (2 * n)  # m processors*(n transitions alloc and n tramsition exec)
        t_alloc = n * m  # m processors*(n transitions alloc)

        pre = scipy.zeros((p, t))
        post = scipy.zeros((p, t))
        pre_alloc = scipy.zeros((p, t_alloc))
        post_alloc = scipy.zeros((p, t_alloc))
        lambda_vector = scipy.zeros(t)
        lambda_alloc = scipy.zeros(t_alloc)
        pi = scipy.zeros((t, p))
        mo = scipy.zeros((p, 1))  # Different from np.zeros(p), column array
        s_exec = scipy.zeros((n * m, p))
        s_busy = scipy.zeros((n * m, p))

        # Incidence Matrix C construction
        # numeration of places and the corresponding label in the model for CPU_1:
        # busy places: p1-pn->p^busy_{1,1},..,p^busy_{n,1}
        # exec places: pn+1-p2n->p^exec_{1,1},...,p^exec_{n,1}
        # idle place:  p2n+1->p^idle_1

        for k in range(m):
            f = cpu_specification.clock_frequencies[k]

            i = (2 * n + 1) * k

            # Construction of matrix Post and Pre for busy and exec places (connections to transitions alloc and exec)
            pre[i:i + n, 2 * k * n + n: 2 * k * n + 2 * n] = scipy.identity(n)
            post[i:i + 2 * n, k * 2 * n:k * 2 * n + 2 * n] = scipy.identity(2 * n)

            # Construction of matrix Post and Pre for idle place (connections to transitions alloc and exec)
            pre[(k + 1) * (2 * n + 1) - 1, 2 * k * n: 2 * k * n + n] = eta * scipy.ones(n)
            post[(k + 1) * (2 * n + 1) - 1, 2 * k * n + n: 2 * (k + 1) * n] = eta * scipy.ones(n)

            # Construction of Pre an Post matrix for Transitions alloc
            pre_alloc[i:i + n, k * n: (k + 1) * n] = pre[i:i + n, 2 * k * n: 2 * k * n + n]
            post_alloc[i:i + n, k * n: k * n + n] = post[i:i + n, 2 * k * n: 2 * k * n + n]

            # Execution rates for transitions exec for CPU_k \lambda^exec= eta*F
            lambda_vector[2 * k * n + n:2 * k * n + 2 * n] = eta * f * scipy.ones(n)

            # Execution rates for transitions alloc \lambda^alloc= eta*\lambda^exec
            lambda_vector[2 * k * n:2 * k * n + n] = eta * lambda_vector[2 * k * n + n:2 * k * n + 2 * n]
            lambda_alloc[k * n:(k + 1) * n] = lambda_vector[2 * k * n:2 * k * n + n]

            # Configuration Matrix
            pi[2 * k * n + n:2 * k * n + 2 * n, i:i + n] = scipy.identity(n)

            # Initial condition
            mo[(k + 1) * (2 * n + 1) - 1, 0] = 1

            # Output matrix of the processor model, ( m^exec )
            s_busy[k * n:(k + 1) * n, i:(2 * n + 1) * k + n] = scipy.identity(n)
            s_exec[k * n:(k + 1) * n, (i + 1) + n - 1:(2 * n + 1) * k + 2 * n] = scipy.identity(n)

        c = post - pre
        c_alloc = post_alloc - pre_alloc
        lambda_proc = scipy.diag(lambda_vector)

        # TODO: Convert to SPARSE MATRIXES
        self.c_proc = c
        self.lambda_proc = lambda_proc
        self.pi_proc = pi
        self.c_proc_alloc = c_alloc
        self.s_exec = s_exec
        self.s_busy = s_busy
        self.m_proc_o = mo

    def change_frequency(self, tasks_specification: TasksSpecification, cpu_specification: CpuSpecification):
        # TODO: TEST
        n = len(tasks_specification.tasks)
        m = cpu_specification.number_of_cores

        # Transition rate
        eta = 100

        # Total of transitions
        t = m * (2 * n)  # m processors*(n transitions alloc and n tramsition exec)

        lambda_vector = scipy.zeros(t)

        for k in range(n):
            f = cpu_specification.clock_frequencies[k]

            # Execution rates for transitions exec for CPU_k \lambda^exec= eta*F
            lambda_vector[2 * k * n + n:2 * k * n + 2 * n] = eta * f * scipy.ones(n)

            # Execution rates for transitions alloc \lambda^alloc= eta*\lambda^exec
            lambda_vector[2 * k * n:2 * k * n + n] = eta * lambda_vector[2 * k * n + n:2 * k * n + 2 * n]

        lambda_proc = scipy.diag(lambda_vector)
        self.lambda_proc = lambda_proc
