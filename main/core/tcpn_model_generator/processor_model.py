import scipy

from main.core.problem_specification.cpu_specification.CpuSpecification import CpuSpecification
from main.core.problem_specification.tasks_specification.TasksSpecification import TasksSpecification


class ProcessorModel(object):
    """
        Represents the task execution module in the paper
    """

    def __init__(self, tasks_specification: TasksSpecification, cpu_specification: CpuSpecification):
        n = len(tasks_specification.periodic_tasks) + len(tasks_specification.aperiodic_tasks)
        m = cpu_specification.number_of_cores

        # Transition rate (n)
        eta = 1  # TODO: Revisar y comentar

        # Total of places of the TCPN processor module
        p = m * (2 * n + 1)  # m processors*(n busy places, n exec places, 1 idle place)

        # Total of transitions
        t_alloc = n * m  # m processors * (n transitions alloc)
        t_exec = n * m  # m processors * (n tramsition exec)

        # Model marking
        mo = scipy.zeros((p, 1))

        # Model for alloc transitions
        pre_alloc = scipy.zeros((p, t_alloc))
        post_alloc = scipy.zeros((p, t_alloc))
        pi_alloc = scipy.zeros((p, t_alloc))
        lambda_vector_alloc = scipy.zeros(t_alloc)

        # Model for exec transitions
        pre_exec = scipy.zeros((p, t_exec))
        post_exec = scipy.zeros((p, t_exec))
        pi_exec = scipy.zeros((p, t_exec))
        lambda_vector_exec = scipy.zeros(t_exec)

        # Construction of the model
        # numeration of places and the corresponding label in the model for CPU_1:
        # busy places: p1-pn->p^busy_{1,1},..,p^busy_{n,1}
        # exec places: pn+1-p2n->p^exec_{1,1},...,p^exec_{n,1}
        # idle place:  p2n+1->p^idle_1

        for k in range(m):
            # f = cpu_specification.clock_relative_frequencies[k]

            i = (2 * n + 1) * k

            # Construction of matrix Post and Pre for busy and exec places (connections to transitions alloc and exec)
            pre_exec[i:i + n, k * n: k * n + n] = scipy.identity(n)  # Arcs going from p_busy to t_exec

            post_alloc[i:i + n, k * n:k * n + n] = scipy.identity(n)  # Arcs going from t_alloc to p_busy
            post_exec[i + n:i + 2 * n, k * n:k * n + n] = scipy.identity(n)  # Arcs going from t_exec to p_exec

            pi_exec[i:i + n, k * n: k * n + n] = scipy.identity(n)

            # Construction of matrix Post and Pre for idle place (connections to transitions alloc and exec)
            pre_alloc[i + 2 * n, k * n: k * n + n] = eta * scipy.ones(n)
            post_exec[i + 2 * n, k * n: k * n + n] = eta * scipy.ones(n)

            pi_alloc[i + 2 * n, k * n: k * n + n] = (1 / eta) * scipy.ones(n)

            # Execution rates for transitions alloc \lambda^alloc= eta*\lambda^exec
            lambda_vector_alloc[k * n:k * n + n] = eta * scipy.ones(n)  # The F will be controlled online

            # Execution rates for transitions exec for CPU_k \lambda^exec= eta*F
            lambda_vector_exec[k * n:k * n + n] = eta * scipy.ones(n)  # The F will be controlled online

            # Initial condition
            mo[i + 2 * n, 0] = 1

        self.mo_proc = mo

        self.pre_alloc_proc = pre_alloc
        self.post_alloc_proc = post_alloc
        self.pi_alloc_proc = pi_alloc
        self.lambda_vector_alloc_proc = lambda_vector_alloc

        self.pre_exec_proc = pre_exec
        self.post_exec_proc = post_exec
        self.pi_exec_proc = pi_exec
        self.lambda_vector_exec_proc = lambda_vector_exec
